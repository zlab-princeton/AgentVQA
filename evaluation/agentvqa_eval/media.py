import hashlib
import io
import math
import re
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np
from huggingface_hub import hf_hub_download
from PIL import Image

from .catalog import REPOSITORY


def digest_file(path):
    result = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def resolve_video(value):
    path = value.get("path") if isinstance(value, dict) else value
    pattern = rf"hf://datasets/{re.escape(REPOSITORY)}@([a-f0-9]{{40}})/(media/.+\.mp4)"
    match = re.fullmatch(pattern, path or "")
    if not match:
        raise ValueError(
            "Video must be a revision-pinned media URI in the public AgentVQA repository"
        )
    revision, filename = match.groups()
    if ".." in Path(filename).parts:
        raise ValueError("Invalid Hub media path")
    local = hf_hub_download(REPOSITORY, filename, repo_type="dataset", revision=revision)
    expected = Path(filename).stem
    actual = digest_file(local)
    if re.fullmatch(r"[a-f0-9]{64}", expected) and actual != expected:
        raise ValueError("Video SHA256 differs from its content-addressed filename")
    return Path(local), {"uri": path, "sha256": actual, "bytes": Path(local).stat().st_size}


def decode_image(value):
    if isinstance(value, Image.Image):
        return value.convert("RGB")
    if not isinstance(value, dict) or not value.get("bytes"):
        raise ValueError("Images must be embedded in the Hugging Face dataset")
    with Image.open(io.BytesIO(value["bytes"])) as image:
        return image.convert("RGB")


def sample_frames(path, count):
    if count < 1:
        raise ValueError("Frame count must be positive")
    capture = cv2.VideoCapture(str(path))
    try:
        if not capture.isOpened():
            raise ValueError("Cannot open video")
        total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = float(capture.get(cv2.CAP_PROP_FPS))
        if total < 1 or not np.isfinite(fps) or fps <= 0:
            raise ValueError("Invalid video frame count or frame rate")
        indices = np.linspace(0, total - 1, min(total, count), dtype=int).tolist()
        frames = []
        for index in indices:
            capture.set(cv2.CAP_PROP_POS_FRAMES, index)
            success, frame = capture.read()
            if not success:
                raise ValueError(f"Cannot decode requested video frame {index}")
            frames.append(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
        return frames, {
            "indices": indices,
            "timestamps": [i / fps for i in indices],
            "fps": fps,
            "total_frames": total,
        }
    finally:
        capture.release()


def stitch(images):
    merged, groups = [], []
    for start in range(0, len(images), 4):
        group = images[start : start + 4]
        width = max(image.width for image in group)
        height = max(image.height for image in group)
        columns = min(2, len(group))
        rows = (len(group) + 1) // 2
        canvas = Image.new("RGB", (columns * width, rows * height), "white")
        panels = []
        for index, image in enumerate(group):
            x, y = (index % 2) * width, (index // 2) * height
            canvas.paste(image, (x, y))
            panels.append({"source_index": start + index, "offset": [x, y], "size": image.size})
        merged.append(canvas)
        groups.append(panels)
    return merged, groups


def smart_size(size, factor, max_pixels):
    width, height = size
    if max(size) / min(size) > 200:
        raise ValueError("Qwen image aspect ratio exceeds 200:1")
    minimum = 4 * factor * factor
    rounded = [max(factor, round(value / factor) * factor) for value in size]
    if math.prod(rounded) > max_pixels:
        scale = math.sqrt(width * height / max_pixels)
        rounded = [max(factor, math.floor(value / scale / factor) * factor) for value in size]
    elif math.prod(rounded) < minimum:
        scale = math.sqrt(minimum / (width * height))
        rounded = [math.ceil(value * scale / factor) * factor for value in size]
    if not minimum <= math.prod(rounded) <= max_pixels:
        raise ValueError("Image cannot satisfy the configured Qwen pixel budget")
    return tuple(rounded)


def encode_image(image, max_side, quality, grid_factor=1, max_pixels=None):
    image = image.convert("RGB")
    if max_side and max(image.size) > max_side:
        scale = max_side / max(image.size)
        image = image.resize(
            (max(1, round(image.width * scale)), max(1, round(image.height * scale))),
            Image.Resampling.LANCZOS,
        )
    if grid_factor > 1:
        size = smart_size(image.size, grid_factor, max_pixels)
        if image.size != size:
            image = image.resize(size, Image.Resampling.LANCZOS)
    output = io.BytesIO()
    image.save(output, format="JPEG", quality=quality)
    return output.getvalue(), image.size


@dataclass
class Media:
    images: list[Image.Image] = field(default_factory=list)
    video: Path | None = None
    mode: str = "images"
    audit: dict = field(default_factory=dict)

    def encoded(self, max_side, quality, grid_factor=1, max_pixels=None):
        values = [
            encode_image(image, max_side, quality, grid_factor, max_pixels) for image in self.images
        ]
        return [v[0] for v in values], [v[1] for v in values]

    def note(self):
        layout = (
            " Consecutive images are packed in groups of at most four, in a 2×2 grid read left-to-right, then top-to-bottom. Any unused area is blank padding."
            if self.audit.get("panels")
            else ""
        )
        if self.mode == "frames":
            times = ", ".join(f"{x:.2f}s" for x in self.audit["frames"]["timestamps"])
            return (
                f"The images are video frames in chronological order, sampled at: {times}." + layout
            )
        if self.mode == "native":
            return "The supplied media is the complete video."
        return "Images are supplied in dataset order." + layout

    def use_frames(self, count, image_limit):
        self.images, self.audit["frames"] = sample_frames(self.video, count)
        self.mode = "frames"
        self.audit["original_sizes"] = [image.size for image in self.images]
        self.pack(image_limit, always=False)

    def pack(self, image_limit, always):
        if len(self.images) > 1 and (always or len(self.images) > image_limit):
            self.images, self.audit["panels"] = stitch(self.images)
        if len(self.images) > image_limit:
            raise ValueError(
                f"Four-per-image packing still exceeds the {image_limit}-image cap; raise --image-limit or reduce --num-frames explicitly"
            )


def prepare_media(doc, config):
    if doc.get("Video") is not None:
        path, audit = resolve_video(doc["Video"])
        result = Media(video=path, audit={"source": audit})
        native_capable = bool(config.native_supported)
        native_size_ok = path.stat().st_size <= config.native_max_mb * 1_000_000
        if config.video_mode == "native":
            if not native_capable:
                raise ValueError(
                    f"Native video is not configured for {config.provider}; use frames"
                )
            if (
                config.provider not in ("gemini", "moonshot", "dashscope", "zai")
                and not native_size_ok
            ):
                raise ValueError("Native video exceeds --native-max-mb; use auto or frames")
            result.mode = "native"
        elif (
            config.video_mode == "auto"
            and native_capable
            and (native_size_ok or config.provider in ("gemini", "moonshot", "dashscope", "zai"))
        ):
            result.mode = "native"
        else:
            result.use_frames(config.num_frames, config.image_limit)
        return result
    raw = [doc["Image"]] if doc.get("Image") is not None else doc.get("Images", [])
    images = [decode_image(value) for value in raw]
    if not images:
        raise ValueError("Sample has no visual input")
    audit = {
        "original_sizes": [image.size for image in images],
        "source_sha256": [
            hashlib.sha256(value["bytes"]).hexdigest()
            if isinstance(value, dict)
            else hashlib.sha256(image.tobytes()).hexdigest()
            for value, image in zip(raw, images)
        ],
    }
    result = Media(images=images, audit=audit)
    result.pack(config.image_limit, always=True)
    return result
