"""
Training Pipeline for SME Regulatory Action Guidance Model
AI-Driven Business Lifecycle Decision Support System — Component 2
"""

import os
import json
import logging
from typing import Dict, Any, List
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ActionModelTrainer")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATASET_PATH = os.path.join(
    PROJECT_ROOT, "data", "compliance", "action_datasets", "western_province_sme_action_dataset_360.csv"
)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "models", "action_guidance_model")


def load_and_preprocess_data(dataset_path: str):
    logger.info("Loading dataset from: %s", dataset_path)
    df = pd.read_csv(dataset_path)
    logger.info("Dataset loaded successfully with shape: %s", df.shape)

    # Basic cleaning
    df["business_type"] = df["business_type"].fillna("general_sme")
    df["business_scale"] = df["business_scale"].fillna("micro")
    df["location_district"] = df["location_district"].fillna("Colombo")
    df["has_physical_premises"] = df["has_physical_premises"].astype(str)
    df["activity"] = df["activity"].fillna("")
    df["business_context"] = df["business_context"].fillna("")
    df["user_question"] = df["user_question"].fillna("")
    df["legal_source_files"] = df["legal_source_files"].fillna("")

    # Construct unified representation for rich feature representation
    df["composite_text"] = (
        "Rules & Legal Sources: " + df["legal_source_files"] + ". " +
        "Business Type: " + df["business_type"] + ". " +
        "Scale: " + df["business_scale"] + ". " +
        "District: " + df["location_district"] + ". " +
        "Physical Premises: " + df["has_physical_premises"] + ". " +
        "Context: " + df["business_context"] + ". " +
        "Activity: " + df["activity"] + ". " +
        "Inquiry: " + df["user_question"]
    )

    return df



