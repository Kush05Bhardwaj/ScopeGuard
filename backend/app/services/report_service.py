from datetime import date

from app.schemas.report import ChangeOrderReportRequest, ChangeOrderReportResponse


def generate_change_order(
    request: ChangeOrderReportRequest,
) -> ChangeOrderReportResponse:
    unverified_quotes = [
        item.quote for item in request.evidence if item.quote not in request.agreement_text
    ]
    if unverified_quotes:
        raise ValueError("Evidence must match an exact passage in the supplied agreement.")

    title = f"Change Order Proposal — {request.project_name}"
    client_line = f"**Client:** {request.client_name}\n\n" if request.client_name.strip() else ""
    proposed_work = request.proposed_work.strip() or "To be defined and approved by both parties."
    evidence_section = (
        "\n\n".join(
            f"> {item.quote.replace(chr(10), chr(10) + '> ')}\n\n"
            f"{item.explanation}"
            for item in request.evidence
        )
        if request.evidence
        else "No verified agreement passage was returned. Manual review is required."
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

**Classification:** {request.analysis_category.replace("_", " ").title()}

{request.analysis_summary.strip()}

## 4. Agreement Evidence

{evidence_section}

## 5. Proposed Additional Work

{proposed_work}

## 6. Estimated Cost

{request.estimated_cost.strip() or "To be agreed"}

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
    return ChangeOrderReportResponse(title=title, markdown=markdown)
