import io
import json
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

from streamlit.components.v1 import html as components_html

from pyvis.network import Network

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Cyber Fraud Correlator",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

BACKEND_URL = "http://127.0.0.1:8000"


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at top right,
                rgba(40, 55, 75, 0.18),
                transparent 32%
            ),
            #0b0f14;
        color: #e8edf3;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    [data-testid="stSidebar"] {
        background: #090d12;
        border-right: 1px solid #1d2630;
    }

    h1, h2, h3 {
        color: #edf2f7 !important;
        letter-spacing: -0.02em;
    }

    [data-testid="stMetric"] {
        background: #10161e;
        border: 1px solid #202a35;
        border-radius: 12px;
        padding: 15px 16px;
    }

    [data-testid="stMetricLabel"] {
        color: #8d9aaa !important;
        font-size: 0.82rem !important;
    }

    [data-testid="stMetricValue"] {
        color: #edf2f7 !important;
        font-weight: 650;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(15, 21, 29, 0.75);
        border-color: #202a35 !important;
        border-radius: 14px !important;
    }

    .stButton > button {
        border-radius: 9px;
        border: 1px solid #293542;
        background: #141b23;
        color: #e8edf3;
        font-weight: 600;
    }

    .stButton > button:hover {
        border-color: #526476;
        background: #1a232d;
    }

    .stDownloadButton > button {
        border-radius: 9px;
        border: 1px solid #293542;
        background: #141b23;
        color: #e8edf3;
        font-weight: 600;
    }

    .stDownloadButton > button:hover {
        border-color: #526476;
        background: #1a232d;
    }

    button[data-baseweb="tab"] {
        color: #8996a5;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #edf2f7;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def format_inr(value):

    try:
        return f"₹{float(value):,.0f}"

    except Exception:
        return "₹0"


def format_number(value):

    try:
        return f"{int(value):,}"

    except Exception:
        return "0"


def api_health():

    try:

        response = requests.get(
            f"{BACKEND_URL}/health",
            timeout=3,
        )

        return response.ok

    except Exception:

        return False


def send_analysis(uploaded_files):

    multipart_files = []

    for uploaded_file in uploaded_files:

        multipart_files.append(
            (
                "files",
                (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                    or "application/octet-stream",
                ),
            )
        )

    response = requests.post(
        f"{BACKEND_URL}/ingest",
        files=multipart_files,
        timeout=120,
    )

    if not response.ok:

        try:

            detail = response.json().get(
                "detail",
                response.text,
            )

        except Exception:

            detail = response.text

        raise RuntimeError(
            f"Backend analysis failed: {detail}"
        )

    return response.json()


# ============================================================
# ENTITY GRAPH
# ============================================================

def make_graph_html(graph_data):

    network = Network(
        height="650px",
        width="100%",
        bgcolor="#0b0f14",
        font_color="#dce4ec",
        directed=False,
    )

    network.set_options(
        """
        {
          "nodes": {
            "shape": "dot",
            "font": {
              "size": 12,
              "face": "Arial"
            },
            "borderWidth": 1
          },

          "edges": {
            "color": {
              "color": "#394653",
              "highlight": "#8795a4"
            },
            "width": 1,
            "smooth": {
              "enabled": true,
              "type": "dynamic"
            }
          },

          "physics": {
            "enabled": true,
            "stabilization": {
              "iterations": 250
            },
            "barnesHut": {
              "gravitationalConstant": -4500,
              "centralGravity": 0.15,
              "springLength": 150,
              "springConstant": 0.03,
              "damping": 0.8
            }
          },

          "interaction": {
            "hover": true,
            "navigationButtons": true,
            "keyboard": true
          }
        }
        """
    )

    node_colors = {
        "account_id": "#c94c4c",
        "upi_id": "#c99345",
        "phone": "#3b9ed8",
        "imei": "#8f7cc7",
        "imsi": "#a77bc4",
        "ip": "#3ca8aa",
        "mac": "#4caaa0",
        "evidence": "#4a5562",
    }

    for node in graph_data.get(
        "nodes",
        [],
    ):

        node_id = node.get(
            "id",
            "",
        )

        node_type = node.get(
            "node_type",
            "unknown",
        )

        label = node.get(
            "label",
            node_id,
        )

        color = node_colors.get(
            node_type,
            "#66717d",
        )

        if node_type == "evidence":

            label = (
                f"Evidence\n"
                f"{node.get('source', node_id)}"
            )

        network.add_node(
            node_id,
            label=label,
            color=color,
            title=(
                f"Type: {node_type}"
                f"<br>Value: {label}"
            ),
            size=20
            if node_type != "evidence"
            else 12,
        )

    for edge in graph_data.get(
        "edges",
        [],
    ):

        source = edge.get(
            "source"
        )

        target = edge.get(
            "target"
        )

        if not source or not target:
            continue

        relationship = edge.get(
            "relationship",
            "",
        )

        evidence = edge.get(
            "evidence",
            "",
        )

        title = relationship

        if evidence:

            title += (
                f"<br>Evidence: {evidence}"
            )

        network.add_edge(
            source,
            target,
            title=title,
        )

    return network.generate_html()


# ============================================================
# FUND FLOW
# ============================================================

def make_fund_flow_html(transactions):

    network = Network(
        height="560px",
        width="100%",
        bgcolor="#0b0f14",
        font_color="#dce4ec",
        directed=True,
    )

    network.set_options(
        """
        {
          "nodes": {
            "shape": "dot",
            "font": {
              "size": 13
            }
          },

          "edges": {
            "arrows": {
              "to": {
                "enabled": true,
                "scaleFactor": 0.7
              }
            },

            "font": {
              "size": 10,
              "color": "#aeb9c5",
              "strokeWidth": 0
            },

            "smooth": {
              "enabled": true,
              "type": "curvedCW"
            }
          },

          "physics": {
            "enabled": true,
            "stabilization": {
              "iterations": 200
            },

            "barnesHut": {
              "gravitationalConstant": -6000,
              "springLength": 190,
              "springConstant": 0.03
            }
          }
        }
        """
    )

    seen_nodes = set()

    for transaction in transactions:

        source = transaction.get(
            "sender_account"
        )

        target = transaction.get(
            "receiver_account"
        )

        amount = transaction.get(
            "amount",
            0,
        )

        txn_id = transaction.get(
            "transaction_id",
            "",
        )

        timestamp = transaction.get(
            "timestamp",
            "",
        )

        if not source or not target:
            continue

        for account in [
            source,
            target,
        ]:

            if account in seen_nodes:
                continue

            seen_nodes.add(
                account
            )

            if account.startswith(
                "vic-"
            ):

                color = "#3b9ed8"

            elif account.startswith(
                "acct-"
            ):

                color = "#c94c4c"

            else:

                color = "#c99345"

            network.add_node(
                account,
                label=account,
                color=color,
                size=25,
            )

        network.add_edge(
            source,
            target,
            label=format_inr(
                amount
            ),
            title=(
                f"Transaction: {txn_id}"
                f"<br>Amount: {format_inr(amount)}"
                f"<br>Time: {timestamp}"
            ),
        )

    return network.generate_html()


# ============================================================
# TIMELINE
# ============================================================

def prepare_timeline(
    transactions
):

    timeline = []

    for transaction in transactions:

        timestamp = transaction.get(
            "timestamp"
        )

        try:

            parsed = datetime.fromisoformat(
                str(timestamp)
            )

        except Exception:

            parsed = None

        timeline.append(
            {
                "parsed": parsed,

                "transaction_id": transaction.get(
                    "transaction_id",
                    "",
                ),

                "timestamp": timestamp,

                "source": transaction.get(
                    "sender_account",
                    "",
                ),

                "target": transaction.get(
                    "receiver_account",
                    "",
                ),

                "amount": transaction.get(
                    "amount",
                    0,
                ),

                "upi_id": transaction.get(
                    "upi_id",
                    "",
                ),
            }
        )

    timeline.sort(
        key=lambda item: (
            item["parsed"]
            or datetime.max
        )
    )

    return timeline


def show_timeline(
    transactions
):

    timeline = prepare_timeline(
        transactions
    )

    if not timeline:

        st.info(
            "No transaction timeline is available."
        )

        return

    for index, event in enumerate(
        timeline
    ):

        col1, col2, col3 = st.columns(
            [1.1, 5, 1.4]
        )

        with col1:

            timestamp = event[
                "timestamp"
            ]

            try:

                parsed = datetime.fromisoformat(
                    str(timestamp)
                )

                st.markdown(
                    f"**{parsed.strftime('%H:%M:%S')}**"
                )

            except Exception:

                st.markdown(
                    f"**{timestamp or 'Unknown'}**"
                )

        with col2:

            st.markdown(
                f"**{event['source']}** "
                f"→ "
                f"**{event['target']}**"
            )

            st.caption(
                f"{event['transaction_id']}"
                f"  ·  "
                f"{event['upi_id'] or 'No UPI'}"
            )

        with col3:

            st.markdown(
                f"**{format_inr(event['amount'])}**"
            )

        if index < len(
            timeline
        ) - 1:

            st.divider()


# ============================================================
# PDF
# ============================================================

def build_pdf_report(
    result
):

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Cyber Fraud Investigation Report",
        author="Cyber Fraud Correlator",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=21,
        leading=25,
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        alignment=TA_CENTER,
        textColor=colors.HexColor(
            "#667085"
        ),
        spaceAfter=18,
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=17,
        spaceBefore=12,
        spaceAfter=7,
        textColor=colors.HexColor(
            "#17212b"
        ),
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        spaceAfter=7,
    )

    small_style = ParagraphStyle(
        "ReportSmall",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor(
            "#56616d"
        ),
    )

    story = []

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "CYBER FRAUD CORRELATOR",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Unified Cyber Fraud Analysis & Digital Artifact Correlation",
            subtitle_style,
        )
    )

    story.append(
        Paragraph(
            f"Generated: "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            subtitle_style,
        )
    )

    # --------------------------------------------------------
    # Brief
    # --------------------------------------------------------

    brief = result.get(
        "investigation_brief",
        {}
    )

    ai = result.get(
        "ai_investigation",
        {}
    )

    story.append(
        Paragraph(
            "1. Executive Summary",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            brief.get(
                "case_assessment",
                "No assessment available.",
            ),
            body_style,
        )
    )

    # --------------------------------------------------------
    # AI section
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "2. AI Investigator Assessment",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            ai.get(
                "narrative",
                "No AI assessment available.",
            ),
            body_style,
        )
    )

    if ai.get(
        "key_indicators"
    ):

        story.append(
            Paragraph(
                "<b>Key Indicators</b>",
                body_style,
            )
        )

        for indicator in ai.get(
            "key_indicators",
            [],
        ):

            story.append(
                Paragraph(
                    f"• {indicator}",
                    body_style,
                )
            )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "3. Investigation Statistics",
            heading_style,
        )
    )

    flow_statistics = result.get(
        "flow_statistics",
        {}
    )

    stats = brief.get(
        "statistics",
        {}
    )

    statistics_data = [
        ["Metric", "Value"],

        [
            "Evidence Files",
            str(
                stats.get(
                    "evidence_files",
                    len(
                        result.get(
                            "evidence",
                            [],
                        )
                    ),
                )
            ),
        ],

        [
            "Records",
            str(
                stats.get(
                    "records",
                    result.get(
                        "records",
                        0,
                    ),
                )
            ),
        ],

        [
            "Entity Links",
            str(
                stats.get(
                    "entity_links",
                    result.get(
                        "links",
                        0,
                    ),
                )
            ),
        ],

        [
            "Transactions",
            str(
                stats.get(
                    "transactions",
                    len(
                        result.get(
                            "transactions",
                            [],
                        )
                    ),
                )
            ),
        ],

        [
            "Transaction Value",
            format_inr(
                flow_statistics.get(
                    "total_value",
                    0,
                )
            ),
        ],

        [
            "High-Risk Accounts",
            str(
                stats.get(
                    "high_risk_accounts",
                    0,
                )
            ),
        ],

        [
            "Medium-Risk Accounts",
            str(
                stats.get(
                    "medium_risk_accounts",
                    0,
                )
            ),
        ],

        [
            "Multi-Hop Paths",
            str(
                stats.get(
                    "multi_hop_paths",
                    len(
                        result.get(
                            "multi_hop_paths",
                            [],
                        )
                    ),
                )
            ),
        ],
    ]

    statistics_table = Table(
        statistics_data,
        colWidths=[
            75 * mm,
            80 * mm,
        ],
    )

    statistics_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor(
                        "#17212b"
                    ),
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor(
                        "#d5dbe1"
                    ),
                ),

                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, -1),
                    colors.HexColor(
                        "#f7f9fb"
                    ),
                ),

                (
                    "FONTNAME",
                    (0, 1),
                    (0, -1),
                    "Helvetica-Bold",
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),

                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(
        statistics_table
    )

    # --------------------------------------------------------
    # Findings
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "4. Key Findings",
            heading_style,
        )
    )

    for finding in brief.get(
        "key_findings",
        [],
    ):

        story.append(
            Paragraph(
                f"• {finding}",
                body_style,
            )
        )

    # --------------------------------------------------------
    # Risk
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "5. Risk Assessment",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            brief.get(
                "risk_statement",
                "",
            ),
            body_style,
        )
    )

    risk_data = [
        [
            "Account",
            "Score",
            "Level",
            "Incoming",
            "Outgoing",
            "Pass-through",
        ]
    ]

    for account in result.get(
        "account_risk",
        [],
    ):

        risk_data.append(
            [
                str(
                    account.get(
                        "account",
                        "",
                    )
                ),

                str(
                    account.get(
                        "risk_score",
                        0,
                    )
                ),

                str(
                    account.get(
                        "risk_level",
                        "",
                    )
                ),

                format_inr(
                    account.get(
                        "incoming_amount",
                        0,
                    )
                ),

                format_inr(
                    account.get(
                        "outgoing_amount",
                        0,
                    )
                ),

                (
                    f"{float(account.get('pass_through_ratio', 0)) * 100:.0f}%"
                ),
            ]
        )

    if len(
        risk_data
    ) > 1:

        risk_table = Table(
            risk_data,
            repeatRows=1,
            colWidths=[
                30 * mm,
                17 * mm,
                20 * mm,
                27 * mm,
                27 * mm,
                28 * mm,
            ],
        )

        risk_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor(
                            "#17212b"
                        ),
                    ),

                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),

                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),

                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.HexColor(
                            "#d5dbe1"
                        ),
                    ),

                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        7.5,
                    ),

                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [
                            colors.white,
                            colors.HexColor(
                                "#f7f9fb"
                            ),
                        ],
                    ),

                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),

                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                ]
            )
        )

        story.append(
            risk_table
        )

    # --------------------------------------------------------
    # Financial flow
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "6. Financial Movement",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            brief.get(
                "money_flow_statement",
                "",
            ),
            body_style,
        )
    )

    for path in result.get(
        "multi_hop_paths",
        [],
    ):

        story.append(
            Paragraph(
                f"Fund path: {' → '.join(path)}",
                body_style,
            )
        )

    # --------------------------------------------------------
    # Timeline
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "7. Transaction Timeline",
            heading_style,
        )
    )

    timeline = prepare_timeline(
        result.get(
            "transactions",
            [],
        )
    )

    timeline_data = [
        [
            "Time",
            "Transaction",
            "Source",
            "Target",
            "Amount",
            "UPI",
        ]
    ]

    for event in timeline:

        timestamp = event.get(
            "timestamp",
            "",
        )

        try:

            timestamp = datetime.fromisoformat(
                str(timestamp)
            ).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        except Exception:

            pass

        timeline_data.append(
            [
                str(timestamp),

                str(
                    event.get(
                        "transaction_id",
                        "",
                    )
                ),

                str(
                    event.get(
                        "source",
                        "",
                    )
                ),

                str(
                    event.get(
                        "target",
                        "",
                    )
                ),

                format_inr(
                    event.get(
                        "amount",
                        0,
                    )
                ),

                str(
                    event.get(
                        "upi_id",
                        "",
                    )
                ),
            ]
        )

    if len(
        timeline_data
    ) > 1:

        timeline_table = Table(
            timeline_data,
            repeatRows=1,
            colWidths=[
                32 * mm,
                25 * mm,
                30 * mm,
                30 * mm,
                25 * mm,
                30 * mm,
            ],
        )

        timeline_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor(
                            "#17212b"
                        ),
                    ),

                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),

                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),

                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.HexColor(
                            "#d5dbe1"
                        ),
                    ),

                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),

                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [
                            colors.white,
                            colors.HexColor(
                                "#f7f9fb"
                            ),
                        ],
                    ),
                ]
            )
        )

        story.append(
            timeline_table
        )

    # --------------------------------------------------------
    # Actions
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "8. Recommended Investigative Actions",
            heading_style,
        )
    )

    for action in brief.get(
        "recommended_actions",
        [],
    ):

        story.append(
            Paragraph(
                f"• {action}",
                body_style,
            )
        )

    # --------------------------------------------------------
    # Evidence
    # --------------------------------------------------------

    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            "9. Evidence Integrity",
            heading_style,
        )
    )

    story.append(
        Paragraph(
            "SHA-256 hashes are included for verification "
            "of the submitted evidence files.",
            body_style,
        )
    )

    evidence_data = [
        [
            "File",
            "Rows",
            "SHA-256",
        ]
    ]

    for item in result.get(
        "evidence",
        [],
    ):

        evidence_data.append(
            [
                str(
                    item.get(
                        "filename",
                        "",
                    )
                ),

                str(
                    item.get(
                        "rows",
                        0,
                    )
                ),

                str(
                    item.get(
                        "sha256",
                        "",
                    )
                ),
            ]
        )

    if len(
        evidence_data
    ) > 1:

        evidence_table = Table(
            evidence_data,
            repeatRows=1,
            colWidths=[
                45 * mm,
                18 * mm,
                100 * mm,
            ],
        )

        evidence_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor(
                            "#17212b"
                        ),
                    ),

                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),

                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),

                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.HexColor(
                            "#d5dbe1"
                        ),
                    ),

                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        6.5,
                    ),

                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),

                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [
                            colors.white,
                            colors.HexColor(
                                "#f7f9fb"
                            ),
                        ],
                    ),
                ]
            )
        )

        story.append(
            evidence_table
        )

    # --------------------------------------------------------
    # AI limitations
    # --------------------------------------------------------

    ai_limitations = ai.get(
        "limitations",
        []
    )

    if ai_limitations:

        story.append(
            Spacer(
                1,
                12,
            )
        )

        story.append(
            Paragraph(
                "AI Limitations",
                heading_style,
            )
        )

        for limitation in ai_limitations:

            story.append(
                Paragraph(
                    f"• {limitation}",
                    small_style,
                )
            )

    # --------------------------------------------------------
    # Disclaimer
    # --------------------------------------------------------

    story.append(
        Spacer(
            1,
            15,
        )
    )

    story.append(
        Paragraph(
            "This report is an automated analytical aid. "
            "Findings should be validated against original "
            "evidence and applicable investigative procedures.",
            small_style,
        )
    )

    document.build(
        story
    )

    buffer.seek(0)

    return buffer.getvalue()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## ◈ Cyber Fraud Correlator"
    )

    st.caption(
        "Unified cyber fraud analysis & "
        "digital artifact correlation"
    )

    st.divider()

    backend_status = api_health()

    if backend_status:

        st.success(
            "Backend connected"
        )

    else:

        st.error(
            "Backend unavailable"
        )

        st.caption(
            "Start FastAPI with:\n\n"
            "`uvicorn backend.app.main:app --reload`"
        )

    st.divider()

    st.markdown(
        "### Evidence Ingestion"
    )

    uploaded_files = st.file_uploader(
        "Upload evidence files",
        type=[
            "csv",
            "xlsx",
            "xls",
            "json",
        ],
        accept_multiple_files=True,
    )

    analyze_button = st.button(
        "Analyze Evidence",
        type="primary",
        use_container_width=True,
        disabled=(
            not uploaded_files
            or not backend_status
        ),
    )

    st.divider()

    st.caption(
        "Artifact classes"
    )

    st.caption(
        "Telecom • Banking • UPI • Device • "
        "Network • Identity"
    )

    st.divider()

    st.caption(
        "Integrity: SHA-256"
    )

    st.caption(
        "Risk: Explainable"
    )

    st.caption(
        "AI: Evidence-grounded"
    )


