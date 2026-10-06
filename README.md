# AI-Powered Unified Cyber Fraud Analysis & Digital Artifact Correlator

Screening-round PoC.

## MVP pipeline
Evidence -> SHA-256 + case chain -> Parsing -> Normalization -> Entity Resolution -> Graph -> Risk Scoring -> JSON/PDF brief

## What the prototype demonstrates
- Multi-source ingestion: CSV, XLS/XLSX, JSON, TXT/LOG, and `.eml` headers.
- Flexible source headings mapped into a common investigation schema.
- Deterministic, explainable links for shared phone, IMEI, IMSI, IP, MAC, UPI, and account identifiers.
- Directed victim-to-mule-to-cash-out fund-flow reconstruction and multi-hop detection.
- Explainable risk scoring for pass-through behaviour, rapid forwarding, and transaction velocity.
- Per-file SHA-256 fingerprints plus an ordered case-chain hash; case files are stored in a unique local case folder.
- Officer-facing, one-page PDF field brief and full JSON export.

> Correlation is an investigative lead, not a finding of guilt. Validate all generated leads against original preserved evidence before operational action.

## Stack
- FastAPI: backend/API
- Pandas: CSV/XLSX normalization
- NetworkX: relationship graph
- Streamlit: lightweight field-officer dashboard
- SQLite: local/offline evidence metadata
- SHA-256: evidence integrity

## Run
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt

uvicorn backend.app.main:app --reload
streamlit run dashboard/app.py
```

Backend: http://127.0.0.1:8000
API docs: http://127.0.0.1:8000/docs
Dashboard: http://localhost:8501

## Hackathon material
- [Technical proposal](docs/TECHNICAL_PROPOSAL.md)
- [Three-minute demonstration script](docs/DEMO_SCRIPT.md)

For a reliable demo, upload every file in `data/mock/`. The sample banking data creates a four-hop fund-flow chain; the telecom/device data creates shared IMEI/IP/MAC correlations.
