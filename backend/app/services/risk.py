def score_record(record, links_for_record=0, multi_hop=False, high_velocity=False):
    score = 0
    reasons = []

    if links_for_record >= 2:
        score += 20
        reasons.append("Multiple cross-source entity links")
    if links_for_record >= 4:
        score += 15
        reasons.append("Dense identity/device correlation")
    if multi_hop:
        score += 25
        reasons.append("Multi-hop fund movement")
    if high_velocity:
        score += 20
        reasons.append("High transaction velocity")

    score = min(score, 100)
    level = "LOW" if score < 35 else "MEDIUM" if score < 65 else "HIGH"
    return {"score": score, "level": level, "reasons": reasons}
