import sys
import tempfile
import unittest
from pathlib import Path

import nbformat

from conftest import PROJECT_ROOT

sys.path.insert(0, str(PROJECT_ROOT))


class TestExecutorLocal(unittest.TestCase):
    def test_executa_celulas_em_ordem_e_salva_outputs(self):
        """Quebra se o executor não preservar estado, stdout e resultado da última expressão."""
        from scripts.execute_notebook import execute_notebook

        notebook = nbformat.v4.new_notebook(
            cells=[
                nbformat.v4.new_code_cell("valor = 2\nprint('inicio')"),
                nbformat.v4.new_code_cell("valor * 5"),
            ]
        )
        with tempfile.TemporaryDirectory() as tempdir:
            caminho = Path(tempdir) / "teste.ipynb"
            nbformat.write(notebook, caminho)
            execute_notebook(caminho, cwd=Path(tempdir))
            executado = nbformat.read(caminho, as_version=4)

        self.assertEqual([cell.execution_count for cell in executado.cells], [1, 2])
        self.assertEqual(executado.cells[0].outputs[0].output_type, "stream")
        self.assertIn("inicio", executado.cells[0].outputs[0].text)
        self.assertEqual(executado.cells[1].outputs[0].output_type, "execute_result")
        self.assertEqual(executado.cells[1].outputs[0].data["text/plain"], "10")


if __name__ == "__main__":
    unittest.main()