# ============================================================
# RUN ANALYSIS
# ============================================================

if analyze_button:

    try:

        with st.spinner(
            "Correlating evidence..."
        ):

            analysis_result = send_analysis(
                uploaded_files
            )

            st.session_state[
                "analysis_result"
            ] = analysis_result

        st.success(
            "Investigation completed successfully."
        )

    except Exception as exc:

        st.error(
            str(exc)
        )


# ============================================================
# LOAD RESULT
# ============================================================

result = st.session_state.get(
    "analysis_result"
)


# ============================================================
# EMPTY STATE
# ============================================================

if not result:

    st.title(
        "Cyber Fraud Correlator"
    )

    st.caption(
        "AI-assisted unified cyber fraud analysis "
        "and digital artifact correlation"
    )

    st.divider()

    left, right = st.columns(
        [1.25, 1]
    )

    with left:

        st.header(
            "Investigation Workspace"
        )

        st.write(
            "Upload heterogeneous digital evidence "
            "and correlate identifiers, financial "
            "movement, device artifacts and "
            "transaction behavior into a unified "
            "investigation view."
        )

        st.info(
            "Upload evidence files from the sidebar "
            "to begin."
        )

    with right:

        st.header(
            "Analysis Pipeline"
        )

        pipeline = [
            "01  Evidence ingestion",
            "02  SHA-256 integrity verification",
            "03  Data normalization",
            "04  Entity resolution",
            "05  Cross-source graph correlation",
            "06  Financial flow reconstruction",
            "07  Multi-hop path detection",
            "08  Explainable risk scoring",
            "09  Investigation brief",
            "10  AI Investigator",
        ]

        for item in pipeline:

            st.write(
                f"**{item}**"
            )

    st.stop()


