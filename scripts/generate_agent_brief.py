#!/usr/bin/env python3
"""Generate sample agent scripts and a manager report from segmented telecom leads."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEGMENTS = ROOT / "data" / "campaign_segments.csv"
AGENT_OUTPUT = ROOT / "outputs" / "sample_agent_scripts.md"
REPORT_OUTPUT = ROOT / "outputs" / "sample_manager_report.md"


def load_rows() -> list[dict[str, str]]:
    with SEGMENTS.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def script_for(row: dict[str, str]) -> str:
    action = row["recommended_action"]
    if action.startswith("Retention rescue"):
        opener = "I am calling to make sure your service issues are understood and resolved before your renewal decision."
        offer = "Confirm the issue, summarize the support history, and offer a retention review or service-quality callback."
    elif action.startswith("Plan upgrade"):
        opener = "I am reaching out because your current usage suggests a stronger telecom package may fit your needs better."
        offer = "Explain the upgrade value in one sentence, then ask which capability matters most: speed, reliability, bundle cost, or support."
    elif action.startswith("Renewal"):
        opener = "I am checking in because your current contract is near its renewal window."
        offer = "Confirm the decision timeline, ask about service satisfaction, and schedule a follow-up if needed."
    else:
        opener = "I am checking whether your current telecom plan is still working well for you."
        offer = "Keep the conversation short, verify contact preference, and ask permission for a future offer."

    return (
        f"### {row['lead_id']} - {row['customer_name']}\n\n"
        f"- Segment: {row['segment']} in {row['region']}\n"
        f"- Service: {row['service_type']}\n"
        f"- Priority: {row['priority']} ({row['campaign_score']})\n"
        f"- Recommended action: {row['recommended_action']}\n"
        f"- Opening line: {opener}\n"
        f"- Agent guidance: {offer}\n"
        f"- CRM note: Log customer sentiment, objection, callback date, and next-best offer.\n"
    )


def write_agent_scripts(rows: list[dict[str, str]]) -> None:
    top_rows = sorted(rows, key=lambda row: int(row["campaign_score"]), reverse=True)[:8]
    content = [
        "# Sample Agent Scripts",
        "",
        "Synthetic examples generated from `data/campaign_segments.csv`.",
        "",
    ]
    content.extend(script_for(row) for row in top_rows)
    AGENT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    AGENT_OUTPUT.write_text("\n".join(content), encoding="utf-8")


def write_manager_report(rows: list[dict[str, str]]) -> None:
    total = len(rows)
    priority_counts = Counter(row["priority"] for row in rows)
    campaign_counts = Counter(row["recommended_action"].split(":")[0] for row in rows)
    high_value = [row for row in rows if row["segment"] in {"Small Business", "Enterprise"}]
    phone_queue = [row for row in rows if row["preferred_channel"] == "Phone" and row["priority"] == "High"]

    lines = [
        "# Sample Manager Report",
        "",
        "This report uses synthetic data for portfolio demonstration.",
        "",
        "## Pilot Snapshot",
        "",
        f"- Total leads reviewed: {total}",
        f"- High-priority leads: {priority_counts['High']}",
        f"- Medium-priority leads: {priority_counts['Medium']}",
        f"- Low-priority leads: {priority_counts['Low']}",
        f"- Business or enterprise accounts: {len(high_value)}",
        f"- High-priority phone queue: {len(phone_queue)}",
        "",
        "## Campaign Mix",
        "",
    ]
    for campaign, count in campaign_counts.most_common():
        lines.append(f"- {campaign}: {count}")

    lines.extend(
        [
            "",
            "## Manager Recommendations",
            "",
            "- Start with the high-priority phone queue before broad outbound activity.",
            "- Assign senior agents to retention rescue accounts with support-ticket history.",
            "- Use email first for upgrade campaigns where the customer prefers written information.",
            "- Review objections daily and update the script after each calling block.",
            "- Keep the pilot to 2-5 agents until conversion, callback, and complaint-resolution trends are visible.",
        ]
    )
    REPORT_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = load_rows()
    write_agent_scripts(rows)
    write_manager_report(rows)
    print(f"Wrote {AGENT_OUTPUT.relative_to(ROOT)}")
    print(f"Wrote {REPORT_OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
