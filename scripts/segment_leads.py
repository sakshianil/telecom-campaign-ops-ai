#!/usr/bin/env python3
"""Segment synthetic telecom leads for a virtual center pilot."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "synthetic_telecom_leads.csv"
OUTPUT = ROOT / "data" / "campaign_segments.csv"


def as_int(row: dict[str, str], key: str) -> int:
    return int(row[key])


def score_lead(row: dict[str, str]) -> tuple[int, str, str]:
    contract = as_int(row, "contract_months_remaining")
    tickets = as_int(row, "support_tickets_90d")
    spend = as_int(row, "monthly_spend_usd")
    usage = as_int(row, "data_usage_gb")
    payment_risk = row["payment_risk"]

    churn_score = 0
    if contract <= 2:
        churn_score += 28
    if tickets >= 3:
        churn_score += 24
    if payment_risk == "High":
        churn_score += 22
    elif payment_risk == "Medium":
        churn_score += 10
    if row["current_status"].lower().find("complaint") >= 0 or row["current_status"].lower().find("escalation") >= 0:
        churn_score += 18

    upgrade_score = 0
    if usage >= 600:
        upgrade_score += 28
    if spend >= 90:
        upgrade_score += 20
    if row["segment"] in {"Small Business", "Enterprise"}:
        upgrade_score += 18
    if row["current_status"].lower().find("prospect") >= 0 or row["current_status"].lower().find("eligible") >= 0:
        upgrade_score += 18

    if churn_score >= upgrade_score and churn_score >= 42:
        campaign = "Retention rescue"
        next_action = "Priority phone call with service recovery offer"
        score = churn_score
    elif upgrade_score >= 45:
        campaign = "Plan upgrade"
        next_action = "Email value bundle, then phone follow-up"
        score = upgrade_score
    elif contract <= 2:
        campaign = "Renewal"
        next_action = "Confirm renewal interest and contract timing"
        score = max(churn_score, 35)
    else:
        campaign = "Nurture"
        next_action = "Low-pressure SMS or email check-in"
        score = max(churn_score, upgrade_score, 18)

    priority = "High" if score >= 60 else "Medium" if score >= 38 else "Low"
    return score, priority, f"{campaign}: {next_action}"


def main() -> None:
    with INPUT.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    output_rows = []
    for row in rows:
        score, priority, recommendation = score_lead(row)
        output_rows.append(
            {
                **row,
                "campaign_score": score,
                "priority": priority,
                "recommended_action": recommendation,
            }
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0].keys()))
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Wrote {len(output_rows)} segmented leads to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