# ============================================================
# RESULT DATA
# ============================================================

evidence = result.get(
    "evidence",
    []
)

records = result.get(
    "records",
    0
)

links = result.get(
    "links",
    0
)

graph_data = result.get(
    "graph",
    {}
)

transactions = result.get(
    "transactions",
    []
)

flow_statistics = result.get(
    "flow_statistics",
    {}
)

multi_hop_paths = result.get(
    "multi_hop_paths",
    []
)

account_risk = result.get(
    "account_risk",
    []
)

brief = result.get(
    "investigation_brief",
    {}
)

ai_investigation = result.get(
    "ai_investigation",
    {}
)

high_risk = [
    account
    for account in account_risk
    if account.get(
        "risk_level"
    ) == "HIGH"
]

medium_risk = [
    account
    for account in account_risk
    if account.get(
        "risk_level"
    ) == "MEDIUM"
]


# ============================================================
# HEADER
# ============================================================

st.title(
    "Investigation Overview"
)

st.caption(
    "Unified cyber fraud analysis workspace"
)


# ============================================================
# METRICS
# ============================================================

metric1, metric2, metric3, metric4, metric5 = st.columns(
    5
)

with metric1:

    st.metric(
        "Evidence Files",
        len(evidence),
    )

with metric2:

    st.metric(
        "Records",
        format_number(records),
    )

