# Architecture

## System Shape

```text
Synthetic telecom leads
        |
        v
Python segmentation script
        |
        v
Campaign segments CSV
        |
        +--> Agent brief generator
        |         |
        |         v
        |   Sample scripts and manager report
        |
        v
Static dashboard
```

## Design Choices

- Static dashboard for GitHub Pages compatibility.
- Python standard library only.
- Synthetic CSV data for public sharing.
- No paid AI API required for the baseline.
- Clear upgrade path for RAG, CRM integration, and LLM-assisted follow-up drafting.

## Future AI Architecture

The next version could introduce:

- CRM connector for real campaign exports.
- Knowledge base containing approved telecom offers, objections, compliance notes, and FAQs.
- Retrieval layer for agent-assist answers.
- LLM-generated email and SMS drafts with human approval.
- Conversation summarization from call notes.
- Manager dashboard with live CRM updates.
