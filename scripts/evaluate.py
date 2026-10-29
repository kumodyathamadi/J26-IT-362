"""
Component 2 — Compliance System Evaluation & BM25 Baseline Comparison
Evaluates the Deterministic Rule Engine against a BM25 Information Retrieval Baseline.

Metrics evaluated:
- Precision
- Recall
- False Negatives (FN)
- F1-Score

Outputs:
- Formatted comparative ASCII table to stdout
- Detailed CSV results saved to benchmark/evaluation_results.csv
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Ensure repository root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from rank_bm25 import BM25Okapi
from engine.loader import load_rulebook
from engine.evaluate import evaluate_all
from engine.schema import ObligationSchema

BENCHMARK_PROFILES_PATH = _REPO_ROOT / "benchmark" / "profiles.json"
RESULTS_CSV_PATH = _REPO_ROOT / "benchmark" / "evaluation_results.csv"


def tokenize(text: str) -> List[str]:
    """Simple alphanumeric tokenizer for BM25 indexing."""
    return re.findall(r"\b\w+\b", text.lower())


def profile_to_query(profile: Dict[str, Any]) -> str:
    """
    Converts a business profile into a natural language text query for BM25.
    Excludes null/None values.
    """
    tokens = []
    for k, v in profile.items():
        if v is not None:
            if isinstance(v, bool):
                if v:
                    tokens.append(k.replace("_", " "))
            else:
                tokens.append(f"{k.replace('_', ' ')} {v}")
    return " ".join(tokens)


class BM25Baseline:
    """
    BM25 Information Retrieval Baseline over statutory source text.
    Ranks obligations and treats top-k as APPLICABLE.
    """

    def __init__(self, obligations: List[ObligationSchema], top_k: int = 2):
        self.obligations = obligations
        self.top_k = top_k
        self.corpus = [
            tokenize(f"{obl.title} {obl.action} {obl.source_text} {obl.authority} {' '.join(obl.documents_needed)}")
            for obl in obligations
        ]
        self.bm25 = BM25Okapi(self.corpus)

    def predict(self, profile: Dict[str, Any]) -> Dict[str, str]:
        query = profile_to_query(profile)
        tokenized_query = tokenize(query)

        if not tokenized_query:
            # If query is completely empty, rank nothing
            return {obl.obligation_id: "NOT_APPLICABLE" for obl in self.obligations}

        scores = self.bm25.get_scores(tokenized_query)
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)

        predicted: Dict[str, str] = {}
        for rank, idx in enumerate(ranked_indices):
            obl_id = self.obligations[idx].obligation_id
            # Treat top_k with positive score as APPLICABLE
            if rank < self.top_k and scores[idx] > 0.0:
                predicted[obl_id] = "APPLICABLE"
            else:
                predicted[obl_id] = "NOT_APPLICABLE"

        return predicted


class RuleEngineSystem:
    """Deterministic Three-Valued Logic Rule Engine System."""

    def __init__(self, obligations: List[ObligationSchema]):
        self.obligations = obligations

    def predict(self, profile: Dict[str, Any]) -> Dict[str, str]:
        results = evaluate_all(profile, self.obligations)
        return {r["obligation_id"]: r["status"] for r in results}


def compute_metrics(
    eval_records: List[Dict[str, Any]], system_name: str
) -> Dict[str, Any]:
    """
    Computes Precision, Recall, False Negatives, and F1 Score for a given system
    with respect to positive class 'APPLICABLE'.
    """
    tp = 0
    fp = 0
    fn = 0
    tn = 0

    for r in eval_records:
        ground_truth = r["expected_status"]
        pred = r[f"{system_name}_predicted"]

        is_gt_positive = (ground_truth == "APPLICABLE")
        is_pred_positive = (pred == "APPLICABLE")

        if is_gt_positive and is_pred_positive:
            tp += 1
        elif not is_gt_positive and is_pred_positive:
            fp += 1
        elif is_gt_positive and not is_pred_positive:
            fn += 1
        else:
            tn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "system": system_name,
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
    }


def run_evaluation() -> Tuple[Dict[str, Any], Dict[str, Any], List[Dict[str, Any]]]:
    obligations = load_rulebook()
    bm25_model = BM25Baseline(obligations, top_k=2)
    rule_engine = RuleEngineSystem(obligations)

    with open(BENCHMARK_PROFILES_PATH, "r", encoding="utf-8") as fh:
        test_cases = json.load(fh)

    detailed_records: List[Dict[str, Any]] = []

    for tc in test_cases:
        p_id = tc["profile_id"]
        profile = tc["profile"]
        expected = tc["expected"]

        re_preds = rule_engine.predict(profile)
        bm25_preds = bm25_model.predict(profile)

        for obl in obligations:
            oid = obl.obligation_id
            gt = expected.get(oid, "UNKNOWN")
            r_pred = re_preds.get(oid, "UNKNOWN")
            b_pred = bm25_preds.get(oid, "NOT_APPLICABLE")

            detailed_records.append({
                "profile_id": p_id,
                "obligation_id": oid,
                "expected_status": gt,
                "rule_engine_predicted": r_pred,
                "rule_engine_correct": (r_pred == gt),
                "bm25_predicted": b_pred,
                "bm25_correct": (b_pred == gt),
            })

    re_metrics = compute_metrics(detailed_records, "rule_engine")
    bm25_metrics = compute_metrics(detailed_records, "bm25")

    # Save detailed CSV
    RESULTS_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "profile_id",
        "obligation_id",
        "expected_status",
        "rule_engine_predicted",
        "rule_engine_correct",
        "bm25_predicted",
        "bm25_correct",
    ]
    with open(RESULTS_CSV_PATH, "w", newline="", encoding="utf-8") as csv_fh:
        writer = csv.DictWriter(csv_fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(detailed_records)

    return re_metrics, bm25_metrics, detailed_records


def print_comparison_table(re_metrics: Dict[str, Any], bm25_metrics: Dict[str, Any]) -> None:
    print("\n" + "=" * 78)
    print(" COMPONENT 2 EVALUATION: RULE ENGINE vs. BM25 BASELINE")
    print("=" * 78)
    print(f"{'Metric':<25} | {'Rule Engine (Deterministic)':<26} | {'BM25 Baseline (IR Top-K)':<20}")
    print("-" * 78)
    print(f"{'Precision':<25} | {re_metrics['precision']:<26.4f} | {bm25_metrics['precision']:<20.4f}")
    print(f"{'Recall':<25} | {re_metrics['recall']:<26.4f} | {bm25_metrics['recall']:<20.4f}")
    print(f"{'F1-Score':<25} | {re_metrics['f1_score']:<26.4f} | {bm25_metrics['f1_score']:<20.4f}")
    print(f"{'False Negatives (FN)':<25} | {re_metrics['false_negatives']:<26} | {bm25_metrics['false_negatives']:<20}")
    print(f"{'False Positives (FP)':<25} | {re_metrics['false_positives']:<26} | {bm25_metrics['false_positives']:<20}")
    print(f"{'True Positives (TP)':<25} | {re_metrics['true_positives']:<26} | {bm25_metrics['true_positives']:<20}")
    print(f"{'True Negatives (TN)':<25} | {re_metrics['true_negatives']:<26} | {bm25_metrics['true_negatives']:<20}")
    print("=" * 78)
    print(f"[OK] Full evaluation CSV exported to: {RESULTS_CSV_PATH}\n")


if __name__ == "__main__":
    re_metrics, bm25_metrics, _ = run_evaluation()
    print_comparison_table(re_metrics, bm25_metrics)