with metric3:

    st.metric(
        "Entity Links",
        format_number(links),
    )

with metric4:

    st.metric(
        "Transactions",
        len(transactions),
    )

with metric5:

    st.metric(
        "Transaction Value",
        format_inr(
            flow_statistics.get(
                "total_value",
                0,
            )
        ),
    )


st.write("")


# ============================================================
# ALERT
# ============================================================

if high_risk:

    st.error(
        f"{len(high_risk)} high-risk account(s) "
        "detected by the explainable risk engine."
    )

elif medium_risk:

    st.warning(
        f"{len(medium_risk)} medium-risk account(s) "
        "require additional review."
    )

else:

    st.success(
        "No high-risk account was detected."
    )


# ============================================================
# TABS
# ============================================================

(
    summary_tab,
    timeline_tab,
    fund_tab,
    risk_tab,
    graph_tab,
    evidence_tab,
    export_tab,
) = st.tabs(
    [
        "Summary",
        "Timeline",
        "Fund Flow",
        "Risk Analysis",
        "Entity Graph",
        "Evidence",
        "Export",
    ]
)


# ============================================================
# SUMMARY
# ============================================================

with summary_tab:

    # --------------------------------------------------------
    # Automated brief
    # --------------------------------------------------------

    st.header(
        "Automated Investigation Brief"
    )

    with st.container(
        border=True
    ):

        st.subheader(
            "Case Assessment"
        )

        st.write(
            brief.get(
                "case_assessment",
                "No case assessment available.",
            )
        )

    st.write("")

    findings_col, actions_col = st.columns(
        2
    )

    with findings_col:

        with st.container(
            border=True
        ):

            st.subheader(
                "Key Findings"
            )

            findings = brief.get(
                "key_findings",
                []
            )

            for finding in findings:

                st.write(
                    f"• {finding}"
                )

    with actions_col:

        with st.container(
            border=True
        ):

            st.subheader(
                "Recommended Actions"
            )

            actions = brief.get(
                "recommended_actions",
                []
            )

            for action in actions:

                st.write(
                    f"→ {action}"
                )

    # --------------------------------------------------------
    # AI Investigator
    # --------------------------------------------------------

    st.write("")

    st.header(
        "AI Investigator Copilot"
    )

    provider = ai_investigation.get(
        "provider",
        "unknown",
    )

    model = ai_investigation.get(
        "model"
    )

    service_status = ai_investigation.get(
        "service_status",
        "",
    )

    if provider == "openai":

        if model:

            st.success(
                f"Evidence-grounded AI analysis · {model}"
            )

        else:

            st.success(
                "Evidence-grounded AI analysis"
            )

    else:

        st.warning(
            "AI provider unavailable — "
            "showing deterministic evidence-grounded analysis."
        )

    if service_status:

        st.caption(
            f"Service status: {service_status}"
        )

    priority = ai_investigation.get(
        "priority",
        "MEDIUM",
    )

    if priority == "HIGH":

        st.error(
            f"Investigation Priority: {priority}"
        )

    elif priority == "MEDIUM":

        st.warning(
            f"Investigation Priority: {priority}"
        )

    else:

        st.info(
            f"Investigation Priority: {priority}"
        )

    # --------------------------------------------------------
    # Narrative
    # --------------------------------------------------------

    with st.container(
        border=True
    ):

        st.subheader(
            "AI Case Assessment"
        )

        st.write(
            ai_investigation.get(
                "narrative",
                "No AI assessment available.",
            )
        )

    # --------------------------------------------------------
    # Leads
    # --------------------------------------------------------

    lead_accounts = ai_investigation.get(
        "lead_accounts",
        []
    )

    if lead_accounts:

        st.write("")

        st.subheader(
            "Priority Investigation Leads"
        )

        for lead in lead_accounts:

            with st.container(
                border=True
            ):

                c1, c2 = st.columns(
                    [1.4, 4]
                )

                with c1:

                    st.write(
                        f"**{lead.get('account', 'Unknown')}**"
                    )

                    st.caption(
                        f"Risk score: "
                        f"{lead.get('risk_score', 'N/A')}"
                    )

                with c2:

                    st.write(
                        lead.get(
                            "reason",
                            "",
                        )
                    )

                    for item in lead.get(
                        "evidence",
                        [],
                    ):

                        st.caption(
                            f"• {item}"
                        )

    # --------------------------------------------------------
    # Indicators
    # --------------------------------------------------------

    indicators = ai_investigation.get(
        "key_indicators",
        []
    )

    if indicators:

        st.write("")

        st.subheader(
            "Key AI Indicators"
        )

        for indicator in indicators:

            st.write(
                f"• {indicator}"
            )

    # --------------------------------------------------------
    # Questions
    # --------------------------------------------------------

    questions = ai_investigation.get(
        "investigation_questions",
        []
    )

    if questions:

        st.write("")

        st.subheader(
            "Questions for the Investigator"
        )

        for question in questions:

            st.write(
                f"→ {question}"
            )

    # --------------------------------------------------------
    # AI Actions
    # --------------------------------------------------------

    ai_actions = ai_investigation.get(
        "recommended_actions",
        []
    )

    if ai_actions:

        st.write("")

        st.subheader(
            "AI Recommended Actions"
        )

        for action in ai_actions:

            st.write(
                f"→ {action}"
            )

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    confidence = ai_investigation.get(
        "confidence"
    )

    if confidence:

        st.caption(
            f"AI confidence: {confidence}"
        )

    limitations = ai_investigation.get(
        "limitations",
        []
    )

    if limitations:

        with st.expander(
            "AI limitations and provenance"
        ):

            for limitation in limitations:

                st.write(
                    f"• {limitation}"
                )

    # --------------------------------------------------------
    # Existing analysis
    # --------------------------------------------------------

    st.write("")

    flow_col, risk_col = st.columns(
        2
    )

    with flow_col:

        with st.container(
            border=True
        ):

            st.subheader(
                "Financial Assessment"
            )

            st.write(
                brief.get(
                    "money_flow_statement",
                    "",
                )
            )

            st.metric(
                "Total Recorded Value",
                format_inr(
                    flow_statistics.get(
                        "total_value",
                        0,
                    )
                ),
            )

    with risk_col:

        with st.container(
            border=True
        ):

            st.subheader(
                "Risk Assessment"
            )

            st.write(
                brief.get(
                    "risk_statement",
                    "",
                )
            )

            r1, r2 = st.columns(
                2
            )

            with r1:

                st.metric(
                    "High Risk",
                    len(high_risk),
                )

            with r2:

                st.metric(
                    "Medium Risk",
                    len(medium_risk),
                )


