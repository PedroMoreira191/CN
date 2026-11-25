from pathlib import Path

import nbformat


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = PROJECT_ROOT / "atividade_calculo_numerico.ipynb"


def carregar_namespace(tags):
    """Executa, em ordem, uma célula de código para cada tag solicitada."""
    if not NOTEBOOK_PATH.exists():
        raise AssertionError(f"Notebook não encontrado: {NOTEBOOK_PATH}")

    notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)
    namespace = {"__name__": "__notebook_test__"}

    for tag in tags:
        correspondentes = [
            cell
            for cell in notebook.cells
            if cell.cell_type == "code" and tag in cell.metadata.get("tags", [])
        ]
        if len(correspondentes) != 1:
            raise AssertionError(
                f"Esperada exatamente uma célula com tag {tag!r}; "
                f"encontradas {len(correspondentes)}."
            )
        exec(compile(correspondentes[0].source, f"<notebook:{tag}>", "exec"), namespace)

    return namespace
