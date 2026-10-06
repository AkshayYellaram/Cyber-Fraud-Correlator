# 🛡️ Cyber Fraud Correlator

### AI-Powered Unified Cyber Fraud Analysis & Digital Artifact Correlator

**Cyber Fraud Investigation** · **Digital Artifact Correlation** · **Entity Resolution** · **Risk Analysis**

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-150458?style=for-the-badge&logo=pandas)
![NetworkX](https://img.shields.io/badge/NetworkX-Graph%20Analysis-orange?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?style=for-the-badge&logo=streamlit)
![SHA-256](https://img.shields.io/badge/SHA--256-Evidence%20Integrity-black?style=for-the-badge)

---

## 🚨 Overview

**Cyber Fraud Correlator** is a screening-round proof-of-concept for analyzing and correlating cyber-fraud evidence from multiple digital sources.

The system converts fragmented evidence into a structured investigation workflow by combining:

- 📂 Multi-source evidence ingestion
- 🧹 Data normalization
- 🔗 Entity resolution
- 🕸️ Relationship graph analysis
- 💰 Fund-flow reconstruction
- ⚠️ Explainable risk scoring
- 🔐 Evidence integrity verification
- 📄 Investigation report generation

### Core Investigation Pipeline

```text
📂 Evidence
     │
     ▼
🔐 SHA-256 + Case Chain
     │
     ▼
📑 Parsing
     │
     ▼
🧹 Normalization
     │
     ▼
🔗 Entity Resolution
     │
     ▼
🕸️ Relationship Graph
     │
     ▼
⚠️ Risk Scoring
     │
     ▼
📄 PDF / JSON Investigation Brief
```

> **Important:** Correlation is an investigative lead, not a finding of guilt. Generated leads should be validated against the original preserved evidence before operational action.

---

## ✨ Key Features

### 📂 Multi-Source Evidence Ingestion

The prototype accepts multiple evidence formats:

- CSV
- XLS / XLSX
- JSON
- TXT / LOG
- `.eml` headers

Different source headings can be mapped into a common investigation schema.

### 🔗 Entity Resolution

The system identifies deterministic relationships using shared identifiers such as:

- 📱 Phone
- 📟 IMEI
- 📡 IMSI
- 🌐 IP
- 💻 MAC
- 💳 UPI
- 🏦 Account identifiers

### 🕸️ Graph Correlation

Connected entities are represented as a directed relationship graph, allowing investigators to explore relationships across multiple evidence sources.

### 💰 Fund-Flow Reconstruction

The prototype can reconstruct victim-to-mule-to-cash-out transaction paths and identify multi-hop movement.

Example:

```text
Victim
  │
  ▼
Mule Account
  │
  ▼
Intermediate Account
  │
  ▼
Cash-Out Account
```

### ⚠️ Explainable Risk Scoring

Risk indicators are generated from observable behaviours such as:

- Pass-through behaviour
- Rapid forwarding
- Transaction velocity

### 🔐 Evidence Integrity

Each evidence file can be fingerprinted using **SHA-256**, with an ordered case-chain hash maintained for the investigation.

---

## 🔍 Investigation Workflow

The system is designed around a simple investigative workflow:

```text
                 ┌──────────────────┐
                 │ Multiple Sources │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │     Parsing      │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │  Normalization   │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Entity Resolution│
                 └────────┬─────────┘
                          │
                    ┌─────┴─────┐
                    ▼           ▼
                 🕸️ Graph    💰 Fund Flow
                    │           │
                    └─────┬─────┘
                          ▼
                  ⚠️ Risk Scoring
                          │
                    ┌─────┴─────┐
                    ▼           ▼
                 📄 PDF       📦 JSON
```

---

## 🕸️ Entity Correlation

A major part of the prototype is connecting identifiers that appear across different evidence sources.

For example:

```text
🏦 Banking Record
       │
       │ Account
       ▼
👤 Entity
       │
       │ Phone
       ▼
📱 Telecom Record
       │
       │ IMEI
       ▼
📟 Device
       │
       │ IP
       ▼
🌐 Network Artifact
```

This allows an investigator to move between related records instead of analyzing every file independently.

---

## 💰 Fund-Flow Analysis

The system supports directed fund-flow reconstruction and multi-hop analysis.

Example:

```text
┌─────────────┐
│    Victim   │
└──────┬──────┘
       │
       │ Transaction
       ▼
┌─────────────┐
│ Mule Account│
└──────┬──────┘
       │
       │ Forwarded
       ▼
┌─────────────┐
│ Intermediate│
│   Account   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Cash-Out   │
└─────────────┘
```

The prototype can use transaction relationships and observed behaviour to generate explainable risk indicators.

---

## 🔐 Evidence Integrity

Evidence integrity is handled using **SHA-256 fingerprints**.

```text
Evidence File
      │
      ▼
   SHA-256
      │
      ▼
File Fingerprint
      │
      ▼
Ordered Case Chain
```

Case files are stored inside a unique local case directory.

This provides an integrity-oriented record of the evidence used during an investigation.

---

## 📄 Investigation Outputs

The prototype produces two primary forms of output.

### 📦 JSON Export

Structured investigation data suitable for further processing or integration.

### 📄 PDF Field Brief

A one-page, officer-facing investigation brief containing relevant findings and risk indicators.

---

## 🖥️ Dashboard

The project includes a lightweight **Streamlit dashboard** designed for field-officer use.

The dashboard provides an interface for:

- Uploading evidence
- Processing investigation data
- Reviewing correlations
- Exploring suspicious relationships
- Reviewing risk indicators
- Preparing investigation outputs

### Dashboard Preview

> 📸 Add a screenshot of the dashboard here.

For example:

```text
docs/
└── dashboard.png
```

Then add:

```markdown
![Cyber Fraud Correlator Dashboard](docs/dashboard.png)
```

---

## 🏗️ Technology Architecture

```text
                 ┌───────────────────────┐
                 │     Evidence Files    │
                 │ CSV XLSX JSON LOG EML │
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │       FastAPI         │
                 │     Backend / API     │
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │  Pandas Normalization │
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │   Entity Resolution   │
                 └───────────┬───────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │ NetworkX Graph Layer  │
                 └───────────┬───────────┘
                             │
                   ┌─────────┴─────────┐
                   ▼                   ▼
             Risk Scoring          Fund Flow
                   │                   │
                   └─────────┬─────────┘
                             ▼
                 ┌───────────────────────┐
                 │ Investigation Output │
                 │      PDF / JSON      │
                 └───────────────────────┘
```

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| **Python** | Core application |
| **FastAPI** | Backend / REST API |
| **Pandas** | Data normalization |
| **NetworkX** | Relationship graph |
| **Streamlit** | Field-officer dashboard |
| **SQLite** | Local evidence metadata |
| **SHA-256** | Evidence integrity |
| **Report Generation** | PDF investigation brief |

---

## 📂 Supported Evidence

| Format | Example Use |
|---|---|
| CSV | Banking / transaction records |
| XLS / XLSX | Spreadsheet evidence |
| JSON | Structured digital artifacts |
| TXT / LOG | Logs and textual evidence |
| `.eml` | Email header analysis |

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/AkshayYellaram/Cyber-Fraud-Correlator.git
cd Cyber-Fraud-Correlator
```

Create a virtual environment:

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Prototype

### Start the FastAPI backend

```bash
uvicorn backend.app.main:app --reload
```

### Start the Streamlit dashboard

```bash
streamlit run dashboard/app.py
```

### Local Endpoints

| Component | Address |
|---|---|
| Backend | `http://127.0.0.1:8000` |
| API Docs | `http://127.0.0.1:8000/docs` |
| Dashboard | `http://localhost:8501` |

---

## 🧪 Demo Data

For the demonstration workflow, upload the files located in:

```text
data/mock/
```

The sample data demonstrates:

- A four-hop banking fund-flow chain
- Shared IMEI correlations
- Shared IP correlations
- Shared MAC correlations

---

## 🏆 Screening-Round Prototype

This project was developed as a **screening-round proof of concept** focused on demonstrating how fragmented cyber-fraud evidence can be transformed into an investigation-oriented view.

### Demonstration Flow

```text
Evidence
   ↓
Integrity Verification
   ↓
Parsing
   ↓
Normalization
   ↓
Correlation
   ↓
Graph Analysis
   ↓
Risk Indicators
   ↓
Investigation Brief
```

### Hackathon Material

- [📘 Technical Proposal](docs/TECHNICAL_PROPOSAL.md)
- [🎬 Three-Minute Demonstration Script](docs/DEMO_SCRIPT.md)

---

## ⚠️ Investigation Disclaimer

**Cyber Fraud Correlator is an investigative assistance prototype.**

A correlation, relationship, or risk score produced by the system should **not** be interpreted as proof of fraud or guilt.

All generated leads should be validated against the original preserved evidence before operational, disciplinary, or legal action.

---

## 🔭 Future Improvements

Potential improvements include:

- [ ] Interactive investigation graph
- [ ] Advanced entity-resolution techniques
- [ ] Timeline-based evidence visualization
- [ ] Additional forensic artifact formats
- [ ] Improved transaction anomaly detection
- [ ] Automated case-report customization
- [ ] Advanced investigator workflow
- [ ] Additional correlation rules

---

## 👨‍💻 Author

### Akshay Yellaram

**Cybersecurity & IoT Student**

Cybersecurity · Digital Forensics · AI/ML · Blockchain · Ethical Hacking

⭐ If you find this project useful or interesting, consider giving the repository a star.
