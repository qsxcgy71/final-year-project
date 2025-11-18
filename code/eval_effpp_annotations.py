"""
Evaluate textual quality of EFF++ frame annotations.

Metrics:
- Yes/No 前缀一致性
- 词数（默认 ≤60）
- 标签数量与合法性
- `manipulated` 字段与回答前缀一致性

Outputs JSON (and可选 Markdown) 汇总。
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

from effpp_dataset import EffppFrameDataset, summarize_dataset
from effpp_schema import load_tags


def _word_count(text: str) -> int:
    return len(text.replace("\n", " ").split())


def evaluate_annotations(
    dataset: EffppFrameDataset,
    tag_ids: List[str],
    word_limit: int = 60,
) -> Dict[str, object]:
    tag_set = set(tag_ids)
    overall_counters = defaultdict(int)
    method_counters: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    word_counts: List[int] = []

    for sample in dataset.samples:
        method = sample.method
        ann = sample.annotation
        answer = str(ann.get("a", "")).strip()
        manipulated = bool(ann.get("manipulated", False))
        tags = ann.get("evidence_tags", [])

        overall_counters["total"] += 1
        method_counters[method]["total"] += 1

        # Yes/No prefix
        answer_lower = answer.lower()
        yes_no_ok = answer_lower.startswith("yes") or answer_lower.startswith("no")
        if yes_no_ok:
            overall_counters["yes_no_ok"] += 1
            method_counters[method]["yes_no_ok"] += 1
        else:
            overall_counters["yes_no_fail"] += 1
            method_counters[method]["yes_no_fail"] += 1

        # Consistency with manipulated flag
        if yes_no_ok:
            is_yes = answer_lower.startswith("yes")
            manipulated_consistent = (is_yes and manipulated) or (not is_yes and not manipulated)
        else:
            manipulated_consistent = False
        if manipulated_consistent:
            overall_counters["manipulated_consistent"] += 1
            method_counters[method]["manipulated_consistent"] += 1
        else:
            overall_counters["manipulated_inconsistent"] += 1
            method_counters[method]["manipulated_inconsistent"] += 1

        # Word count
        wc = _word_count(answer)
        word_counts.append(wc)
        if wc <= word_limit:
            overall_counters["word_limit_ok"] += 1
            method_counters[method]["word_limit_ok"] += 1
        else:
            overall_counters["word_limit_fail"] += 1
            method_counters[method]["word_limit_fail"] += 1

        # Tag checks
        if isinstance(tags, list):
            tag_count = len(tags)
            if 2 <= tag_count <= 4:
                overall_counters["tag_count_ok"] += 1
                method_counters[method]["tag_count_ok"] += 1
            else:
                overall_counters["tag_count_fail"] += 1
                method_counters[method]["tag_count_fail"] += 1

            invalid = [t for t in tags if t not in tag_set]
            if not invalid:
                overall_counters["tag_vocab_ok"] += 1
                method_counters[method]["tag_vocab_ok"] += 1
            else:
                overall_counters["tag_vocab_fail"] += 1
                method_counters[method]["tag_vocab_fail"] += 1
        else:
            overall_counters["tag_count_fail"] += 1
            method_counters[method]["tag_count_fail"] += 1
            overall_counters["tag_vocab_fail"] += 1
            method_counters[method]["tag_vocab_fail"] += 1

    average_wc = sum(word_counts) / len(word_counts) if word_counts else 0.0
    summary = summarize_dataset(dataset)
    return {
        "summary": summary,
        "word_limit": word_limit,
        "average_word_count": round(average_wc, 2),
        "overall": dict(overall_counters),
        "per_method": {method: dict(counts) for method, counts in method_counters.items()},
    }


def write_markdown(report: Dict[str, object], output_path: Path) -> None:
    lines = []
    summary = report["summary"]
    lines.append(f"# EFF++ Annotation Metrics ({summary['split']})")
    lines.append("")
    lines.append(f"- 样本数: {summary['num_samples']}")
    lines.append(f"- 身份数: {summary['num_identities']}")
    lines.append("- 每方法计数:")
    for key, value in summary["counts_by_split_method"].items():
        lines.append(f"  - {key}: {value}")
    lines.append("")
    lines.append("## 关键指标")
    overall = report["overall"]
    lines.append(f"- Yes/No 前缀一致: {overall.get('yes_no_ok', 0)}/{overall.get('total', 0)}")
    lines.append(f"- 与 `manipulated` 一致: {overall.get('manipulated_consistent', 0)}/{overall.get('total', 0)}")
    lines.append(f"- <= {report['word_limit']} 词: {overall.get('word_limit_ok', 0)}/{overall.get('total', 0)}")
    lines.append(f"- 标签数量合法: {overall.get('tag_count_ok', 0)}/{overall.get('total', 0)}")
    lines.append(f"- 标签在枚举内: {overall.get('tag_vocab_ok', 0)}/{overall.get('total', 0)}")
    lines.append(f"- 平均词数: {report['average_word_count']}")
    lines.append("")
    lines.append("## 分方法统计")
    lines.append("| Method | Samples | Yes/No OK | Manip OK | Word OK | Tag Count OK | Tag Vocab OK |")
    lines.append("|--------|---------|-----------|----------|---------|---------------|--------------|")
    for method, counts in sorted(report["per_method"].items()):
        total = counts.get("total", 0)
        yes_no_ok = counts.get("yes_no_ok", 0)
        manip_ok = counts.get("manipulated_consistent", 0)
        word_ok = counts.get("word_limit_ok", 0)
        tag_count_ok = counts.get("tag_count_ok", 0)
        tag_vocab_ok = counts.get("tag_vocab_ok", 0)
        lines.append(
            f"| {method} | {total} | {yes_no_ok} | {manip_ok} | {word_ok} | {tag_count_ok} | {tag_vocab_ok} |"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate EFF++ annotation textual quality.")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--split", choices=["train", "val", "test"], default="train")
    parser.add_argument("--word-limit", type=int, default=60)
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument("--markdown-out", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true", help="Write results to default reports directory.")
    args = parser.parse_args()

    dataset = EffppFrameDataset(project_root=args.project_root, split=args.split)
    tag_file = args.project_root / "config" / "effpp_tags.json"
    tag_ids = load_tags(tag_file)
    report = evaluate_annotations(dataset, tag_ids, word_limit=args.word_limit)

    json_out = args.json_out
    markdown_out = args.markdown_out
    if args.overwrite:
        reports_dir = args.project_root / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        json_out = reports_dir / f"effpp_annotation_metrics_{args.split}.json"
        markdown_out = reports_dir / f"effpp_annotation_metrics_{args.split}.md"

    if json_out:
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))

    if markdown_out:
        write_markdown(report, markdown_out)


if __name__ == "__main__":
    main()
