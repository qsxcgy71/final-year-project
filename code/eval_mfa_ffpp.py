from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
from scipy.stats import kendalltau, pointbiserialr, spearmanr
from sklearn.metrics import average_precision_score, f1_score, roc_auc_score

TOP_K = 5


@dataclass
class QuestionMeta:
    question_en: str
    question_zh: str
    category: str


@dataclass
class QuestionStats:
    yes: int
    total: int

    @property
    def score(self) -> float:
        return self.yes / self.total if self.total else 0.0

    @property
    def prediction(self) -> bool:
        return self.yes >= self.total / 2 if self.total else False


@dataclass
class VideoRecord:
    key: str
    split: str
    label: int
    method: str
    question_stats: Dict[str, QuestionStats]


def load_question_meta(root: Path) -> Dict[str, QuestionMeta]:
    config_path = root / "config" / "mfa_questions.json"
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return {
        item["id"]: QuestionMeta(
            question_en=item.get("question_en", ""),
            question_zh=item.get("question_zh", ""),
            category=item.get("category", "")
        )
        for item in data
    }


def load_progress(path: Path, split: str) -> List[VideoRecord]:
    records: List[VideoRecord] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            if data.get("split") != split:
                continue
            questions = {
                qid: QuestionStats(yes=stats.get("yes", 0), total=stats.get("total", 0))
                for qid, stats in data.get("questions", {}).items()
            }
            records.append(
                VideoRecord(
                    key=data.get("video_key", data.get("video_id", "")),
                    split=data.get("split", split),
                    label=int(data.get("label", 0)),
                    method=data.get("method", ""),
                    question_stats=questions,
                )
            )
    return records


def collect_scores(records: Iterable[VideoRecord], question_id: str) -> Tuple[List[float], List[int], int, int, int, int]:
    scores: List[float] = []
    labels: List[int] = []
    tp = tn = fp = fn = 0
    for record in records:
        stats = record.question_stats.get(question_id)
        if not stats:
            continue
        score = stats.score
        pred = stats.prediction
        label = int(record.label)
        scores.append(score)
        labels.append(label)
        if label == 1 and pred:
            tp += 1
        elif label == 1 and not pred:
            fn += 1
        elif label == 0 and pred:
            fp += 1
        else:
            tn += 1
    return scores, labels, tp, tn, fp, fn


def balanced_accuracy(tp: int, tn: int, fp: int, fn: int) -> float:
    tpr = tp / (tp + fn) if (tp + fn) else 0.0
    tnr = tn / (tn + fp) if (tn + fp) else 0.0
    return 0.5 * (tpr + tnr)


def balanced_accuracy_ci(tp: int, tn: int, fp: int, fn: int) -> Tuple[float, float]:
    if tp + fn == 0 or tn + fp == 0:
        ba = balanced_accuracy(tp, tn, fp, fn)
        return ba, ba
    tpr = tp / (tp + fn)
    tnr = tn / (tn + fp)
    var_tpr = tpr * (1 - tpr) / (tp + fn)
    var_tnr = tnr * (1 - tnr) / (tn + fp)
    se = np.sqrt((var_tpr + var_tnr) / 4)
    ba = balanced_accuracy(tp, tn, fp, fn)
    z = 1.96
    return max(0.0, ba - z * se), min(1.0, ba + z * se)


def safe_auc(labels: List[int], scores: List[float]) -> Optional[float]:
    try:
        if len(set(labels)) < 2:
            return None
        return float(roc_auc_score(labels, scores))
    except ValueError:
        return None


def safe_ap(labels: List[int], scores: List[float]) -> Optional[float]:
    try:
        if len(set(labels)) < 2:
            return None
        return float(average_precision_score(labels, scores))
    except ValueError:
        return None


def safe_pointbiserial(labels: List[int], scores: List[float]) -> Optional[float]:
    if len(set(labels)) < 2:
        return None
    try:
        corr, _ = pointbiserialr(labels, scores)
        return float(corr)
    except Exception:
        return None