def build_knowledge_index(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Builds an authoritative procedural knowledge index grouped by action_type and category,
    capturing concrete institutional authorities, required documents, and procedural steps
    for Western Province SMEs.
    """
    knowledge = {}

    wp_offices = {
        "business_registration": "Divisional Secretariat (Department of Business Names) / Registrar of Companies (eROC, Colombo)",
        "food_business": "Local Authority Health Department (CMC / Municipal / Urban Council / Pradeshiya Sabha) & MOH / PHI Office",
        "environmental_waste": "Central Environmental Authority (CEA Head Office Battaramulla / District Offices) & Local Authority",
        "vehicle_repair_motor_trade": "Department of Motor Traffic (DMT Werahera / Narahenpita) & Local Authority Trade Licensing Unit",
        "cosmetics_salon": "National Medicines Regulatory Authority (NMRA Colombo 10) & Local Authority Health Unit",
        "data_protection_digital": "Data Protection Authority of Sri Lanka (DPA SL), Colombo",
    }

    for action_type, group in df.groupby("action_type"):
        sample = group.iloc[0]
        cat = str(sample.get("category", ""))

        # Parse documents list from string (pipe-separated)
        docs_raw = str(sample.get("required_documents", ""))
        documents = [d.strip() for d in docs_raw.split("|") if d.strip()]

        # Parse procedural steps list from string (pipe-separated)
        steps_raw = str(sample.get("procedural_steps", ""))
        steps = [s.strip() for s in steps_raw.split("|") if s.strip()]

        # Parse cited source acts
        sources_raw = str(sample.get("legal_source_files", ""))
        legal_sources = [src.strip() for src in sources_raw.split("|") if src.strip()]

        office_loc = wp_offices.get(cat, "Relevant District / Local Authority Office (Western Province)")

        knowledge[action_type] = {
            "action_type": action_type,
            "category": cat,
            "required_action_name": str(sample.get("required_action_name", "")),
            "target_authority": str(sample.get("target_authority", "")),
            "office_location": office_loc,
            "action_urgency": str(sample.get("action_urgency", "Prior to commencing commercial activities")),
            "required_documents": documents,
            "procedural_steps": steps,
            "legal_sources": legal_sources,
            "applicability_status": str(sample.get("applicability_status", "UNKNOWN")),
            "review_instructions": str(sample.get("review_instructions", "")),
            "province_scope": "Western Province (Colombo, Gampaha, Kalutara)",
        }

    return knowledge


def train_action_guidance_model(df: pd.DataFrame):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    X_text = df["composite_text"]
    y_action = df["action_type"]
    y_category = df["category"]

    logger.info("Target classes distribution:\n%s", y_action.value_counts())

    # Stratified Train/Test Split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X_text, y_action, test_size=0.20, random_state=42, stratify=y_action
    )

    logger.info("Training set size: %d, Test set size: %d", len(X_train), len(X_test))

    # Candidate models for model benchmarking
    candidates = {
        "LogisticRegression": LogisticRegression(max_iter=1000, C=1.0, random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42),
    }

    best_model_name = None
    best_score = -1.0
    best_pipeline = None

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    benchmark_results = {}

    for name, clf in candidates.items():
        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=2500, sublinear_tf=True)),
            ("clf", clf),
        ])

        scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="f1_macro")
        mean_cv = float(scores.mean())
        std_cv = float(scores.std())

        benchmark_results[name] = {
            "mean_cv_f1_macro": mean_cv,
            "std_cv": std_cv,
            "fold_scores": [float(s) for s in scores],
        }
        logger.info("Model: %-20s | 5-Fold CV F1-Macro: %.4f (+/- %.4f)", name, mean_cv, std_cv)

        if mean_cv > best_score:
            best_score = mean_cv
            best_model_name = name
            best_pipeline = pipeline

    logger.info("Selected Champion Model: %s with CV Score: %.4f", best_model_name, best_score)

    # Train Champion Model on full train set and evaluate on test set
    best_pipeline.fit(X_train, y_train)
    y_pred = best_pipeline.predict(X_test)
    y_pred_proba = best_pipeline.predict_proba(X_test) if hasattr(best_pipeline, "predict_proba") else None

    # Compute evaluation metrics
    test_acc = accuracy_score(y_test, y_pred)
    p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(y_test, y_pred, average="macro")
    p_weighted, r_weighted, f1_weighted, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted")

    cls_report = classification_report(y_test, y_pred, output_dict=True)
    labels = sorted(list(y_action.unique()))
    cm = confusion_matrix(y_test, y_pred, labels=labels).tolist()

    evaluation_report = {
        "model_architecture": f"TF-IDF(1,2) + {best_model_name}",
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "test_accuracy": round(test_acc, 4),
        "macro_metrics": {
            "precision": round(p_macro, 4),
            "recall": round(r_macro, 4),
            "f1_score": round(f1_macro, 4),
        },
        "weighted_metrics": {
            "precision": round(p_weighted, 4),
            "recall": round(r_weighted, 4),
            "f1_score": round(f1_weighted, 4),
        },
        "cross_validation_benchmark": benchmark_results,
        "per_class_classification_report": cls_report,
        "confusion_matrix": {
            "labels": labels,
            "matrix": cm,
        },
    }

    # Save Pipeline and Index Artifacts
    model_path = os.path.join(OUTPUT_DIR, "action_guidance_pipeline.joblib")
    joblib.dump(best_pipeline, model_path)
    logger.info("Saved model pipeline to: %s", model_path)

    knowledge_index = build_knowledge_index(df)
    index_path = os.path.join(OUTPUT_DIR, "action_knowledge_index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(knowledge_index, f, indent=2, ensure_ascii=False)
    logger.info("Saved action knowledge index to: %s", index_path)

    metrics_path = os.path.join(OUTPUT_DIR, "evaluation_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(evaluation_report, f, indent=2)
    logger.info("Saved evaluation report to: %s", metrics_path)

    # Perform a sample inference to verify end-to-end functionality
    test_query = (
        "Business Type: food_business. Scale: small. District: Colombo. "
        "Physical Premises: True. Context: new business. Activity: bakery manufacturing. "
        "Inquiry: I want to start a food bakery and need to obtain environmental clearance and trade license."
    )
    predicted_action = best_pipeline.predict([test_query])[0]
    action_details = knowledge_index.get(predicted_action, {})

    sample_output = {
        "test_input": test_query,
        "predicted_action_type": predicted_action,
        "action_details": action_details,
    }
    sample_output_path = os.path.join(OUTPUT_DIR, "test_inference_output.json")
    with open(sample_output_path, "w", encoding="utf-8") as f:
        json.dump(sample_output, f, indent=2, ensure_ascii=False)

    logger.info("\n=== EVALUATION REPORT SUMMARY ===")
    logger.info("Champion Model: %s", best_model_name)
    logger.info("Test Accuracy:  %.2f%%", test_acc * 100)
    logger.info("Macro F1-Score: %.4f", f1_macro)
    logger.info("Sample Prediction for Bakery: %s", predicted_action)
    logger.info("=================================")

    return evaluation_report


if __name__ == "__main__":
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Action dataset not found at {DATASET_PATH}")
    df = load_and_preprocess_data(DATASET_PATH)
    train_action_guidance_model(df)
