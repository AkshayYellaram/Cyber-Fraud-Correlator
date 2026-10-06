import networkx as nx


# ============================================================
# ENTITY FIELDS
# ============================================================

ENTITY_FIELDS = [

    "phone",
    "imei",
    "imsi",
    "ip",
    "mac",
    "upi_id",
    "account_id",

]


# ============================================================
# BUILD ENTITY GRAPH
# ============================================================

def build_entity_graph(
    dataframes
):

    G = nx.Graph()


    # ========================================================
    # EVIDENCE → ENTITY
    # ========================================================

    for source_name, df in dataframes:

        for row_index, row in df.iterrows():

            evidence_id = (
                f"{source_name}:{row_index}"
            )


            G.add_node(
                evidence_id,
                node_type="evidence",
                source=source_name,
            )


            for field in ENTITY_FIELDS:

                value = row.get(
                    field
                )


                if value is None:
                    continue


                value = (
                    str(value)
                    .strip()
                    .lower()
                )


                if (
                    not value
                    or value == "nan"
                ):
                    continue


                entity_id = (
                    f"{field}:{value}"
                )


                G.add_node(
                    entity_id,
                    node_type=field,
                    label=value,
                )


                G.add_edge(
                    evidence_id,
                    entity_id,
                    relationship=(
                        f"contains_{field}"
                    ),
                )


    # ========================================================
    # ENTITY CO-OCCURRENCE
    # ========================================================

    for source_name, df in dataframes:

        for row_index, row in df.iterrows():

            entities = []


            for field in ENTITY_FIELDS:

                value = row.get(
                    field
                )


                if value is None:
                    continue


                value = (
                    str(value)
                    .strip()
                    .lower()
                )


                if (
                    not value
                    or value == "nan"
                ):
                    continue


                entities.append(
                    f"{field}:{value}"
                )


            for i in range(
                len(entities)
            ):

                for j in range(
                    i + 1,
                    len(entities)
                ):

                    G.add_edge(
                        entities[i],
                        entities[j],
                        relationship="co_occurrence",
                        evidence=(
                            f"{source_name}:{row_index}"
                        ),
                    )


    return G


# ============================================================
# GRAPH JSON
# ============================================================

def graph_json(
    G
):

    nodes = []


    for node, attrs in G.nodes(
        data=True
    ):

        nodes.append(
            {
                "id": node,
                **attrs,
            }
        )


    edges = []


    for source, target, attrs in G.edges(
        data=True
    ):

        edges.append(
            {
                "source": source,
                "target": target,
                **attrs,
            }
        )


    return {
        "nodes": nodes,
        "edges": edges,
    }