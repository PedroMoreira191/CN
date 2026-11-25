from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO
import unittest
from unittest.mock import patch

import nbformat
from IPython import display as ipython_display


NOTEBOOK = Path(__file__).with_name("solucao.ipynb")


class NotebookAnimationTest(unittest.TestCase):
    def test_animation_cell_is_runnable_and_numerically_verified(self):
        self.assertTrue(NOTEBOOK.exists(), "o notebook resolvido ainda não foi gerado")

        notebook = nbformat.read(NOTEBOOK, as_version=4)
        animation_cell = notebook.cells[6]

        self.assertEqual(animation_cell.cell_type, "code")
        self.assertIn("FuncAnimation", animation_cell.source)
        self.assertIn("to_jshtml", animation_cell.source)
        self.assertIn("gerar_quadros_gauss", animation_cell.source)
        self.assertIn('alt="Quadro da eliminação de Gauss"', animation_cell.source)

        namespace = {}
        displayed_objects = []
        text_by_cell = {}
        with patch.object(
            ipython_display,
            "display",
            side_effect=lambda value: displayed_objects.append(value),
        ):
            for index, cell in enumerate(notebook.cells):
                if cell.cell_type != "code" or not cell.source.strip():
                    continue
                captured = StringIO()
                with redirect_stdout(captured):
                    exec(compile(cell.source, f"cell_{index}", "exec"), namespace)
                text_by_cell[index] = captured.getvalue()

        html_outputs = [
            value.data
            for value in displayed_objects
            if isinstance(value, ipython_display.HTML)
        ]
        self.assertTrue(html_outputs, "a animação não produziu saída HTML")

        text_output = text_by_cell[6]
        self.assertIn("Matriz triangular superior final", text_output)
        self.assertIn("Norma do resíduo: 0.000e+00", text_output)
        self.assertEqual(
            namespace["quadros"][2]["descricao"],
            "L2 ← L2 + 0.25 L1",
        )


if __name__ == "__main__":
    unittest.main()
