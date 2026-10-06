"""Case-level findings and a compact court-oriented field brief."""

from __future__ import annotations

from collections import Counter
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def build_findings(links, transactions, account_risk, multi_hop_paths):
    shared = Counter(link["type"] for link in links)
    high_risk = [item for item in account_risk if item["risk_level"] == "HIGH"]
    recommendations = []
    if high_risk:
        recommendations.append("Prioritise preservation request / debit-freeze review for high-risk intermediary accounts.")
    if multi_hop_paths:
        recommendations.append("Issue time-bounded transaction preservation requests for every account in the detected money trail.")
    if any(shared.get(key) for key in ("imei", "imsi", "mac")):
        recommendations.append("Preserve linked handset and subscriber records; shared device identifiers require investigator verification.")
    return {
        "prime_suspects": high_risk[:10],
        "shared_identifier_counts": dict(shared),
        "multi_hop_path_count": len(multi_hop_paths),
        "recommendations": recommendations or ["Review uploaded artefacts and collect supplementary banking, telecom, or device evidence."],
        "analyst_note": "Links are deterministic shared-observable correlations, not a finding of guilt. Validate against original evidence before operational action.",
    }


def build_pdf(case_id, evidence, findings, transactions):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=1.4*cm, rightMargin=1.4*cm, topMargin=1.2*cm, bottomMargin=1.2*cm)
    styles = getSampleStyleSheet()
    story = [Paragraph("Cyber fraud investigation brief", styles["Title"]), Paragraph(f"Case ID: {case_id}", styles["Normal"]), Spacer(1, 10), Paragraph("Evidence integrity", styles["Heading2"])]
    rows = [["File", "Rows", "SHA-256 (prefix)"]] + [[item["filename"], str(item["rows"]), item["sha256"][:20] + "…"] for item in evidence]
    table = Table(rows, colWidths=[6*cm, 2*cm, 8*cm])
    table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1f4e78")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("GRID", (0,0), (-1,-1), .25, colors.grey), ("FONTSIZE", (0,0), (-1,-1), 8)]))
    story += [table, Spacer(1, 10), Paragraph("Priority findings", styles["Heading2"])]
    suspects = "; ".join(f"{item['account']} ({item['risk_score']}/100)" for item in findings["prime_suspects"]) or "No high-risk account reached the configured threshold."
    story += [Paragraph(f"High-risk accounts: {suspects}", styles["BodyText"]), Paragraph(f"Multi-hop money paths: {findings['multi_hop_path_count']}; transactions parsed: {len(transactions)}.", styles["BodyText"]), Spacer(1, 8), Paragraph("Immediate recommendations", styles["Heading2"])]
    story += [Paragraph(f"• {item}", styles["BodyText"]) for item in findings["recommendations"]]
    story += [Spacer(1, 8), Paragraph(findings["analyst_note"], styles["Italic"])]
    doc.build(story)
    return buffer.getvalue()
