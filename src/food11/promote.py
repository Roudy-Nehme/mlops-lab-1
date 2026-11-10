"""Apply an accuracy quality gate to an MLflow model version."""
import argparse
import math
import os
from pathlib import Path


def gate(candidate, champion, n):
    if n <= 0 or not all(math.isfinite(p) and 0 <= p <= 1 for p in (candidate, champion)):
        raise ValueError("Accuracies must be in [0, 1] and test size must be positive")
    margin = 2 * math.sqrt(champion * (1 - champion) / n)
    return candidate >= champion + margin, margin


def main():
    import mlflow
    from mlflow import MlflowClient

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--name", default="food11")
    parser.add_argument("--metric", default="test_accuracy")
    parser.add_argument("--test-size", type=int)
    parser.add_argument("--dataset", type=Path, default=Path("data/food11_processed_mini"))
    args = parser.parse_args()
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"))
    client = MlflowClient()
    candidate = client.get_model_version(args.name, args.version)
    champion = client.get_model_version_by_alias(args.name, "champion")
    if str(candidate.version) == str(champion.version):
        parser.error("Candidate is already champion; choose a new model version")
    candidate_run = client.get_run(candidate.run_id)
    champion_run = client.get_run(champion.run_id)
    # Use a logged evaluation size when available; otherwise count the local split.
    n = args.test_size
    if n is None:
        logged = champion_run.data.params.get("test_size")
        n = int(logged) if logged else sum(p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"} for p in (args.dataset / "evaluation").rglob("*"))
    acc_candidate = candidate_run.data.metrics[args.metric]
    acc_champion = champion_run.data.metrics[args.metric]
    promote, margin = gate(acc_candidate, acc_champion, n)
    decision = "champion" if promote else "challenger"
    print(f"candidate={acc_candidate:.6f}, champion={acc_champion:.6f}, n={n}, 2se={margin:.6f}, decision={decision}")
    tags = {"gate.decision": decision, "gate.candidate_accuracy": acc_candidate,
            "gate.champion_accuracy": acc_champion, "gate.margin": margin,
            "gate.test_size": n, "gate.previous_champion": champion.version}
    for key, value in tags.items():
        client.set_model_version_tag(args.name, args.version, key, str(value))
    client.set_registered_model_alias(args.name, decision, args.version)


if __name__ == "__main__":
    main()
