from datetime import datetime


# ============================================================
# TIMESTAMP PARSER
# ============================================================

def parse_timestamp(value):

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    formats = [

        "%Y-%m-%d %H:%M:%S",

        "%Y-%m-%d %H:%M",

        "%d-%m-%Y %H:%M:%S",

        "%d-%m-%Y %H:%M",

        "%Y/%m/%d %H:%M:%S",

        "%Y/%m/%d %H:%M",

    ]


    for fmt in formats:

        try:

            return datetime.strptime(
                text,
                fmt,
            )

        except ValueError:

            continue


    return None


# ============================================================
# ACCOUNT RISK ANALYSIS
# ============================================================

def analyze_accounts(
    transactions
):

    accounts = {}


    # ========================================================
    # BUILD ACCOUNT ACTIVITY
    # ========================================================

    for transaction in transactions:

        sender = transaction.get(
            "sender_account"
        )

        receiver = transaction.get(
            "receiver_account"
        )

        amount = transaction.get(
            "amount",
            0,
        )

        try:

            amount = float(amount)

        except (
            TypeError,
            ValueError,
        ):

            amount = 0.0


        timestamp = parse_timestamp(
            transaction.get(
                "timestamp"
            )
        )


        # ----------------------------------------------------
        # SENDER
        # ----------------------------------------------------

        if sender:

            if sender not in accounts:

                accounts[sender] = {
                    "incoming": [],
                    "outgoing": [],
                }


            accounts[sender][
                "outgoing"
            ].append(
                {
                    "amount": amount,
                    "timestamp": timestamp,
                }
            )


        # ----------------------------------------------------
        # RECEIVER
        # ----------------------------------------------------

        if receiver:

            if receiver not in accounts:

                accounts[receiver] = {
                    "incoming": [],
                    "outgoing": [],
                }


            accounts[receiver][
                "incoming"
            ].append(
                {
                    "amount": amount,
                    "timestamp": timestamp,
                }
            )


    results = []


    # ========================================================
    # ANALYZE EACH ACCOUNT
    # ========================================================

    for account, data in accounts.items():

        incoming = data[
            "incoming"
        ]

        outgoing = data[
            "outgoing"
        ]


        incoming_count = len(
            incoming
        )

        outgoing_count = len(
            outgoing
        )


        incoming_amount = sum(
            item["amount"]
            for item in incoming
        )


        outgoing_amount = sum(
            item["amount"]
            for item in outgoing
        )


        transaction_count = (
            incoming_count
            + outgoing_count
        )


        # ====================================================
        # PASS-THROUGH RATIO
        # ====================================================

        if incoming_amount > 0:

            pass_through_ratio = (
                outgoing_amount
                / incoming_amount
            )

        else:

            pass_through_ratio = 0.0


        # ====================================================
        # RAPID FORWARDING
        # ====================================================

        rapid_forwarding = False


        for incoming_tx in incoming:

            incoming_time = (
                incoming_tx["timestamp"]
            )


            if not incoming_time:
                continue


            for outgoing_tx in outgoing:

                outgoing_time = (
                    outgoing_tx["timestamp"]
                )


                if not outgoing_time:
                    continue


                difference = (
                    outgoing_time
                    - incoming_time
                ).total_seconds()


                if (
                    difference >= 0
                    and difference <= 600
                ):

                    rapid_forwarding = True

                    break


            if rapid_forwarding:
                break


        # ====================================================
        # RISK SCORE
        # ====================================================

        score = 0

        reasons = []


        if incoming_count > 0:

            score += 10

            reasons.append(
                "Receives funds"
            )


        if outgoing_count > 0:

            score += 10

            reasons.append(
                "Forwards funds"
            )


        if (
            incoming_amount > 0
            and pass_through_ratio >= 0.70
        ):

            score += 25

            reasons.append(
                "High pass-through ratio"
            )


        if rapid_forwarding:

            score += 25

            reasons.append(
                "Rapid forwarding of received funds"
            )


        if transaction_count >= 3:

            score += 15

            reasons.append(
                "High transaction activity"
            )


        score = min(
            score,
            100,
        )


        # ====================================================
        # RISK LEVEL
        # ====================================================

        if score >= 70:

            risk_level = "HIGH"

        elif score >= 40:

            risk_level = "MEDIUM"

        else:

            risk_level = "LOW"


        results.append(
            {
                "account": account,

                "risk_score": score,

                "risk_level": risk_level,

                "incoming_count": incoming_count,

                "outgoing_count": outgoing_count,

                "incoming_amount": incoming_amount,

                "outgoing_amount": outgoing_amount,

                "pass_through_ratio": round(
                    pass_through_ratio,
                    2,
                ),

                "rapid_forwarding": rapid_forwarding,

                "reasons": reasons,
            }
        )


    # ========================================================
    # SORT
    # ========================================================

    results.sort(
        key=lambda item: item[
            "risk_score"
        ],
        reverse=True,
    )


    return results