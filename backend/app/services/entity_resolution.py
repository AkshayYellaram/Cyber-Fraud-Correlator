from collections import defaultdict

ENTITY_FIELDS = ["phone", "imei", "imsi", "ip", "mac", "upi_id", "account_id"]

def build_entity_links(dataframes):
    # Each dataframe becomes a source of evidence. Values shared across
    # records create deterministic links; no opaque ML decision is required.
    value_index = defaultdict(list)
    records = []

    for source_name, df in dataframes:
        for row_idx, row in df.iterrows():
            record_id = f"{source_name}:{row_idx}"
            record = {"record_id": record_id, "source": source_name}
            for field in ENTITY_FIELDS:
                value = row.get(field)
                if value is not None and str(value).strip() and str(value).lower() != "nan":
                    value = str(value).strip().lower()
                    record[field] = value
                    value_index[(field, value)].append(record_id)
            records.append(record)

    links = []
    for (field, value), ids in value_index.items():
        if len(ids) > 1:
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    links.append({
                        "type": field,
                        "value": value,
                        "source": ids[i],
                        "target": ids[j],
                    })
    return records, links