def compute_question_table(
    val_records: List[VideoRecord],
    test_records: List[VideoRecord],
    meta: Dict[str, QuestionMeta],
) -> Tuple[List[Dict[str, object]], Dict[str, float], Dict[str, float]]:
    question_ids = sorted(
        {qid for record in val_records + test_records for qid in record.question_stats}
    )
    table: List[Dict[str, object]] = []
    val_map: Dict[str, float] = {}
    test_map: Dict[str, float] = {}

    for qid in question_ids:
        info = meta.get(qid, QuestionMeta(qid, qid, ""))
        row: Dict[str, object] = {
            "id": qid,
            "category": info.category,
            "question_en": info.question_en,
            "question_zh": info.question_zh,
        }
        val_scores, val_labels, val_tp, val_tn, val_fp, val_fn = collect_scores(val_records, qid)
        test_scores, test_labels, test_tp, test_tn, test_fp, test_fn = collect_scores(test_records, qid)

        val_ba = balanced_accuracy(val_tp, val_tn, val_fp, val_fn)
        test_ba = balanced_accuracy(test_tp, test_tn, test_fp, test_fn)
        avg_ba = (val_ba + test_ba) / 2

        row["val"] = {
            "balanced_accuracy": val_ba,
            "auc": safe_auc(val_labels, val_scores),
            "average_precision": safe_ap(val_labels, val_scores),
            "r_pb": safe_pointbiserial(val_labels, val_scores),
            "ci95": balanced_accuracy_ci(val_tp, val_tn, val_fp, val_fn),
            "tp": val_tp,
            "tn": val_tn,
            "fp": val_fp,
            "fn": val_fn,
        }
        row["test"] = {
            "balanced_accuracy": test_ba,
            "auc": safe_auc(test_labels, test_scores),
            "average_precision": safe_ap(test_labels, test_scores),
            "r_pb": safe_pointbiserial(test_labels, test_scores),
            "ci95": balanced_accuracy_ci(test_tp, test_tn, test_fp, test_fn),
            "tp": test_tp,
            "tn": test_tn,
            "fp": test_fp,
            "fn": test_fn,
        }
        row["avg_balanced_accuracy"] = avg_ba
        table.append(row)
        val_map[qid] = val_ba
        test_map[qid] = test_ba

    table.sort(key=lambda x: x["avg_balanced_accuracy"], reverse=True)
    for idx, row in enumerate(table, start=1):
        row["rank"] = idx

    return table, val_map, test_map


def build_score_arrays(records: List[VideoRecord], top_ids: List[str]) -> Dict[str, Dict[str, List[float]]]:
    aggregations = {name: {"scores": [], "labels": []} for name in ("mean", "max", "topk")}
    for record in records:
        scores = [record.question_stats[qid].score for qid in top_ids if qid in record.question_stats]
        if not scores:
            continue
        mean_score = float(np.mean(scores))
        max_score = float(np.max(scores))
        topk_score = float(np.mean(sorted(scores, reverse=True)[: min(TOP_K, len(scores))]))
        for name, value in (("mean", mean_score), ("max", max_score), ("topk", topk_score)):
            aggregations[name]["scores"].append(value)
            aggregations[name]["labels"].append(int(record.label))
    return aggregations


def find_best_threshold(scores: List[float], labels: List[int]) -> Tuple[float, Dict[str, float]]:
    unique = sorted(set(scores))
    best_thr = 0.5
    best_f1 = -1.0
    best_stats: Dict[str, float] = {}
    for thr in unique:
        preds = [1 if s >= thr else 0 for s in scores]
        f1 = f1_score(labels, preds, zero_division=0)
        if f1 > best_f1:
            best_f1 = f1
            tp = sum(1 for p, y in zip(preds, labels) if p == 1 and y == 1)
            fp = sum(1 for p, y in zip(preds, labels) if p == 1 and y == 0)
            tn = sum(1 for p, y in zip(preds, labels) if p == 0 and y == 0)
            fn = sum(1 for p, y in zip(preds, labels) if p == 0 and y == 1)
            precision = tp / (tp + fp) if (tp + fp) else 0.0
            recall = tp / (tp + fn) if (tp + fn) else 0.0
            best_stats = {
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "balanced_accuracy": balanced_accuracy(tp, tn, fp, fn),
                "tp": tp,
                "tn": tn,
                "fp": fp,
                "fn": fn,
            }
            best_thr = thr
    return best_thr, best_stats