# ============================================================
# TIMELINE
# ============================================================

with timeline_tab:

    st.header(
        "Investigation Timeline"
    )

    st.caption(
        "Chronological reconstruction of recorded financial movement"
    )

    show_timeline(
        transactions
    )

    timeline = prepare_timeline(
        transactions
    )

    rapid_count = 0

    for index in range(
        len(timeline) - 1
    ):

        first = timeline[index].get(
            "parsed"
        )

        second = timeline[index + 1].get(
            "parsed"
        )

        if first and second:

            seconds = (
                second - first
            ).total_seconds()

            if 0 <= seconds <= 600:

                rapid_count += 1

    st.divider()

    if rapid_count:

        st.warning(
            f"{rapid_count} consecutive transaction "
            "sequence(s) occurred within 10 minutes."
        )

    else:

        st.info(
            "No rapid transaction sequence was detected."
        )


# ============================================================
# FUND FLOW
# ============================================================

with fund_tab:

    st.header(
        "Financial Fund Flow"
    )

    st.caption(
        "Reconstructed movement of funds across accounts"
    )

    c1, c2, c3 = st.columns(
        3
    )

    with c1:

        st.metric(
            "Transactions",
            len(transactions),
        )

    with c2:

        st.metric(
            "Total Value",
            format_inr(
                flow_statistics.get(
                    "total_value",
                    0,
                )
            ),
        )

    with c3:

        st.metric(
            "Multi-hop Paths",
            len(multi_hop_paths),
        )

    st.write("")

    if transactions:

        flow_html = make_fund_flow_html(
            transactions
        )

        components_html(
            flow_html,
            height=590,
            scrolling=False,
        )

    st.divider()

    st.subheader(
        "Detected Multi-hop Paths"
    )

    for index, path in enumerate(
        multi_hop_paths,
        start=1,
    ):

        st.write(
            f"**Path {index}:** "
            f"{' → '.join(path)}"
        )


