import json
import os
from datetime import datetime
from typing import Any, Dict

from openai import OpenAI


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6-luna",
)


# ============================================================
# OPENAI CLIENT
# ============================================================

def get_client():
    """
    Create an OpenAI client if an API key is available.

    The API key is intentionally read from the environment
    instead of being hard-coded into the project.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return None

    return OpenAI(
        api_key=api_key
    )


# ============================================================
# HELPERS
# ============================================================

def safe_json(data: Any) -> str:
    """
    Convert Python data to readable JSON.
    """

    return json.dumps(
        data,
        indent=2,
        default=str,
    )


def calculate_total_value(transactions):
    """
    Calculate total transaction value.
    """

    return sum(
        float(
            transaction.get(
                "amount",
                0,
            ) or 0
        )
        for transaction in transactions
    )


def detect_rapid_sequences(transactions):
    """
    Detect consecutive transactions occurring
    within ten minutes.
    """

    parsed = []

    for transaction in transactions:

        timestamp = transaction.get(
            "timestamp"
        )

        if not timestamp:
            continue

        try:

            parsed.append(
                (
                    datetime.fromisoformat(
                        str(timestamp)
                    ),
                    transaction,
                )
            )

        except Exception:
            continue

    parsed.sort(
        key=lambda item: item[0]
    )

    rapid_sequences = []

    for index in range(
        len(parsed) - 1
    ):

        current_time = parsed[index][0]
        next_time = parsed[index + 1][0]

        difference = (
            next_time - current_time
        ).total_seconds()

        if 0 <= difference <= 600:

            rapid_sequences.append(
                {
                    "first_transaction": parsed[index][1].get(
                        "transaction_id"
                    ),
                    "second_transaction": parsed[index + 1][1].get(
                        "transaction_id"
                    ),
                    "time_difference_seconds": difference,
                }
            )

    return rapid_sequences


# ============================================================
# DETERMINISTIC FALLBACK
# ============================================================

def build_fallback_copilot(
    result: Dict[str, Any],
    fallback_reason: str = "no_api_key",
) -> Dict[str, Any]:
    """
    Deterministic investigation assistant.

    This is intentionally NOT described as generative AI.
    """

    account_risk = result.get(
        "account_risk",
        []
    )

    transactions = result.get(
        "transactions",
        []
    )

    multi_hop_paths = result.get(
        "multi_hop_paths",
        []
    )

    investigation_brief = result.get(
        "investigation_brief",
        {}
    )

    # --------------------------------------------------------
    # Risk classification
    # --------------------------------------------------------

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

    if high_risk:
        priority = "HIGH"

    elif medium_risk:
        priority = "MEDIUM"

    else:
        priority = "LOW"

    # --------------------------------------------------------
    # Lead accounts
    # --------------------------------------------------------

    lead_accounts = []

    for account in high_risk[:5]:

        incoming = float(
            account.get(
                "incoming_amount",
                0,
            ) or 0
        )

        outgoing = float(
            account.get(
                "outgoing_amount",
                0,
            ) or 0
        )

        pass_through = float(
            account.get(
                "pass_through_ratio",
                0,
            ) or 0
        )

        reasons = account.get(
            "reasons",
            []
        )

        lead_accounts.append(
            {
                "account": account.get(
                    "account",
                    "Unknown",
                ),

                "risk_score": account.get(
                    "risk_score",
                    0,
                ),

                "reason": (
                    "; ".join(
                        reasons
                    )
                    or "Account requires review."
                ),

                "evidence": [
                    (
                        f"Incoming amount: "
                        f"₹{incoming:,.0f}"
                    ),

                    (
                        f"Outgoing amount: "
                        f"₹{outgoing:,.0f}"
                    ),

                    (
                        f"Pass-through ratio: "
                        f"{pass_through * 100:.0f}%"
                    ),
                ],
            }
        )

    # --------------------------------------------------------
    # Key indicators
    # --------------------------------------------------------

    key_indicators = []

    if high_risk:

        key_indicators.append(
            f"{len(high_risk)} account(s) "
            "were classified as HIGH risk "
            "by the deterministic risk engine."
        )

    if multi_hop_paths:

        longest_path = max(
            multi_hop_paths,
            key=len,
            default=[],
        )

        if longest_path:

            key_indicators.append(
                "Longest observed financial path: "
                f"{' → '.join(longest_path)}"
            )

    rapid_sequences = detect_rapid_sequences(
        transactions
    )

    if rapid_sequences:

        key_indicators.append(
            f"{len(rapid_sequences)} transaction "
            "sequence(s) occurred within 10 minutes."
        )

    high_pass_through = [
        account
        for account in account_risk
        if float(
            account.get(
                "pass_through_ratio",
                0,
            ) or 0
        ) >= 0.70
    ]

    if high_pass_through:

        key_indicators.append(
            f"{len(high_pass_through)} account(s) "
            "show a pass-through ratio of at least 70%."
        )

    # --------------------------------------------------------
    # Narrative
    # --------------------------------------------------------

    total_value = calculate_total_value(
        transactions
    )

    narrative = (
        "The deterministic investigation analyzed "
        f"{len(transactions)} transaction(s) representing "
        f"₹{total_value:,.0f} in recorded value."
    )

    if multi_hop_paths:

        longest_path = max(
            multi_hop_paths,
            key=len,
            default=[],
        )

        if longest_path:

            narrative += (
                " The longest observed financial sequence "
                "is "
                f"{' → '.join(longest_path)}."
            )

    # --------------------------------------------------------
    # Investigation questions
    # --------------------------------------------------------

    investigation_questions = [
        "Who controls the intermediary accounts?",
        "Why were the funds forwarded so rapidly?",
        "Are the same device or network identifiers associated with multiple identities?",
        "Can the UPI identifiers be independently verified against the original evidence?",
        "Does the transaction timing match the reported fraud event timeline?",
    ]

    # --------------------------------------------------------
    # Recommended actions
    # --------------------------------------------------------

    recommended_actions = [
        "Validate the high-risk accounts against the original financial evidence.",
        "Trace the longest detected fund-flow path.",
        "Cross-check correlated phone, IMEI, IMSI, IP and MAC identifiers.",
        "Review rapid transaction sequences against the known incident timeline.",
    ]

    # --------------------------------------------------------
    # Correct service status
    # --------------------------------------------------------

    if fallback_reason == "no_api_key":

        provider = "deterministic_fallback"

        model = None

        limitations = [
            "No OPENAI_API_KEY was configured.",
            "The investigation shown here was generated by the deterministic correlation and risk engines.",
        ]

        service_status = "API key not configured"

    elif fallback_reason == "quota":

        provider = "openai_unavailable"

        model = DEFAULT_MODEL

        limitations = [
            "OpenAI API was reached successfully but the API account has no available credits/quota.",
            "The investigation shown here was generated by the deterministic correlation and risk engines.",
        ]

        service_status = "OpenAI API quota exhausted"

    elif fallback_reason == "api_error":

        provider = "openai_unavailable"

        model = DEFAULT_MODEL

        limitations = [
            "The OpenAI API request could not be completed.",
            "The investigation shown here was generated by the deterministic correlation and risk engines.",
        ]

        service_status = "OpenAI API unavailable"

    else:

        provider = "deterministic_fallback"

        model = None

        limitations = [
            "The generative AI investigation was not available.",
            "The investigation shown here was generated by the deterministic correlation and risk engines.",
        ]

        service_status = "Deterministic fallback"

    return {
        "provider": provider,

        "model": model,

        "service_status": service_status,

        "priority": priority,

        "narrative": narrative,

        "lead_accounts": lead_accounts,

        "key_indicators": key_indicators,

        "investigation_questions": investigation_questions,

        "recommended_actions": recommended_actions,

        "confidence": "MEDIUM",

        "limitations": limitations,
    }


# ============================================================
# OPENAI INVESTIGATOR
# ============================================================

def run_ai_investigator(
    result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Run the OpenAI investigation assistant.

    If OpenAI cannot be used, automatically return
    a deterministic investigation instead.
    """

    client = get_client()

    # --------------------------------------------------------
    # No API key
    # --------------------------------------------------------

    if client is None:

        return build_fallback_copilot(
            result,
            fallback_reason="no_api_key",
        )

    # --------------------------------------------------------
    # Extract analysis context
    # --------------------------------------------------------

    evidence = result.get(
        "evidence",
        []
    )

    transactions = result.get(
        "transactions",
        []
    )

    account_risk = result.get(
        "account_risk",
        []
    )

    multi_hop_paths = result.get(
        "multi_hop_paths",
        []
    )

    graph = result.get(
        "graph",
        {}
    )

    investigation_brief = result.get(
        "investigation_brief",
        {}
    )

    graph_nodes = graph.get(
        "nodes",
        []
    )

    graph_edges = graph.get(
        "edges",
        []
    )

    # --------------------------------------------------------
    # Limit graph context
    # --------------------------------------------------------

    graph_context = {
        "node_count": len(
            graph_nodes
        ),

        "edge_count": len(
            graph_edges
        ),

        "nodes": graph_nodes[:100],

        "edges": graph_edges[:150],
    }

    # --------------------------------------------------------
    # Complete AI context
    # --------------------------------------------------------

    context = {

        "evidence": evidence,

        "transactions": transactions,

        "account_risk": account_risk,

        "multi_hop_paths": multi_hop_paths,

        "graph": graph_context,

        "investigation_brief": investigation_brief,
    }

    # --------------------------------------------------------
    # System instructions
    # --------------------------------------------------------

    system_prompt = """
You are an AI Investigation Assistant inside a
cyber fraud analysis platform.

Your job is to analyze ONLY the structured evidence
and deterministic analytical results supplied by the
application.

IMPORTANT RULES:

1. Never invent an account, person, device,
   transaction, relationship, timestamp or event.

2. Never state that a person is definitely a criminal.

3. Distinguish clearly between:
   - observed evidence
   - analytical indicators
   - investigative hypotheses

4. Risk scores are indicators requiring review.
   They are NOT proof of fraud.

5. Explain why an account or relationship deserves
   investigative review.

6. Prefer exact identifiers, transaction IDs and
   timestamps supplied in the evidence.

7. Do not make unsupported assumptions about intent.

8. If the evidence is insufficient, explicitly say so.

9. Recommended actions should be validation,
   correlation or investigative steps.

10. Do not invent missing evidence.

11. Keep the response concise and useful to a
    cyber-fraud investigator.

12. Return ONLY valid JSON.

The JSON must contain exactly:

{
  "priority": "HIGH | MEDIUM | LOW",

  "narrative": "Evidence-grounded explanation.",

  "lead_accounts": [
    {
      "account": "account identifier",
      "reason": "why the account deserves review",
      "evidence": [
        "specific evidence item"
      ]
    }
  ],

  "key_indicators": [
    "indicator"
  ],

  "investigation_questions": [
    "question"
  ],

  "recommended_actions": [
    "action"
  ],

  "confidence": "HIGH | MEDIUM | LOW",

  "limitations": [
    "limitation"
  ]
}
"""

    # --------------------------------------------------------
    # User prompt
    # --------------------------------------------------------

    user_prompt = f"""
Analyze the following cyber-fraud investigation.

STRUCTURED ANALYSIS:

{safe_json(context)}

Produce ONLY the required JSON.

Remember:

- Do not invent facts.
- Risk is an indicator, not proof.
- Ground every statement in supplied data.
- Do not identify a person as a criminal.
- Distinguish evidence from hypotheses.
- State important limitations.
"""

    # --------------------------------------------------------
    # OpenAI request
    # --------------------------------------------------------

    try:

        response = client.responses.create(
            model=DEFAULT_MODEL,
            instructions=system_prompt,
            input=user_prompt,
        )

        raw_text = response.output_text

        # ----------------------------------------------------
        # Parse JSON
        # ----------------------------------------------------

        try:

            parsed = json.loads(
                raw_text
            )

        except json.JSONDecodeError:

            return {
                "provider": "openai",

                "model": DEFAULT_MODEL,

                "service_status": "OpenAI returned non-JSON output",

                "priority": "MEDIUM",

                "narrative": raw_text,

                "lead_accounts": [],

                "key_indicators": [],

                "investigation_questions": [],

                "recommended_actions": [],

                "confidence": "LOW",

                "limitations": [
                    "The model returned non-JSON output."
                ],
            }

        # ----------------------------------------------------
        # Add provider metadata
        # ----------------------------------------------------

        parsed["provider"] = "openai"

        parsed["model"] = DEFAULT_MODEL

        parsed["service_status"] = "OpenAI investigation completed"

        return parsed

    # --------------------------------------------------------
    # API failure
    # --------------------------------------------------------

    except Exception as exc:

        error_text = str(
            exc
        ).lower()

        # ----------------------------------------------------
        # Quota / credit error
        # ----------------------------------------------------

        if (
            "insufficient_quota"
            in error_text
            or "credit_balance_exhausted"
            in error_text
            or "quota" in error_text
            or "credits" in error_text
        ):

            fallback = build_fallback_copilot(
                result,
                fallback_reason="quota",
            )

            fallback["limitations"].insert(
                0,
                (
                    "OpenAI API returned a quota/credit "
                    "error. No generative AI response was "
                    "available for this analysis."
                ),
            )

            return fallback

        # ----------------------------------------------------
        # Other API errors
        # ----------------------------------------------------

        fallback = build_fallback_copilot(
            result,
            fallback_reason="api_error",
        )

        fallback["limitations"].insert(
            0,
            (
                "OpenAI API request failed: "
                f"{str(exc)}"
            ),
        )

        return fallback