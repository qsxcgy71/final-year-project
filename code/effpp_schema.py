"""Utility helpers for validating EFF++ frame annotations."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Sequence

REQUIRED_FIELDS = [
    "q",
    "manipulated",
    "a",
    "cfad_rationale",
    "evidence_tags",
    "technique_summary",
    "pair",
]


def load_tags(path: Path) -> List[str]:
    with path.open("r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    return [item["id"] for item in data]


def validate_annotation(annotation: Dict[str, object], tag_ids: Sequence[str]) -> List[str]:
    errors: List[str] = []
    tag_set = set(tag_ids)
    for field in REQUIRED_FIELDS:
        if field not in annotation:
            errors.append(f"missing field: {field}")
    if annotation.get("q") != "Is this image manipulated?":
        errors.append("q must be the canonical question")
    answer = str(annotation.get("a", "")).strip()
    if not answer:
        errors.append("answer a is empty")
    if answer and not (answer.startswith("Yes") or answer.startswith("No")):
        errors.append("answer must start with Yes/No")
    rationale = str(annotation.get("cfad_rationale", "")).strip()
    if not rationale:
        errors.append("cfad_rationale is empty")
    tags = annotation.get("evidence_tags", [])
    if not isinstance(tags, list) or not tags:
        errors.append("evidence_tags must be a non-empty list")
    else:
        invalid = [tag for tag in tags if tag not in tag_set]
        if invalid:
            errors.append(f"invalid evidence tags: {invalid}")
        if len(tags) < 2:
            errors.append("evidence_tags must contain at least two items")
    pair = annotation.get("pair")
    if not isinstance(pair, dict):
        errors.append("pair must be a dict")
    else:
        for key in ["identity", "frame_rank", "frame_index", "method", "split", "video_id", "real_frame_path", "target_frame_path"]:
            if key not in pair:
                errors.append(f"pair missing field: {key}")
    return errors