# ============================================================
# RISK
# ============================================================

with risk_tab:

    st.header(
        "Account Risk Analysis"
    )

    st.caption(
        "Explainable behavioral risk scoring"
    )

    c1, c2, c3 = st.columns(
        3
    )

    with c1:

        st.metric(
            "High Risk",
            len(high_risk),
        )

    with c2:

        st.metric(
            "Medium Risk",
            len(medium_risk),
        )

    with c3:

        st.metric(
            "Accounts Analyzed",
            len(account_risk),
        )

    st.write("")

    risk_rows = []

    for account in account_risk:

        risk_rows.append(
            {
                "Account": account.get(
                    "account",
                    "",
                ),

                "Risk Score": account.get(
                    "risk_score",
                    0,
                ),

                "Risk Level": account.get(
                    "risk_level",
                    "",
                ),

                "Incoming": format_inr(
                    account.get(
                        "incoming_amount",
                        0,
                    )
                ),

                "Outgoing": format_inr(
                    account.get(
                        "outgoing_amount",
                        0,
                    )
                ),

                "Pass-through": (
                    f"{float(account.get('pass_through_ratio', 0)) * 100:.0f}%"
                ),

                "Rapid Forwarding": (
                    "Yes"
                    if account.get(
                        "rapid_forwarding"
                    )
                    else "No"
                ),

                "Reasons": "; ".join(
                    account.get(
                        "reasons",
                        [],
                    )
                ),
            }
        )

    if risk_rows:

        st.dataframe(
            pd.DataFrame(
                risk_rows
            ),
            use_container_width=True,
            hide_index=True,
        )

    st.write("")

    st.subheader(
        "Why Accounts Were Flagged"
    )

    for account in account_risk:

        with st.container(
            border=True
        ):

            c1, c2, c3 = st.columns(
                [2, 1, 4]
            )

            with c1:

                st.write(
                    f"**{account.get('account')}**"
                )

            with c2:

                st.write(
                    f"{account.get('risk_level')} "
                    f"· "
                    f"{account.get('risk_score')}/100"
                )

            with c3:

                st.caption(
                    " • ".join(
                        account.get(
                            "reasons",
                            [],
                        )
                    )
                )


