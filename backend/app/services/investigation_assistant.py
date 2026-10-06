from typing import Any, Dict, List
from datetime import datetime


def format_inr(value: float) -> str:
    """
    Format a numeric value as Indian Rupees.
    """

    try:
        value = float(value)
    except (ValueError, TypeError):
        value = 0.0

    return f"₹{value:,.0f}"


def get_high_risk_accounts(
    account_risk: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Return accounts classified as HIGH risk.
    """

    return [
        account
        for account in account_risk
        if account.get("risk_level") == "HIGH"
    ]


def get_medium_risk_accounts(
    account_risk: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Return accounts classified as MEDIUM risk.
    """

    return [
        account
        for account in account_risk
        if account.get("risk_level") == "MEDIUM"
    ]


def detect_rapid_transactions(
    transactions: List[Dict[str, Any]],
    window_seconds: int = 600,
) -> List[Dict[str, Any]]:
    """
    Detect consecutive transactions occurring within the
    configured time window.

    Default window = 10 minutes.
    """

    if not transactions:
        return []

    parsed_transactions = []

    for transaction in transactions:
        timestamp = transaction.get("timestamp")

        if not timestamp:
            continue

        try:
            parsed_time = datetime.fromisoformat(
                str(timestamp)
            )

            parsed_transactions.append(
                (
                    parsed_time,
                    transaction
                )
            )

        except (ValueError, TypeError):
            continue

    parsed_transactions.sort(
        key=lambda item: item[0]
    )

    rapid_sequences = []

    for index in range(len(parsed_transactions) - 1):

        current_time, current_transaction = (
            parsed_transactions[index]
        )

        next_time, next_transaction = (
            parsed_transactions[index + 1]
        )

        difference = (
            next_time - current_time
        ).total_seconds()

        if 0 <= difference <= window_seconds:

            rapid_sequences.append(
                {
                    "from_transaction": current_transaction.get(
                        "transaction_id"
                    ),
                    "to_transaction": next_transaction.get(
                        "transaction_id"
                    ),
                    "delay_seconds": difference,
                    "from_account": current_transaction.get(
                        "receiver_account"
                    ),
                    "to_account": next_transaction.get(
                        "receiver_account"
                    ),
                }
            )

    return rapid_sequences


def build_money_flow_statement(
    transactions: List[Dict[str, Any]],
    multi_hop_paths: List[List[str]],
) -> str:
    """
    Generate a human-readable explanation of the
    financial movement.
    """

    if not transactions:
        return (
            "No financial transactions were available "
            "for correlation."
        )

    total_value = sum(
        float(transaction.get("amount", 0) or 0)
        for transaction in transactions
    )

    statement = (
        f"The dataset contains {len(transactions)} "
        f"financial transactions with a combined "
        f"recorded value of {format_inr(total_value)}."
    )

    if multi_hop_paths:

        longest_path = max(
            multi_hop_paths,
            key=len,
            default=[]
        )

        if longest_path:

            hops = len(longest_path) - 1

            statement += (
                f" The longest detected fund-flow path "
                f"contains {hops} transfer hop(s): "
                f"{' → '.join(longest_path)}."
            )

    return statement


def build_risk_statement(
    account_risk: List[Dict[str, Any]]
) -> str:
    """
    Generate an explanation of the automated risk results.
    """

    if not account_risk:
        return (
            "No account-level risk assessment "
            "was generated."
        )

    high = get_high_risk_accounts(
        account_risk
    )

    medium = get_medium_risk_accounts(
        account_risk
    )

    statement = (
        f"The automated risk engine identified "
        f"{len(high)} high-risk account(s) and "
        f"{len(medium)} medium-risk account(s)."
    )

    if high:

        highest = max(
            high,
            key=lambda item: item.get(
                "risk_score",
                0
            )
        )

        statement += (
            f" The highest-risk account is "
            f"{highest.get('account')} with a "
            f"risk score of "
            f"{highest.get('risk_score')}/100."
        )

    return statement


def build_entity_statement(
    graph_data: Dict[str, Any]
) -> str:
    """
    Explain the entity correlation graph.
    """

    nodes = graph_data.get(
        "nodes",
        []
    )

    edges = graph_data.get(
        "edges",
        []
    )

    if not nodes:
        return (
            "No entity graph relationships "
            "were generated."
        )

    entity_nodes = [
        node
        for node in nodes
        if node.get("node_type") != "evidence"
    ]

    return (
        f"The correlation graph contains "
        f"{len(entity_nodes)} resolved entity "
        f"node(s) connected through "
        f"{len(edges)} relationship edge(s). "
        f"These relationships allow identifiers "
        f"appearing across different evidence "
        f"sources to be examined as a connected case."
    )


def build_key_findings(
    transactions: List[Dict[str, Any]],
    account_risk: List[Dict[str, Any]],
    multi_hop_paths: List[List[str]],
    graph_data: Dict[str, Any],
) -> List[str]:
    """
    Generate the main investigative findings.
    """

    findings = []

    high = get_high_risk_accounts(
        account_risk
    )

    # Finding 1: high-risk accounts
    if high:

        findings.append(
            f"{len(high)} account(s) were classified "
            f"as HIGH risk by the explainable "
            f"risk engine."
        )

    # Finding 2: multi-hop fund movement
    if multi_hop_paths:

        longest_path = max(
            multi_hop_paths,
            key=len,
            default=[]
        )

        if len(longest_path) >= 3:

            findings.append(
                f"A multi-hop financial path was "
                f"identified: "
                f"{' → '.join(longest_path)}."
            )

    # Finding 3: rapid forwarding
    rapid_sequences = detect_rapid_transactions(
        transactions
    )

    if rapid_sequences:

        findings.append(
            f"{len(rapid_sequences)} transaction "
            f"sequence(s) show fund movement "
            f"within 10 minutes."
        )

    # Finding 4: high pass-through accounts
    pass_through_accounts = []

    for account in account_risk:

        ratio = account.get(
            "pass_through_ratio",
            0
        )

        if ratio >= 0.70:

            pass_through_accounts.append(
                account
            )

    if pass_through_accounts:

        findings.append(
            f"{len(pass_through_accounts)} account(s) "
            f"show a pass-through ratio of at least "
            f"70%, indicating that a large proportion "
            f"of received funds were subsequently "
            f"forwarded."
        )

    # Finding 5: cross-source entity correlation
    entity_nodes = [
        node
        for node in graph_data.get(
            "nodes",
            []
        )
        if node.get("node_type") != "evidence"
    ]

    if entity_nodes:

        findings.append(
            f"{len(entity_nodes)} normalized entities "
            f"were correlated across the submitted "
            f"evidence."
        )

    # Fallback
    if not findings:

        findings.append(
            "No major automated investigative finding "
            "was generated from the available evidence."
        )

    return findings


def build_recommended_actions(
    transactions: List[Dict[str, Any]],
    account_risk: List[Dict[str, Any]],
    multi_hop_paths: List[List[str]],
    links: int,
) -> List[str]:
    """
    Generate investigator-oriented next actions.
    """

    actions = []

    high = get_high_risk_accounts(
        account_risk
    )

    if high:

        actions.append(
            "Prioritize review of high-risk accounts "
            "and inspect their incoming and outgoing "
            "transaction relationships."
        )

    if multi_hop_paths:

        longest_path = max(
            multi_hop_paths,
            key=len,
            default=[]
        )

        if longest_path:

            actions.append(
                "Trace the longest detected fund-flow "
                "path and validate each intermediary "
                "account against the original evidence."
            )

    if links:

        actions.append(
            "Cross-check correlated phone, IMEI, IMSI, "
            "IP, MAC, UPI and account identifiers "
            "against their original evidence files."
        )

    rapid_sequences = detect_rapid_transactions(
        transactions
    )

    if rapid_sequences:

        actions.append(
            "Review rapid transaction sequences and "
            "determine whether the timing is consistent "
            "with automated or coordinated fund movement."
        )

    if not actions:

        actions.append(
            "Review the source evidence manually and "
            "add additional artifacts if available."
        )

    return actions


def build_investigation_brief(
    evidence: List[Dict[str, Any]],
    records: int,
    links: int,
    graph_data: Dict[str, Any],
    transactions: List[Dict[str, Any]],
    flow_statistics: Dict[str, Any],
    multi_hop_paths: List[List[str]],
    account_risk: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Build the complete automated investigation brief.

    This is intentionally evidence-grounded:
    the assistant only describes patterns already
    detected by the analysis pipeline.
    """

    high = get_high_risk_accounts(
        account_risk
    )

    medium = get_medium_risk_accounts(
        account_risk
    )

    total_value = flow_statistics.get(
        "total_value",
        0
    )

    # -----------------------------
    # Case assessment
    # -----------------------------

    if high and multi_hop_paths:

        highest = max(
            high,
            key=lambda item: item.get(
                "risk_score",
                0
            )
        )

        case_assessment = (
            "The submitted evidence contains multiple "
            "correlated indicators requiring investigation. "
            f"{len(high)} account(s) were classified as "
            f"high risk and {len(multi_hop_paths)} "
            f"multi-hop financial path(s) were detected. "
            f"The strongest automated investigative lead "
            f"is {highest.get('account')}."
        )

    elif high:

        highest = max(
            high,
            key=lambda item: item.get(
                "risk_score",
                0
            )
        )

        case_assessment = (
            "The submitted evidence contains account-level "
            "risk indicators requiring investigation. "
            f"{len(high)} account(s) were classified as "
            f"high risk. The strongest automated lead is "
            f"{highest.get('account')}."
        )

    elif medium:

        case_assessment = (
            "The submitted evidence contains indicators "
            "requiring further review. "
            f"{len(medium)} account(s) were classified "
            f"as medium risk."
        )

    else:

        case_assessment = (
            "The current evidence does not produce a "
            "high-confidence automated fraud indicator."
        )

    # -----------------------------
    # Key findings
    # -----------------------------

    key_findings = build_key_findings(
        transactions=transactions,
        account_risk=account_risk,
        multi_hop_paths=multi_hop_paths,
        graph_data=graph_data,
    )

    # -----------------------------
    # Recommended actions
    # -----------------------------

    recommended_actions = build_recommended_actions(
        transactions=transactions,
        account_risk=account_risk,
        multi_hop_paths=multi_hop_paths,
        links=links,
    )

    # -----------------------------
    # Final result
    # -----------------------------

    return {
        "title": "Automated Investigation Brief",

        "case_assessment": case_assessment,

        "money_flow_statement": build_money_flow_statement(
            transactions=transactions,
            multi_hop_paths=multi_hop_paths,
        ),

        "risk_statement": build_risk_statement(
            account_risk=account_risk,
        ),

        "entity_statement": build_entity_statement(
            graph_data=graph_data,
        ),

        "key_findings": key_findings,

        "recommended_actions": recommended_actions,

        "statistics": {
            "evidence_files": len(evidence),
            "records": records,
            "entity_links": links,
            "transactions": len(transactions),
            "total_value": total_value,
            "high_risk_accounts": len(high),
            "medium_risk_accounts": len(medium),
            "multi_hop_paths": len(multi_hop_paths),
            "graph_nodes": len(
                graph_data.get(
                    "nodes",
                    []
                )
            ),
            "graph_edges": len(
                graph_data.get(
                    "edges",
                    []
                )
            ),
        },
    }