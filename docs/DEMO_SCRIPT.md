# Three-minute demo script

1. **0:00–0:20 — framing.** “This offline-first tool triages a fraud case in the golden hour. It preserves an SHA-256 fingerprint before parsing anything.”
2. **0:20–0:45 — ingest.** Start the API and dashboard. Upload `data/mock/bank_transactions.csv`, `telecom.csv`, `device.csv`, and `upi.csv`; click **Analyze evidence**. Point out the generated case ID.
3. **0:45–1:10 — integrity.** Open **Evidence**. Show the hash per original file and the ordered case-chain hash. Explain that these fingerprints make later tampering detectable.
4. **1:10–1:40 — entity correlation.** Open **Digital evidence relationship graph**. Highlight the two phone numbers sharing IMEI `356789012345678`, IP `10.10.10.21`, and MAC address. State that these are reviewable links, not an automatic accusation.
5. **1:40–2:10 — mule trail.** Open **Financial fund flow**. Follow VIC-001 through the accounts to the cash-out side. Show the multi-hop path.
6. **2:10–2:35 — risk explanation.** Open **Account risk analysis**. Select a high-risk intermediary and read the pass-through and rapid-forwarding indicators.
7. **2:35–3:00 — field handover.** Open **Investigation export**, download the JSON and prepare the one-page PDF. Conclude: “The officer receives provenance, leads, money movement, and immediate preservation recommendations in one place.”