# ============================================================
# ENTITY GRAPH
# ============================================================

with graph_tab:

    st.header(
        "Entity Correlation Graph"
    )

    st.caption(
        "Cross-source relationships between digital artifacts"
    )

    nodes = graph_data.get(
        "nodes",
        []
    )

    edges = graph_data.get(
        "edges",
        []
    )

    c1, c2 = st.columns(
        2
    )

    with c1:

        st.metric(
            "Graph Nodes",
            len(nodes),
        )

    with c2:

        st.metric(
            "Graph Relationships",
            len(edges),
        )

    st.write("")

    if nodes:

        try:

            graph_html = make_graph_html(
                graph_data
            )

            components_html(
                graph_html,
                height=680,
                scrolling=False,
            )

        except Exception as exc:

            st.error(
                f"Could not render entity graph: {exc}"
            )


# ============================================================
# EVIDENCE
# ============================================================

with evidence_tab:

    st.header(
        "Evidence Integrity"
    )

    st.caption(
        "Submitted artifacts and SHA-256 verification hashes"
    )

    evidence_rows = []

    for item in evidence:

        evidence_rows.append(
            {
                "File": item.get(
                    "filename",
                    "",
                ),

                "Rows": item.get(
                    "rows",
                    0,
                ),

                "SHA-256": item.get(
                    "sha256",
                    "",
                ),

                "Columns": ", ".join(
                    item.get(
                        "columns",
                        [],
                    )
                ),
            }
        )

    if evidence_rows:

        st.dataframe(
            pd.DataFrame(
                evidence_rows
            ),
            use_container_width=True,
            hide_index=True,
        )

    st.write("")

    for item in evidence:

        with st.container(
            border=True
        ):

            st.write(
                f"**{item.get('filename', '')}**"
            )

            st.code(
                item.get(
                    "sha256",
                    "",
                ),
                language="text",
            )


