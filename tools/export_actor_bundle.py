"""Export each named actor separately and retain explicit runtime routing metadata."""

import hashlib
from pathlib import Path

import yaml

from tools.export_policy import export_policy
from wheelleg.multi_actor import read_bundle


def export_bundle(checkpoint: Path, bundle_path: Path, rollout: Path, output: Path) -> dict:
    bundle = read_bundle(bundle_path, checkpoint)
    output.mkdir(parents=True, exist_ok=False)
    actors = {}
    for name, spec in bundle["actors"].items():
        result = export_policy(
            Path(spec["checkpoint"]),
            Path(spec["policy"]),
            Path(spec["robot"]),
            rollout,
            output / name,
            include_bundle=False,
        )
        actors[name] = dict(
            onnx=f"{name}/policy.onnx",
            checkpoint_sha256=spec["sha256"],
            onnx_sha256=hashlib.sha256((output / name / "policy.onnx").read_bytes()).hexdigest(),
            onnx_max_absolute_error=result["onnx_max_absolute_error"],
        )
    manifest = dict(
        version=1,
        mode_contract_revision=bundle["mode_contract_revision"],
        default_actor=bundle["default_actor"],
        trainable_actor=bundle["trainable_actor"],
        handoff=bundle["handoff"],
        actors=actors,
        routing="jump mode selects the jump specialist; other phases select the frozen base",
        previous_action="actual raw action from the previously selected actor",
    )
    (output / "deployment_bundle.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return manifest
