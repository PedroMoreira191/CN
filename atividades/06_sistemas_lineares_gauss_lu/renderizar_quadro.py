from pathlib import Path
from unittest.mock import patch

import nbformat
from IPython import display as ipython_display


NOTEBOOK = Path(__file__).with_name("solucao.ipynb")
PREVIEW = Path(__file__).with_name("figuras") / "quadro_gauss.png"


def main():
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    namespace = {}

    with patch.object(ipython_display, "display", return_value=None):
        for index in (3, 5, 6):
            exec(
                compile(notebook.cells[index].source, f"cell_{index}", "exec"),
                namespace,
            )

    namespace["desenhar_quadro"](2)
    namespace["figura"].savefig(PREVIEW, dpi=160, bbox_inches="tight")
    print(PREVIEW.resolve())


if __name__ == "__main__":
    main()
