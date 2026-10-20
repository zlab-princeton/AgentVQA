import cv2
import numpy as np
import pytest
from PIL import Image

from agentvqa_eval.media import (
    Media,
    decode_image,
    resolve_video,
    sample_frames,
    smart_size,
    stitch,
)
from agentvqa_eval.prompts import build_prompt, convert_points, coordinate_format


@pytest.mark.parametrize(
    "model,expected",
    [
        ("gemini-3.1-pro-preview", "1000-yx"),
        ("Qwen/Qwen2.5-VL-72B-Instruct", "pixel-xy"),
        ("qwen/qwen3.5-27b", "1000-xy"),
        ("gpt-5.6-sol", "unit-xy"),
    ],
)
def test_coordinate_profiles(model, expected):
    assert coordinate_format(model) == expected


def test_dashscope_coordinate_convention_is_endpoint_specific():
    assert coordinate_format("qwen3.5-27b", provider="dashscope") == "999-xy"
    assert coordinate_format("qwen/qwen3.5-27b", provider="openrouter") == "1000-xy"
    assert coordinate_format("qwen3.5-27b", "1000-xy", "dashscope") == "1000-xy"
    assert coordinate_format("Qwen/Qwen2-VL-7B-Instruct") == "1000-xy"


@pytest.mark.parametrize("size", [(1920, 1080), (2560, 1440), (17, 12), (400, 800)])
def test_qwen_pixel_grid_is_bounded_and_stable(size):
    result = smart_size(size, 28, 1003520)
    assert all(v > 0 and v % 28 == 0 for v in result)
    assert 3136 <= result[0] * result[1] <= 1003520
    assert smart_size(result, 28, 1003520) == result


def test_ambiguous_multiframe_coordinates_fail_closed():
    doc = {"Question": "Where?", "Options": ["[1, 2]", "[3, 4]"]}
    with pytest.raises(ValueError, match="one unambiguous source image"):
        build_prompt(doc, "ERQA", "pixel-xy", [(100, 100)] * 4, [(200, 200)])


@pytest.mark.parametrize(
    "mode,expected",
    [
        ("pixel-xy", "[25, 75]"),
        ("unit-xy", "[0.250, 0.375]"),
        ("1000-xy", "[250, 375]"),
        ("1000-yx", "[375, 250]"),
        ("999-yx", "[375, 250]"),
    ],
)
def test_coordinate_geometry(mode, expected):
    actual, warnings = convert_points("Tap: [50, 150]", (200, 400), (100, 200), mode)
    assert actual == "Tap: " + expected
    assert not warnings


def test_out_of_bounds_distractor_not_clipped():
    converted, warnings = convert_points("[2982, 242]", (2560, 1440), (2560, 1440), "1000-yx")
    assert converted == "[168, 1165]"
    assert warnings


def test_prompt_preserves_grid_and_all_options_and_excludes_answer():
    doc = {
        "Question": "Which grid cell?",
        "Options": [f"({i}, 2)" for i in range(8)],
        "Answer": "SECRET_TARGET",
        "Action History": "Walked left",
        "Episode Goal": "Find door",
    }
    prompt, options, _ = build_prompt(doc, "GameQA", "1000-yx", [(10, 10)], [(10, 10)], True)
    assert "H. (7, 2)" in prompt
    assert options == doc["Options"]
    assert "SECRET_TARGET" not in prompt
    assert "Action History" in prompt and "Episode Goal" in prompt
    assert "brief explanation" in prompt


def test_four_image_grid_preserves_pixels_and_order():
    images = [
        Image.new("RGB", (20, 10), color) for color in ("red", "green", "blue", "yellow", "black")
    ]
    packed, panels = stitch(images)
    assert len(packed) == 2
    assert packed[0].size == (40, 20)
    assert [packed[0].getpixel(point) for point in ((0, 0), (20, 0), (0, 10), (20, 10))] == [
        im.getpixel((0, 0)) for im in images[:4]
    ]
    assert [[p["source_index"] for p in group] for group in panels] == [[0, 1, 2, 3], [4]]


def test_32_frames_fit_ten_image_endpoint_without_discarding():
    frames = [Image.new("RGB", (12, 8), (i, 0, 0)) for i in range(32)]
    media = Media(images=frames)
    media.pack(10, always=False)
    assert len(media.images) == 8
    assert sum(len(g) for g in media.audit["panels"]) == 32


def test_sampling_equal_intervals_including_endpoints(tmp_path):
    path = tmp_path / "video.avi"
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 10, (32, 24))
    assert writer.isOpened()
    for i in range(65):
        writer.write(np.full((24, 32, 3), i * 3, dtype=np.uint8))
    writer.release()
    frames, audit = sample_frames(path, 32)
    assert len(frames) == 32
    assert audit["indices"] == np.linspace(0, 64, 32, dtype=int).tolist()
    assert audit["indices"][0] == 0 and audit["indices"][-1] == 64
    assert max(np.diff(audit["indices"])) - min(np.diff(audit["indices"])) <= 1


def test_reject_local_media_paths():
    with pytest.raises(ValueError):
        resolve_video({"path": "/data/old.mp4"})
    with pytest.raises(ValueError):
        decode_image({"path": "/data/image.jpg"})
