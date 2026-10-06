import pandas as pd


# ============================================================
# EXTRACT TRANSACTIONS
# ============================================================

def extract_transactions(
    dataframes
):

    transactions = []


    for source_name, df in dataframes:

        if "amount" not in df.columns:
            continue


        if (
            "sender_account" not in df.columns
            or
            "receiver_account" not in df.columns
        ):
            continue


        for row_index, row in df.iterrows():

            sender = row.get(
                "sender_account"
            )

            receiver = row.get(
                "receiver_account"
            )

            amount = row.get(
                "amount"
            )

            timestamp = row.get(
                "timestamp"
            )


            if pd.isna(amount):
                continue


            if pd.isna(sender):
                continue


            if pd.isna(receiver):
                continue


            try:

                amount = float(
                    amount
                )

            except (
                ValueError,
                TypeError,
            ):

                continue


            sender = (
                str(sender)
                .strip()
                .lower()
            )


            receiver = (
                str(receiver)
                .strip()
                .lower()
            )


            if not sender or not receiver:
                continue


            transaction_id = row.get(
                "transaction_id"
            )


            if pd.isna(transaction_id):

                transaction_id = (
                    f"{source_name}:{row_index}"
                )

            else:

                transaction_id = (
                    str(transaction_id)
                    .strip()
                )


            if pd.isna(timestamp):

                timestamp_value = None

            else:

                timestamp_value = str(
                    timestamp
                )


            upi_id = row.get(
                "upi_id"
            )


            if pd.isna(upi_id):

                upi_value = None

            else:

                upi_value = (
                    str(upi_id)
                    .strip()
                    .lower()
                )


            transactions.append(
                {
                    "transaction_id": transaction_id,

                    "timestamp": timestamp_value,

                    "sender_account": sender,

                    "receiver_account": receiver,

                    "amount": amount,

                    "upi_id": upi_value,

                    "evidence_source": source_name,
                }
            )


    return transactions


# ============================================================
# FUND FLOW
# ============================================================

def build_fund_flow_graph(
    transactions
):

    flow = []


    for transaction in transactions:

        sender = transaction[
            "sender_account"
        ]

        receiver = transaction[
            "receiver_account"
        ]


        if not sender or not receiver:
            continue


        flow.append(
            {
                "source": sender,

                "target": receiver,

                "amount": transaction[
                    "amount"
                ],

                "timestamp": transaction[
                    "timestamp"
                ],

                "transaction_id": transaction[
                    "transaction_id"
                ],

                "upi_id": transaction[
                    "upi_id"
                ],

                "evidence_source": transaction[
                    "evidence_source"
                ],
            }
        )


    return flow


# ============================================================
# STATISTICS
# ============================================================

def calculate_flow_statistics(
    transactions
):

    if not transactions:

        return {
            "transaction_count": 0,
            "total_value": 0,
            "average_value": 0,
            "max_value": 0,
        }


    amounts = [
        transaction["amount"]
        for transaction in transactions
    ]


    total = sum(
        amounts
    )


    return {

        "transaction_count": len(
            transactions
        ),

        "total_value": total,

        "average_value": (
            total
            / len(transactions)
        ),

        "max_value": max(
            amounts
        ),
    }


# ============================================================
# MULTI-HOP PATHS
# ============================================================

def find_multi_hop_paths(
    transactions,
    max_hops=5,
):

    graph = {}


    for transaction in transactions:

        sender = transaction[
            "sender_account"
        ]

        receiver = transaction[
            "receiver_account"
        ]


        if not sender or not receiver:
            continue


        graph.setdefault(
            sender,
            []
        ).append(
            receiver
        )


    paths = []


    def dfs(
        current,
        path,
    ):

        if len(path) >= max_hops:

            paths.append(
                path.copy()
            )

            return


        next_nodes = graph.get(
            current,
            []
        )


        if not next_nodes:

            if len(path) >= 3:

                paths.append(
                    path.copy()
                )

            return


        for next_node in next_nodes:

            if next_node in path:
                continue


            dfs(
                next_node,
                path + [
                    next_node
                ],
            )


    for start_node in graph:

        dfs(
            start_node,
            [start_node],
        )


    unique_paths = []

    seen = set()


    for path in paths:

        key = tuple(
            path
        )


        if key in seen:
            continue


        seen.add(
            key
        )


        unique_paths.append(
            path
        )


    return unique_paths