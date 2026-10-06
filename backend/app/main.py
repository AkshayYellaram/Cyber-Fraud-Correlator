from pathlib import Path
import shutil

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
)

from .utils.hash_utils import sha256_file

from .services.normalizer import load_file

from .services.entity_resolution import (
    build_entity_links,
)

from .services.graph import (
    build_entity_graph,
    graph_json,
)

from .services.fund_flow import (
    extract_transactions,
    build_fund_flow_graph,
    calculate_flow_statistics,
    find_multi_hop_paths,
)

from .services.risk_engine import (
    analyze_accounts,
)

from .services.investigation_assistant import (
    build_investigation_brief,
)

from .services.ai_investigator import (
    run_ai_investigator,
)


# ============================================================
# PATHS
# ============================================================

BASE = Path(__file__).resolve().parents[2]

UPLOAD_DIR = (
    BASE
    / "data"
    / "uploads"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Cyber Fraud Correlator",
    version="0.3.0",
    description=(
        "AI-assisted unified cyber fraud analysis "
        "and digital artifact correlation platform."
    ),
)


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "cyber-fraud-correlator",
        "version": "0.3.0",
    }


# ============================================================
# INGEST
# ============================================================

@app.post("/ingest")
async def ingest(
    files: list[UploadFile] = File(...)
):
    """
    Complete investigation pipeline.

    Evidence
        ↓
    SHA-256
        ↓
    Parsing
        ↓
    Normalization
        ↓
    Entity Resolution
        ↓
    Entity Graph
        ↓
    Transaction Extraction
        ↓
    Fund Flow
        ↓
    Multi-hop Detection
        ↓
    Risk Analysis
        ↓
    Investigation Brief
        ↓
    AI Investigator
    """

    if not files:

        raise HTTPException(
            status_code=400,
            detail="No evidence files were supplied.",
        )

    dataframes = []

    evidence = []

    records = []

    # ========================================================
    # 1. INGEST EVIDENCE
    # ========================================================

    for upload in files:

        if not upload.filename:
            continue

        safe_name = Path(
            upload.filename
        ).name

        destination = (
            UPLOAD_DIR
            / safe_name
        )

        # ----------------------------------------------------
        # Save file
        # ----------------------------------------------------

        try:

            with destination.open(
                "wb"
            ) as output:

                shutil.copyfileobj(
                    upload.file,
                    output,
                )

        except Exception as exc:

            raise HTTPException(
                status_code=500,
                detail=(
                    f"Could not save "
                    f"{safe_name}: {exc}"
                ),
            )

        # ----------------------------------------------------
        # SHA-256
        # ----------------------------------------------------

        try:

            digest = sha256_file(
                str(destination)
            )

        except Exception as exc:

            raise HTTPException(
                status_code=500,
                detail=(
                    f"Could not hash "
                    f"{safe_name}: {exc}"
                ),
            )

        # ----------------------------------------------------
        # Parse
        # ----------------------------------------------------

        try:

            df = load_file(
                str(destination)
            )

        except Exception as exc:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Could not parse "
                    f"{safe_name}: {exc}"
                ),
            )

        dataframes.append(
            (
                safe_name,
                df,
            )
        )

        evidence.append(
            {
                "filename": safe_name,
                "sha256": digest,
                "rows": len(df),
                "columns": list(
                    df.columns
                ),
            }
        )

    # ========================================================
    # 2. ENTITY RESOLUTION
    # ========================================================

    try:

        records, links = build_entity_links(
            dataframes
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Entity resolution failed: "
                f"{exc}"
            ),
        )

    # ========================================================
    # 3. ENTITY GRAPH
    # ========================================================

    try:

        entity_graph = build_entity_graph(
            dataframes
        )

        entity_graph_data = graph_json(
            entity_graph
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Entity graph generation failed: "
                f"{exc}"
            ),
        )

    # ========================================================
    # 4. TRANSACTION EXTRACTION
    # ========================================================

    try:

        transactions = extract_transactions(
            dataframes
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Transaction extraction failed: "
                f"{exc}"
            ),
        )

    # ========================================================
    # 5. FUND FLOW
    # ========================================================

    try:

        fund_flow = build_fund_flow_graph(
            transactions
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Fund-flow graph generation failed: "
                f"{exc}"
            ),
        )

    # ========================================================
    # 6. FLOW STATISTICS
    # ========================================================

    try:

        flow_statistics = calculate_flow_statistics(
            transactions
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Fund-flow statistics failed: "
                f"{exc}"
            ),
        )

    # ========================================================
    # 7. MULTI-HOP PATHS
    # ========================================================

    try:

        multi_hop_paths = find_multi_hop_paths(
            transactions,
            max_hops=5,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Multi-hop path detection failed: "
                f"{exc}"
            ),
        )

    # ========================================================
    # 8. ACCOUNT RISK
    # ========================================================

    try:

        account_risk = analyze_accounts(
            transactions
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Account risk analysis failed: "
                f"{exc}"
            ),
        )

    # ========================================================
    # 9. INVESTIGATION BRIEF
    # ========================================================

    try:

        investigation_brief = (
            build_investigation_brief(
                evidence=evidence,
                records=len(records),
                links=len(links),
                graph_data=entity_graph_data,
                transactions=transactions,
                flow_statistics=flow_statistics,
                multi_hop_paths=multi_hop_paths,
                account_risk=account_risk,
            )
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Investigation brief generation failed: "
                f"{exc}"
            ),
        )

    # ========================================================
    # 10. STRUCTURED RESULT FOR AI
    # ========================================================

    analysis_result = {
        "evidence": evidence,
        "records": len(records),
        "links": len(links),
        "graph": entity_graph_data,
        "transactions": transactions,
        "fund_flow": fund_flow,
        "flow_statistics": flow_statistics,
        "multi_hop_paths": multi_hop_paths,
        "account_risk": account_risk,
        "investigation_brief": investigation_brief,
    }

    # ========================================================
    # 11. AI INVESTIGATOR
    # ========================================================

    try:

        ai_investigation = run_ai_investigator(
            analysis_result
        )

    except Exception as exc:

        # The core investigation must never fail just
        # because the AI layer has an issue.

        ai_investigation = {
            "provider": "unavailable",
            "model": None,
            "priority": "MEDIUM",
            "narrative": (
                "The deterministic investigation completed, "
                "but the AI Investigator could not be executed."
            ),
            "lead_accounts": [],
            "key_indicators": [],
            "investigation_questions": [],
            "recommended_actions": [],
            "confidence": "LOW",
            "limitations": [
                str(exc)
            ],
        }

    # ========================================================
    # 12. FINAL RESPONSE
    # ========================================================

    return {
        "evidence": evidence,

        "records": len(records),

        "links": len(links),

        "graph": entity_graph_data,

        "transactions": transactions,

        "fund_flow": fund_flow,

        "flow_statistics": flow_statistics,

        "multi_hop_paths": multi_hop_paths,

        "account_risk": account_risk,

        "investigation_brief": investigation_brief,

        "ai_investigation": ai_investigation,
    }