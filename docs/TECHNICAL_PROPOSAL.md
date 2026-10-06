# Technical proposal — Cyber Fraud Correlator

## Objective

The Cyber Fraud Correlator is an offline-first triage system for the reporting “golden hour”. It turns telecom, banking/UPI, device-log, JSON, text-log and email-header artefacts into explainable entity links, a directed money trail and a concise investigator brief. It does not make a guilt determination: every generated link is a reviewable lead with its originating evidence retained.

## Architecture and ingestion pipeline

```text
Original artefacts
  └─ SHA-256 per file + ordered case-chain hash
       └─ Parser (CSV/XLSX/JSON/TXT/LOG/EML)
            └─ Canonical schema + source metadata
                 ├─ deterministic entity resolver ──► evidence/entity graph
                 └─ transaction extractor ──────────► directed fund-flow graph
                                                        └─ explainable risk rules
                                                             └─ JSON + one-page PDF brief
```

The FastAPI service stores each upload in a uniquely identified case folder and records the original filename, SHA-256, parsed row count, fields, and cumulative chain hash. A subsequent hash check can prove whether an original artefact has changed. The app enforces a 50 MB per-file limit and accepts only the documented formats.

Normalization maps common source headings (`MSISDN`, `VPA`, `beneficiary_account`, `from_account`, `IP Address`) to a canonical schema. Source-specific columns remain available so an investigator can trace a conclusion back to the source. Email parsing preserves key headers and extracts IP/UPI observables. Android and app dumps can be loaded as delimited data or `key=value` logs.

## Graph modelling and correlation

The entity graph has two node classes: evidence records and entities. Entity nodes include phone/MSISDN, IMEI, IMSI, IP address, MAC address, UPI ID and bank account. An evidence-to-entity edge means the original record contains that value; entity-to-entity co-occurrence edges retain the record that supplied the relationship. This gives officers a direct audit path rather than an opaque similarity score.

The money graph is deliberately separate and directed. A bank/UPI transaction is an edge from sender account to receiver account with amount, time, UPI handle, transaction ID and source file. Depth-first traversal surfaces chains of three or more accounts, including victim → mule → onward/cash-out patterns.

## Risk and safeguards

Risk is transparent and configurable. The prototype scores accounts for receiving and forwarding funds, pass-through ratio of at least 70%, forwarding within ten minutes, and high transaction activity. The dashboard displays every reason for a score. Identical values are deterministic correlations, not proof of identity: shared identifiers, graph clusters and risk scores must be validated against the preserved originals before a freeze, seizure, arrest, or court filing.

The solution is designed for a normal police workstation: Python, FastAPI, Pandas, NetworkX, Streamlit and local files only. No cloud inference, model API, or external database is required.

## Demonstration dataset and success criteria

Use the provided mock records. `bank_transactions.csv` produces the four-hop trail VIC-001 → acct-1001 → acct-1002 → acct-1003 → acct-1004. The telecom/device files demonstrate common IMEI, IP and MAC across distinct phone numbers. Success is measured by: accepted source types, reproducible hashes, correctly surfaced shared values, legible directed graph, explainable high-risk mule scoring, and JSON/PDF exports suitable for field handover.
