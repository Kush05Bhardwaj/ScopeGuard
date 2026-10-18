from datetime import date

from app.schemas.report import ChangeOrderReportRequest, ChangeOrderReportResponse


def generate_change_order(
    request: ChangeOrderReportRequest,
    estimate_assumptions: str = "",
) -> ChangeOrderReportResponse:
    if not request.analysis.evidence and (
        request.analysis.category != "needs_review"
        or not request.analysis.requires_human_review
    ):
        raise ValueError(
            "Analysis without verified evidence must require human review and use needs_review."
        )
    if (
        request.analysis.category in {"needs_review", "potential_scope_change"}
        and not request.analysis.requires_human_review
    ):
        raise ValueError(
            "Potential scope changes and ambiguous analyses must require human review."
        )

    unverified_quotes = [
        item.quote
        for item in request.analysis.evidence
        if item.quote not in request.agreement_text
    ]
    if unverified_quotes:
        raise ValueError("Evidence must match an exact passage in the supplied agreement.")

    title = f"Change Order Proposal — {request.project_name}"
    client_line = f"**Client:** {request.client_name}\n\n" if request.client_name.strip() else ""
    proposed_work = request.proposed_work.strip() or "To be defined and approved by both parties."
    human_review_note = (
        "**Human review required:** Yes. Review this analysis and the agreement before relying on the proposal."
        if request.analysis.requires_human_review
        else "**Human review required:** Review the evidence and proposal before approval."
    )
    evidence_section = (
        "\n\n".join(
            f"> {item.quote.replace(chr(10), chr(10) + '> ')}\n\n"
            f"{item.explanation}"
            for item in request.analysis.evidence
        )
        if request.analysis.evidence
        else "No verified agreement passage was returned. Manual review is required."
    )
    estimate_note = (
        f"\n\n**AI-generated planning estimate — review and edit before sharing.** "
        f"Assumptions: {estimate_assumptions.strip()}"
        if estimate_assumptions.strip()
        else ""
    )

    markdown = f"""# {title}

**Date:** {date.today().isoformat()}

{client_line}**Status:** Draft — requires review and approval

**Original agreement:** {request.agreement_reference.strip() or "Not provided"}

## 1. Background

This proposal documents a requested change to the existing project scope.

## 2. Client Request

{request.client_request.strip()}

## 3. Scope Analysis

**Classification:** {request.analysis.category.replace("_", " ").title()}

{request.analysis.summary.strip()}

{request.analysis.reasoning.strip()}

{human_review_note}

## 4. Agreement Evidence

{evidence_section}

## 5. Proposed Additional Work

{proposed_work}

## 6. Estimated Cost

{request.estimated_cost.strip() or "To be agreed"}
{estimate_note}

## 7. Estimated Timeline

{request.estimated_timeline.strip() or "To be agreed"}

## 8. Approval and Next Steps

Please review and edit the proposed work, cost, and timeline. Discuss any open details, then record explicit approval from both parties before beginning additional work.

**Client approval:** ____________________

**Date:** ____________________

**Provider approval:** ____________________

**Date:** ____________________

---

*This document is a draft for discussion, not legal advice or a signed agreement.*
"""
    return ChangeOrderReportResponse(
        title=title,
        markdown=markdown,
        estimated_cost=request.estimated_cost.strip() or "To be agreed",
        estimated_timeline=request.estimated_timeline.strip() or "To be agreed",
        estimate_assumptions=estimate_assumptions,
    )
