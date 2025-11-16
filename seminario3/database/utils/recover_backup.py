# pyright: reportAny=false, reportUnknownMemberType=false
import os
from typing import Any
import dill  # pyright: ignore [reportMissingTypeStubs]


def recover_backup(data_path: str) -> dict[str, Any]:  # pyright: ignore [reportExplicitAny]
    data = {}
    if not os.path.exists(data_path):
        print("Arquivo de backup não encontrado. Criando novo...")
        with open(data_path, "wb") as f:
            dill.dump(data, f)  ## inicia vazio

    # Carrega o conteúdo
    with open(data_path, "rb") as f:
        data = dill.load(f)
    return data