def compute_pooling_metrics(val_records: List[VideoRecord], test_records: List[VideoRecord], top_ids: List[str]) -> Dict[str, object]:
    result: Dict[str, object] = {"top_question_ids": top_ids}
    val_aggs = build_score_arrays(val_records, top_ids)
    test_aggs = build_score_arrays(test_records, top_ids)

    for name in ("mean", "max", "topk"):
        val_scores = val_aggs[name]["scores"]
        val_labels = val_aggs[name]["labels"]
        test_scores = test_aggs[name]["scores"]
        test_labels = test_aggs[name]["labels"]

        thr, val_metrics = find_best_threshold(val_scores, val_labels)

        try:
            roc_auc = float(roc_auc_score(test_labels, test_scores))
        except ValueError:
            roc_auc = None
        try:
            ap = float(average_precision_score(test_labels, test_scores))
        except ValueError:
            ap = None

        preds = [1 if s >= thr else 0 for s in test_scores]
        tp = sum(1 for p, y in zip(preds, test_labels) if p == 1 and y == 1)
        fp = sum(1 for p, y in zip(preds, test_labels) if p == 1 and y == 0)
        tn = sum(1 for p, y in zip(preds, test_labels) if p == 0 and y == 0)
        fn = sum(1 for p, y in zip(preds, test_labels) if p == 0 and y == 1)

        result[name] = {
            "threshold": thr,
            "val": val_metrics,
            "test": {
                "roc_auc": roc_auc,
                "average_precision": ap,
                "f1": f1_score(test_labels, preds, zero_division=0),
                "precision": tp / (tp + fp) if (tp + fp) else 0.0,
                "recall": tp / (tp + fn) if (tp + fn) else 0.0,
                "balanced_accuracy": balanced_accuracy(tp, tn, fp, fn),
                "tp": tp,
                "tn": tn,
                "fp": fp,
                "fn": fn,
            },
        }

    return result


def compute_frame_metrics(records: List[VideoRecord], question_id: str) -> Dict[str, float]:
    tp = tn = fp = fn = 0
    for record in records:
        stats = record.question_stats.get(question_id)
        if not stats:
            continue
        yes = stats.yes
        no = stats.total - stats.yes
        if record.label == 1:
            tp += yes
            fn += no
        else:
            fp += yes
            tn += no
    total_pos = tp + fn
    total_neg = tn + fp
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / total_pos if total_pos else 0.0
    ba = balanced_accuracy(tp, tn, fp, fn)
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return {
        "question_id": question_id,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "balanced_accuracy": ba,
        "note": "Binary frame-level approximation based on top-ranked question votes.",
    }


def load_summary(path: Path) -> Dict[str, float]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    durations = [item.get("duration_sec", 0.0) for item in data if item.get("status") == "ok"]
    if not durations:
        return {}
    return {
        "count": len(durations),
        "total_seconds": float(sum(durations)),
        "avg_seconds": float(np.mean(durations)),
        "median_seconds": float(np.median(durations)),
    }


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    meta = load_question_meta(project_root)

    val_records = load_progress(project_root / "mfa" / "ffpp_c23" / "mfa_ffpp_val_progress.jsonl", "val")
    test_records = load_progress(project_root / "mfa" / "ffpp_c23" / "mfa_ffpp_test_progress.jsonl", "test")

    question_table, val_rank_map, test_rank_map = compute_question_table(val_records, test_records, meta)

    val_scores = [val_rank_map[q["id"]] for q in question_table]
    test_scores = [test_rank_map[q["id"]] for q in question_table]
    spearman = spearmanr(val_scores, test_scores).correlation if len(question_table) > 1 else None
    kendall = kendalltau(val_scores, test_scores).correlation if len(question_table) > 1 else None

    top_ids = [row["id"] for row in question_table[:TOP_K]]
    pooling_metrics = compute_pooling_metrics(val_records, test_records, top_ids)

    top_question_id = question_table[0]["id"] if question_table else None
    frame_metrics = {
        "val": compute_frame_metrics(val_records, top_question_id) if top_question_id else {},
        "test": compute_frame_metrics(test_records, top_question_id) if top_question_id else {},
    }

    extraction_val = load_summary(project_root / "data" / "processed" / "ffpp_c23" / "summary_val.json")
    extraction_test = load_summary(project_root / "data" / "processed" / "ffpp_c23" / "summary_test.json")

    output = {
        "top_k": TOP_K,
        "rank_stability": {"spearman": spearman, "kendall_tau": kendall},
        "question_metrics": question_table,
        "pooling_metrics": pooling_metrics,
        "frame_metrics": frame_metrics,
        "efficiency": {
            "extraction_val": extraction_val,
            "extraction_test": extraction_test,
            "mfa_runtime_note": "Per-video MFA runtime not logged; enable profiling in future runs.",
        },
    }

    out_path = project_root / "eval" / "ffpp_c23" / "metrics.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Evaluation metrics written to {out_path}")


if __name__ == "__main__":
    main()
