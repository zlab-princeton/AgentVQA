import hashlib
import importlib.metadata
import json
import os
import platform
import tempfile
from pathlib import Path

from . import __version__
from .catalog import LMMS_REVISION, REPOSITORY


def fingerprint(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".writing-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def provenance(config, revision, subsets, limit, offset, dry_run, capabilities, validations):
    root = Path(__file__).parent
    source = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.glob("*.py"))}
    dependencies = {
        d.metadata["Name"]: d.version
        for d in importlib.metadata.distributions()
        if d.metadata.get("Name")
    }
    return {
        "schema_version": 1,
        "package_version": __version__,
        "source_sha256": source,
        "lmms_eval_revision": LMMS_REVISION,
        "python": platform.python_version(),
        "dependencies": dependencies,
        "dataset": {
            "repository": REPOSITORY,
            "revision": revision,
            "split": "train",
            "subsets": subsets,
            "validation": validations,
        },
        "config": config,
        "selection": {"limit_per_subset": limit, "offset_per_subset": offset},
        "dry_run": dry_run,
        "capabilities": capabilities,
        "ground_truth_sent_to_model": False,
    }


class Store:
    def __init__(self, root, manifest, resume=False):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.manifest = manifest
        self.run_id = fingerprint(manifest)
        path = self.root / "manifest.json"
        if path.exists():
            if not resume:
                raise ValueError(
                    "Output already contains a run; use --resume or a new output directory"
                )
            if json.loads(path.read_text()) != manifest:
                raise ValueError(
                    "Resume refused: code, dependencies, dataset, model, or run settings changed"
                )
        elif resume:
            raise ValueError("Cannot resume: manifest.json is absent")
        else:
            if any(p.name != ".lock" for p in self.root.iterdir()):
                raise ValueError("New output directory must be empty")
            atomic_json(path, manifest)

    def path(self, subset, index):
        return self.root / "samples" / subset / f"{index:05d}.json"

    def read(self, subset, index):
        path = self.path(subset, index)
        if not path.exists():
            return None
        record = json.loads(path.read_text())
        if (
            record.get("run_id") != self.run_id
            or record.get("subset") != subset
            or record.get("row_index") != index
        ):
            raise ValueError("Checkpoint identity mismatch")
        return record

    def write(self, record):
        record["run_id"] = self.run_id
        atomic_json(self.path(record["subset"], record["row_index"]), record)
