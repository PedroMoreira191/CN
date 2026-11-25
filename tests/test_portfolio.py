import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTIVITIES = ROOT / "atividades"
EXPECTED_ACTIVITY_DIRS = [
    "01_fundamentos_erros",
    "02_propagacao_erros_peca_circular",
    "03_biofluidodinamica",
    "04_estabilidade_overflow",
    "05_raizes_equacoes",
    "06_sistemas_lineares_gauss_lu",
    "07_sistemas_lineares_planos",
    "08_gauss_seidel",
    "09_interpolacao_polinomial",
    "10_integracao_numerica",
]
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


class PortfolioStructureTest(unittest.TestCase):
    def test_all_documented_activities_exist(self):
        actual = sorted(path.name for path in ACTIVITIES.iterdir() if path.is_dir())
        self.assertEqual(actual, EXPECTED_ACTIVITY_DIRS)
        for directory in EXPECTED_ACTIVITY_DIRS:
            readme = ACTIVITIES / directory / "README.md"
            self.assertTrue(readme.is_file(), f"README ausente: {readme}")
            self.assertGreater(len(readme.read_text(encoding="utf-8")), 500)

    def test_local_markdown_links_resolve(self):
        failures = []
        for markdown in ROOT.rglob("*.md"):
            relative_parts = markdown.relative_to(ROOT).parts
            if any(part in {".venv", "tmp"} for part in relative_parts):
                continue
            text = markdown.read_text(encoding="utf-8")
            for raw_target in MARKDOWN_LINK.findall(text):
                target = raw_target.split("#", 1)[0].strip()
                if not target or "://" in target or target.startswith("mailto:"):
                    continue
                target = target.strip("<>")
                resolved = (markdown.parent / target).resolve()
                if not resolved.exists():
                    failures.append(f"{markdown.relative_to(ROOT)} -> {target}")
        self.assertEqual(failures, [], "Links locais quebrados:\n" + "\n".join(failures))

    def test_notebooks_are_valid_json_without_saved_error_outputs(self):
        failures = []
        for notebook_path in ACTIVITIES.rglob("*.ipynb"):
            if ".ipynb_checkpoints" in notebook_path.parts:
                continue
            try:
                notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                failures.append(f"{notebook_path.relative_to(ROOT)}: {error}")
                continue
            if notebook.get("nbformat") != 4 or not isinstance(notebook.get("cells"), list):
                failures.append(f"{notebook_path.relative_to(ROOT)}: nbformat inválido")
            for cell_index, cell in enumerate(notebook.get("cells", [])):
                for output in cell.get("outputs", []):
                    if output.get("output_type") == "error":
                        failures.append(
                            f"{notebook_path.relative_to(ROOT)}: erro salvo na célula {cell_index}"
                        )
        self.assertEqual(failures, [], "Problemas em notebooks:\n" + "\n".join(failures))

    def test_python_sources_do_not_depend_on_user_home_paths(self):
        offenders = []
        for source in (ACTIVITIES / "06_sistemas_lineares_gauss_lu").glob("*.py"):
            if "/Users/" in source.read_text(encoding="utf-8"):
                offenders.append(source.relative_to(ROOT).as_posix())
        for source in (ACTIVITIES / "07_sistemas_lineares_planos").glob("*.py"):
            if "/Users/" in source.read_text(encoding="utf-8"):
                offenders.append(source.relative_to(ROOT).as_posix())
        self.assertEqual(offenders, [])

    def test_common_runtime_dependencies_are_declared(self):
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
        for package in (
            "jupyterlab",
            "matplotlib",
            "nbformat",
            "numpy",
            "pandas",
            "pillow",
            "scipy",
        ):
            self.assertRegex(requirements, rf"(?m)^{package}(?:[<>=!~].*)?$")

    def test_root_markdown_table_does_not_contain_raw_math_pipes(self):
        root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("\\frac{|", root_readme)
        self.assertNotIn("|x|", root_readme)

    def test_integration_notebook_uses_portable_reference_and_trapezoid(self):
        notebook_path = ACTIVITIES / "10_integracao_numerica" / "solucao.ipynb"
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
        source = "\n".join(
            "".join(cell.get("source", [])) for cell in notebook["cells"]
        )
        self.assertIn("math.erf", source)
        self.assertNotIn("scipy.integrate", source)
        self.assertNotIn("np.trapz", source)
        self.assertNotIn("np.trapezoid", source)


if __name__ == "__main__":
    unittest.main()

