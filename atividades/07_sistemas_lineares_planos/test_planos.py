from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nbformat
import numpy as np


ROOT = Path(__file__).parent
GENERATOR = ROOT / "construir_notebook.py"


class ColabPlanosTest(unittest.TestCase):
    def load_generator(self):
        self.assertTrue(GENERATOR.exists(), "o gerador do notebook ainda não existe")
        spec = spec_from_file_location("criar_colab_planos", GENERATOR)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def build_notebook(self):
        module = self.load_generator()
        temporary_directory = TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        notebook_path = Path(temporary_directory.name) / "planos.ipynb"
        module.build_notebook(notebook_path)
        notebook = nbformat.read(notebook_path, as_version=4)
        nbformat.validate(notebook)
        return notebook

    @staticmethod
    def execute_tagged_cell(notebook, tag, namespace):
        cell = next(cell for cell in notebook.cells if tag in cell.metadata.get("tags", []))
        exec(compile(cell.source, f"<{tag}>", "exec"), namespace)

    def test_default_system_has_the_expected_unique_solution(self):
        notebook = self.build_notebook()
        namespace = {}
        self.execute_tagged_cell(notebook, "core", namespace)

        result = namespace["analisar_sistema"](
            np.array([[2, 1, -1], [-3, -1, 2], [-2, 1, 2]], dtype=float),
            np.array([8, -11, -3], dtype=float),
        )

        self.assertEqual(result["classificacao"], "Solução única")
        np.testing.assert_allclose(result["solucao"], [2, 3, -1])
        self.assertLess(result["norma_residuo"], 1e-12)

    def test_singular_systems_are_classified_correctly(self):
        notebook = self.build_notebook()
        namespace = {}
        self.execute_tagged_cell(notebook, "core", namespace)

        matrix = np.array([[1, 1, 1], [2, 2, 2], [1, -1, 0]], dtype=float)
        consistent = namespace["analisar_sistema"](matrix, np.array([3, 6, 0], dtype=float))
        inconsistent = namespace["analisar_sistema"](matrix, np.array([3, 7, 0], dtype=float))

        self.assertEqual(consistent["classificacao"], "Infinitas soluções")
        self.assertEqual(inconsistent["classificacao"], "Sistema incompatível")

    def test_classification_is_invariant_under_uniform_rescaling(self):
        notebook = self.build_notebook()
        namespace = {}
        self.execute_tagged_cell(notebook, "core", namespace)

        matrix = 1e-12 * np.eye(3)
        right_side = 1e-12 * np.array([2.0, 3.0, -1.0])
        result = namespace["analisar_sistema"](matrix, right_side)

        self.assertEqual(result["classificacao"], "Solução única")
        self.assertEqual(result["posto_A"], 3)
        self.assertEqual(result["posto_aumentada"], 3)
        np.testing.assert_allclose(result["solucao"], [2.0, 3.0, -1.0])

    def test_large_right_side_never_reduces_augmented_rank(self):
        notebook = self.build_notebook()
        namespace = {}
        self.execute_tagged_cell(notebook, "core", namespace)

        result = namespace["analisar_sistema"](
            np.eye(3), np.array([1e15, 2.0, 3.0])
        )

        self.assertEqual(result["classificacao"], "Solução única")
        self.assertEqual(result["posto_A"], 3)
        self.assertEqual(result["posto_aumentada"], 3)
        np.testing.assert_allclose(result["solucao"], [1e15, 2.0, 3.0])

    def test_incompatible_classification_survives_extreme_rescaling(self):
        notebook = self.build_notebook()
        namespace = {}
        self.execute_tagged_cell(notebook, "core", namespace)

        matrix = np.diag([1.0, 1.0, 0.0])
        right_side = np.array([1.0, 1.0, 1.0])
        for factor in (1e-200, 1.0, 1e200):
            with self.subTest(factor=factor):
                result = namespace["analisar_sistema"](
                    factor * matrix, factor * right_side
                )
                self.assertEqual(result["classificacao"], "Sistema incompatível")
                self.assertEqual(result["posto_A"], 2)
                self.assertEqual(result["posto_aumentada"], 3)

    def test_plot_keeps_all_planes_after_uniform_rescaling(self):
        notebook = self.build_notebook()
        namespace = {}
        self.execute_tagged_cell(notebook, "core", namespace)

        matrix = 1e-15 * np.array(
            [[2, 1, -1], [-3, -1, 2], [-2, 1, 2]], dtype=float
        )
        right_side = 1e-15 * np.array([8, -11, -3], dtype=float)
        result = namespace["analisar_sistema"](matrix, right_side)
        figure, axes = namespace["plotar_planos"](
            matrix, right_side, result, limite=6
        )
        self.addCleanup(plt.close, figure)

        self.assertGreaterEqual(len(axes.collections), 4)

    def test_plane_mesh_satisfies_each_equation_for_any_orientation(self):
        notebook = self.build_notebook()
        namespace = {}
        self.execute_tagged_cell(notebook, "core", namespace)

        cases = [
            (np.array([1.0, 2.0, 3.0]), 4.0),
            (np.array([0.0, 2.0, 3.0]), -2.0),
            (np.array([1.0, 0.0, 0.0]), 5.0),
        ]
        for normal, independent_term in cases:
            x, y, z = namespace["malha_plano"](normal, independent_term, limite=6, pontos=17)
            residual = normal[0] * x + normal[1] * y + normal[2] * z - independent_term
            self.assertLess(np.max(np.abs(residual)), 1e-10)

    def test_plot_contains_three_planes_and_the_unique_intersection(self):
        notebook = self.build_notebook()
        namespace = {}
        self.execute_tagged_cell(notebook, "core", namespace)

        matrix = np.array([[2, 1, -1], [-3, -1, 2], [-2, 1, 2]], dtype=float)
        right_side = np.array([8, -11, -3], dtype=float)
        result = namespace["analisar_sistema"](matrix, right_side)
        figure, axes = namespace["plotar_planos"](matrix, right_side, result, limite=6)
        self.addCleanup(plt.close, figure)

        self.assertGreaterEqual(len(axes.collections), 4)
        self.assertEqual(axes.get_xlabel(), "x")
        self.assertEqual(axes.get_ylabel(), "y")
        self.assertEqual(axes.get_zlabel(), "z")

    def test_colab_interface_cell_executes_without_local_widgets(self):
        notebook = self.build_notebook()
        namespace = {}
        self.execute_tagged_cell(notebook, "core", namespace)
        self.execute_tagged_cell(notebook, "interface-colab", namespace)

    def test_saved_notebook_contains_a_rendered_preview(self):
        notebook = self.build_notebook()
        preview = next(
            cell for cell in notebook.cells if "preview" in cell.metadata.get("tags", [])
        )
        image_outputs = [
            output.data["image/png"]
            for output in preview.outputs
            if output.output_type in {"display_data", "execute_result"}
            and "image/png" in output.get("data", {})
        ]
        self.assertTrue(image_outputs)
        self.assertGreater(len(image_outputs[0]), 10_000)
        html_outputs = [
            output.data["text/html"]
            for output in preview.outputs
            if output.output_type in {"display_data", "execute_result"}
            and "text/html" in output.get("data", {})
        ]
        self.assertTrue(html_outputs)
        self.assertIn('alt="Três planos do sistema linear', html_outputs[0])


if __name__ == "__main__":
    unittest.main()
