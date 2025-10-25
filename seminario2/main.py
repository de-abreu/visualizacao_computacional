from sqlalchemy import create_engine

import numpy as np
import pandas as pd

from arc_diagram.arc_diagram_dash import create_arc_diagram_dash


def main():
    """
    Main function for testing the interactive arc diagram with Dash.

    This script serves as a test harness for the interactive arc diagram visualization.
    """

    engine = create_engine("sqlite:///database/lattes.db")
    collaborations_query = """
    WITH article_collaborations AS (
        SELECT
            r1.name AS researcher_1,
            r2.name AS researcher_2,
            a.title AS collaboration,
            'artigo' AS type,
            a.year AS start,
            a.year AS end
        FROM authorship au1
        JOIN authorship au2 ON au1.article_id = au2.article_id AND au1.author_id < au2.author_id
        JOIN researchers r1 ON au1.author_id = r1.lattes_id
        JOIN researchers r2 ON au2.author_id = r2.lattes_id
        JOIN articles a ON au1.article_id = a.id
    ),
    project_collaborations AS (
        SELECT
            r1.name AS researcher_1,
            r2.name AS researcher_2,
            p.name AS collaboration,
            'projeto' AS type,
            p.start AS start,
            CAST(COALESCE(p.end, strftime('%Y', 'now')) AS INTEGER) AS end
        FROM participation p1
        JOIN participation p2 ON p1.project_id = p2.project_id AND p1.participant_id < p2.participant_id
        JOIN researchers r1 ON p1.participant_id = r1.lattes_id
        JOIN researchers r2 ON p2.participant_id = r2.lattes_id
        JOIN projects p ON p1.project_id = p.id
    )
    SELECT * FROM article_collaborations
    UNION ALL
    SELECT * FROM project_collaborations
    """

    # Load dataframe with data extracted from the database query
    try:
        collaborations: pd.DataFrame = pd.read_sql_query(collaborations_query, engine)
    except Exception as e:
        print(f"✗ Erro ao carregar dados de colaboração do banco de dados: {e}")
        print(
            "  - Verifique se o banco de dados existe e contém as tabelas necessárias"
        )
        raise

    print("✓ Dados de colaboração carregados com sucesso")
    print(f"  - {len(collaborations)} registros carregados")

    collaboration_graph: pd.DataFrame = (
        collaborations.groupby(["researcher_1", "researcher_2"])
        .size()
        .reset_index(name="collaborations")
    )

    researchers = sorted(
        set(collaboration_graph["researcher_1"]).union(
            set(collaboration_graph["researcher_2"])
        )
    )

    # Create mapping from researcher name to matrix index directly from the set
    researcher_to_index = {name: idx for idx, name in enumerate(researchers)}

    # Create empty square matrix
    n = len(researchers)
    collaboration_matrix = np.zeros((n, n), dtype=int)

    # Populate matrix with collaboration values
    for _, row in collaboration_graph.iterrows():
        i = researcher_to_index[row["researcher_1"]]
        j = researcher_to_index[row["researcher_2"]]
        collaboration_matrix[i, j] = collaboration_matrix[j, i] = row["collaborations"]

    # Create and run the Dash app with interactive hover filtering
    app = create_arc_diagram_dash(
        matrix=collaboration_matrix,
        title="Colaborações entre Professores do ICMC, em artigos e projetos de pesquisa",
        labels=researchers,
    )

    # Run the Dash app
    app.run(debug=True, host="127.0.0.1", port=8050)


if __name__ == "__main__":
    main()
