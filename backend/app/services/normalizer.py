from __future__ import annotations

from email import policy
from email.parser import BytesParser
from pathlib import Path
import json
import re

import pandas as pd


# ============================================================
# COLUMN ALIASES
# ============================================================

COLUMN_ALIASES = {

    "phone": "phone",
    "phone_number": "phone",
    "mobile": "phone",
    "mobile_number": "phone",
    "msisdn": "phone",

    "upi": "upi_id",
    "upi_id": "upi_id",
    "beneficiary_upi": "upi_id",
    "vpa": "upi_id",

    "account": "account_id",
    "account_number": "account_id",
    "bank_account": "account_id",
    "beneficiary_account": "account_id",

    "sender": "sender_account",
    "sender_account": "sender_account",
    "source_account": "sender_account",
    "from_account": "sender_account",

    "receiver": "receiver_account",
    "receiver_account": "receiver_account",
    "destination_account": "receiver_account",
    "to_account": "receiver_account",

    "imei": "imei",
    "imei_number": "imei",

    "imsi": "imsi",
    "imsi_number": "imsi",

    "ip": "ip",
    "ip_address": "ip",

    "mac": "mac",
    "mac_address": "mac",

    "timestamp": "timestamp",
    "time": "timestamp",
    "datetime": "timestamp",
    "date_time": "timestamp",

    "amount": "amount",
    "transaction_amount": "amount",
    "value": "amount",

    "transaction_id": "transaction_id",
    "txn_id": "transaction_id",
    "transaction": "transaction_id",
}


# ============================================================
# NORMALIZE COLUMNS
# ============================================================

def normalize_columns(
    df: pd.DataFrame
) -> pd.DataFrame:

    renamed = {}


    for column in df.columns:

        key = (
            str(column)
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )


        renamed[column] = COLUMN_ALIASES.get(
            key,
            key,
        )


    df = df.rename(
        columns=renamed
    ).copy()


    # ========================================================
    # IDENTITY FIELDS
    # ========================================================

    identity_fields = [

        "phone",
        "upi_id",
        "account_id",
        "sender_account",
        "receiver_account",
        "imei",
        "imsi",
        "ip",
        "mac",

    ]


    for field in identity_fields:

        if field in df.columns:

            df[field] = (
                df[field]
                .astype(str)
                .str.strip()
                .str.lower()
            )


    # ========================================================
    # AMOUNT
    # ========================================================

    if "amount" in df.columns:

        df["amount"] = (
            df["amount"]
            .astype(str)
            .str.replace(
                ",",
                "",
                regex=False,
            )
            .str.replace(
                "₹",
                "",
                regex=False,
            )
            .str.strip()
        )


        df["amount"] = pd.to_numeric(
            df["amount"],
            errors="coerce",
        )


    # ========================================================
    # TIMESTAMP
    # ========================================================

    if "timestamp" in df.columns:

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce",
        )


    return df


# ============================================================
# LOAD FILE
# ============================================================

IP_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
UPI_PATTERN = re.compile(r"\b[\w.+-]{2,}@[\w.-]{2,}\b")


def _email_dataframe(path: str) -> pd.DataFrame:
    """Preserve email headers as a single evidentiary record and extract observables."""
    with open(path, "rb") as source:
        message = BytesParser(policy=policy.default).parse(source)
    received = "\n".join(message.get_all("Received", []))
    headers = "\n".join(f"{key}: {value}" for key, value in message.items())
    ip_match = IP_PATTERN.search(received) or IP_PATTERN.search(headers)
    # A subject explicitly naming UPI/VPA is more probative than an address in
    # From/To. Fall back to other headers only when no subject value exists.
    subject = str(message.get("Subject", ""))
    upi_match = UPI_PATTERN.search(subject) or UPI_PATTERN.search(headers)
    return pd.DataFrame([{
        "email_from": str(message.get("From", "")),
        "email_to": str(message.get("To", "")),
        "email_subject": str(message.get("Subject", "")),
        "timestamp": message.get("Date", ""),
        "ip": ip_match.group(0) if ip_match else None,
        "upi_id": upi_match.group(0) if upi_match else None,
        "email_message_id": str(message.get("Message-ID", "")),
    }])


def load_file(path: str) -> pd.DataFrame:
    """Load common telecom, banking, device-log, and email artefacts."""
    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(path)
    elif suffix in (".xlsx", ".xls"):
        df = pd.read_excel(path)
    elif suffix == ".json":
        with open(path, encoding="utf-8") as source:
            payload = json.load(source)
        df = pd.json_normalize(payload if isinstance(payload, list) else [payload])
    elif suffix in (".txt", ".log"):
        try:
            df = pd.read_csv(path, sep=None, engine="python")
        except (UnicodeDecodeError, pd.errors.ParserError):
            content = Path(path).read_text(encoding="utf-8", errors="replace")
            pairs = [dict(re.findall(r"([\w.-]+)=([^\s,;]+)", line)) for line in content.splitlines() if "=" in line]
            df = pd.DataFrame(pairs or [{"raw_log": content}])
    elif suffix == ".eml":
        df = _email_dataframe(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Use CSV, Excel, JSON, TXT/LOG, or EML.")
    return normalize_columns(df)