# ============================================================
# EXPORT
# ============================================================

with export_tab:

    st.header(
        "Case Export"
    )

    st.caption(
        "Generate a portable investigative package"
    )

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    st.subheader(
        "Investigation Report"
    )

    try:

        pdf_bytes = build_pdf_report(
            result
        )

        st.download_button(
            label="Download Investigation Report",
            data=pdf_bytes,
            file_name=(
                "cyber_fraud_investigation_report.pdf"
            ),
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )

    except Exception as exc:

        st.error(
            f"Could not generate PDF: {exc}"
        )

    st.write("")

    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    st.subheader(
        "Machine-readable Case Data"
    )

    json_bytes = json.dumps(
        result,
        indent=2,
        default=str,
    ).encode(
        "utf-8"
    )

    st.download_button(
        label="Download Analysis JSON",
        data=json_bytes,
        file_name=(
            "cyber_fraud_analysis.json"
        ),
        mime="application/json",
        use_container_width=True,
    )

    st.write("")

    # --------------------------------------------------------
    # AI Investigator export preview
    # --------------------------------------------------------

    st.subheader(
        "AI Investigator Assessment"
    )

    provider = ai_investigation.get(
        "provider",
        "unknown"
    )

    model = ai_investigation.get(
        "model"
    )

    service_status = ai_investigation.get(
        "service_status",
        ""
    )

    priority = ai_investigation.get(
        "priority",
        "MEDIUM"
    )

    confidence = ai_investigation.get(
        "confidence",
        "N/A"
    )

    if provider == "openai":

        if model:

            st.success(
                f"AI provider: OpenAI · Model: {model}"
            )

        else:

            st.success(
                "AI provider: OpenAI"
            )

    else:

        st.warning(
            "AI provider unavailable — "
            "showing deterministic evidence-grounded analysis."
        )

    if service_status:

        st.caption(
            f"Service status: {service_status}"
        )

    c1, c2 = st.columns(
        2
    )

    with c1:

        st.metric(
            "Investigation Priority",
            priority
        )

    with c2:

        st.metric(
            "Confidence",
            confidence
        )

    st.write("")

    with st.container(
        border=True
    ):

        st.markdown(
            "### Investigation Narrative"
        )

        st.write(
            ai_investigation.get(
                "narrative",
                "No investigation narrative available."
            )
        )

    lead_accounts = ai_investigation.get(
        "lead_accounts",
        []
    )

    if lead_accounts:

        st.write("")

        st.markdown(
            "### Priority Investigation Leads"
        )

        for lead in lead_accounts:

            account = lead.get(
                "account",
                "Unknown"
            )

            risk_score = lead.get(
                "risk_score",
                "N/A"
            )

            reason = lead.get(
                "reason",
                ""
            )

            evidence_items = lead.get(
                "evidence",
                []
            )

            with st.container(
                border=True
            ):

                col1, col2 = st.columns(
                    [1.5, 4]
                )

                with col1:

                    st.write(
                        f"**{account}**"
                    )

                    st.caption(
                        f"Risk score: {risk_score}/100"
                    )

                with col2:

                    st.write(
                        reason
                    )

                    for evidence_item in evidence_items:

                        st.caption(
                            f"• {evidence_item}"
                        )

    indicators = ai_investigation.get(
        "key_indicators",
        []
    )

    if indicators:

        st.write("")

        st.markdown(
            "### Key Indicators"
        )

        for indicator in indicators:

            st.write(
                f"• {indicator}"
            )

    questions = ai_investigation.get(
        "investigation_questions",
        []
    )

    if questions:

        st.write("")

        st.markdown(
            "### Investigation Questions"
        )

        for question in questions:

            st.write(
                f"→ {question}"
            )

    ai_actions = ai_investigation.get(
        "recommended_actions",
        []
    )

    if ai_actions:

        st.write("")

        st.markdown(
            "### Recommended Actions"
        )

        for action in ai_actions:

            st.write(
                f"→ {action}"
            )

    limitations = ai_investigation.get(
        "limitations",
        []
    )

    if limitations:

        st.write("")

        with st.expander(
            "AI limitations and provenance"
        ):

            for limitation in limitations:

                st.write(
                    f"• {limitation}"
                )

    st.write("")

    with st.expander(
        "View raw AI response JSON"
    ):

        st.json(
            ai_investigation
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Cyber Fraud Correlator • Evidence-grounded "
    "digital artifact correlation • SHA-256 integrity • "
    "Explainable risk analysis • AI Investigator"
)