from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import nbformat
from IPython import display as ipython_display


NOTEBOOK = Path(__file__).with_name("solucao.ipynb")


def display_output(value):
    if isinstance(value, ipython_display.HTML):
        return nbformat.v4.new_output(
            "display_data",
            data={
                "text/html": value.data,
                "text/plain": "<IPython.core.display.HTML object>",
            },
            metadata={},
        )
    return nbformat.v4.new_output(
        "display_data",
        data={"text/plain": repr(value)},
        metadata={},
    )


def main():
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    namespace = {}
    execution_count = 1

    for index, cell in enumerate(notebook.cells):
        if cell.cell_type != "code":
            continue

        cell.outputs = []
        cell.execution_count = execution_count
        execution_count += 1

        if not cell.source.strip():
            continue

        captured = StringIO()
        displayed = []
        with patch.object(
            ipython_display,
            "display",
            side_effect=lambda value: displayed.append(value),
        ):
            with redirect_stdout(captured):
                exec(compile(cell.source, f"cell_{index}", "exec"), namespace)

        if captured.getvalue():
            cell.outputs.append(
                nbformat.v4.new_output(
                    "stream",
                    name="stdout",
                    text=captured.getvalue(),
                )
            )
        cell.outputs.extend(display_output(value) for value in displayed)

    nbformat.validate(notebook)
    nbformat.write(notebook, NOTEBOOK)
    print(NOTEBOOK.resolve())


if __name__ == "__main__":
    main()
