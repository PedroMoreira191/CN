import ast
import os
import tempfile
import unittest
from pathlib import Path

import nbformat
import numpy as np
from PIL import Image, ImageStat

from conftest import NOTEBOOK_PATH, PROJECT_ROOT, carregar_namespace


class TestEstruturaDoNotebook(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)
        cls.markdown = "\n".join(
            cell.source for cell in cls.notebook.cells if cell.cell_type == "markdown"
        )
        cls.codigo = "\n".join(
            cell.source for cell in cls.notebook.cells if cell.cell_type == "code"
        )

    def test_secoes_academicas_aparecem_na_ordem_de_leitura(self):
        """Quebra se o notebook deixar de funcionar como relatório acadêmico."""
        titulos = [
            "## 1. Introdução",
            "## 2. Funções investigadas",
            "## 3. Critérios de convergência",
            "## 4. Método da Bisseção",
            "## 5. Método de Newton",
            "## 6. Método da Secante",
            "## 7. Aplicação dos métodos",
            "## 8. Tabela comparativa",
            "## 9. Animações",
            "## 10. Discussão dos resultados",
            "## 11. Estudo de f4",
            "## 12. Conclusões",
            "# Resumo para o Dashboard",
            "## Checklist final",
        ]
        posicoes = [self.markdown.index(titulo) for titulo in titulos]
        self.assertEqual(posicoes, sorted(posicoes))

    def test_conteudo_explica_formulas_criterios_e_resultados_reais(self):
        """Quebra se teoria, critério combinado ou análise numérica forem removidos."""
        obrigatorios = [
            "x_{k+1}",
            "f'(x_k)",
            "f(x_k)-f(x_{k-1})",
            "tol=1e-6",
            "max_iter=100",
            "ZERO_TOL=1e-12",
            "20 e 22 iterações",
            "3 e 4 iterações",
            "Experimentos adicionais",
            "0 → 1 → 0",
        ]
        texto_total = self.markdown + "\n" + self.codigo
        for trecho in obrigatorios:
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, texto_total)

    def test_codigo_e_portatil_e_nao_usa_resolvedores_prontos(self):
        """Quebra se o notebook passar a depender da máquina local ou do SciPy."""
        self.assertNotIn("/Users/", self.codigo)
        self.assertNotIn("scipy.optimize", self.codigo)
        self.assertNotIn("fsolve", self.codigo)
        permitidos = {
            "pathlib",
            "math",
            "os",
            "tempfile",
            "numpy",
            "pandas",
            "matplotlib",
            "IPython",
            "PIL",
        }
        encontrados = set()
        for cell in self.notebook.cells:
            if cell.cell_type != "code":
                continue
            arvore = ast.parse(cell.source)
            for no in ast.walk(arvore):
                if isinstance(no, ast.Import):
                    encontrados.update(alias.name.split(".")[0] for alias in no.names)
                elif isinstance(no, ast.ImportFrom) and no.module:
                    encontrados.add(no.module.split(".")[0])
        self.assertTrue(encontrados <= permitidos, encontrados - permitidos)
        self.assertEqual(self.notebook.metadata.kernelspec.name, "python3")
        self.assertIn("colab", self.notebook.metadata)


class TestDocumentacao(unittest.TestCase):
    COLAB_URL = "https://colab.research.google.com/drive/1FAhXt0_V3iNqLZA3MsjNvorEmtYeY4mf"

    def test_readme_e_guia_cobrem_execucao_e_montagem(self):
        """Quebra se a entrega deixar de ser reproduzível ou montável no Mathcha."""
        readme_path = PROJECT_ROOT / "README.md"
        guia_path = PROJECT_ROOT / "GUIA_MATHCHA.md"
        self.assertTrue(readme_path.exists())
        self.assertTrue(guia_path.exists())
        readme = readme_path.read_text(encoding="utf-8")
        guia = guia_path.read_text(encoding="utf-8")
        for trecho in (
            "Objetivo",
            "Arquivos",
            "Dependências",
            "Como executar",
            "Regenerar os GIFs",
            "Critério de parada",
            "bissecao_f2.gif",
            "newton_f2.gif",
            "secante_f2.gif",
        ):
            self.assertIn(trecho, readme)
        for trecho in (
            "1200 px",
            "Cálculo Numérico — Atividade Prática III",
            "Abrir notebook no Google Colab",
            "Resultados dos 12 testes",
            "Leituras principais",
            "hyperlink",
            "GIF",
        ):
            self.assertIn(trecho, guia)

    def test_link_publicado_aparece_em_todos_os_artefatos(self):
        """Quebra se a entrega voltar a exibir um link provisório do Colab."""
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        guia = (PROJECT_ROOT / "GUIA_MATHCHA.md").read_text(encoding="utf-8")
        notebook = NOTEBOOK_PATH.read_text(encoding="utf-8")
        builder = (PROJECT_ROOT / "scripts" / "build_notebook.py").read_text(
            encoding="utf-8"
        )
        for nome, conteudo in {
            "README": readme,
            "guia": guia,
            "notebook": notebook,
            "builder": builder,
        }.items():
            with self.subTest(artefato=nome):
                self.assertIn(self.COLAB_URL, conteudo)
                self.assertNotIn("será inserido após a publicação", conteudo)


class TestDashboardPreview(unittest.TestCase):
    def test_cartoes_resumem_as_formulas_dos_tres_metodos(self):
        """Quebra se um cartão visual omitir a fórmula do método correspondente."""
        builder = (PROJECT_ROOT / "scripts" / "build_notebook.py").read_text(
            encoding="utf-8"
        )
        for trecho in [
            "c = (a+b)/2",
            "xₖ₊₁ = xₖ − f(xₖ)/f′(xₖ)",
            "(xₖ−xₖ₋₁)/(f(xₖ)−f(xₖ₋₁))",
        ]:
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, builder)

    def test_layout_separa_objetivo_dos_cartoes_de_metodo(self):
        """Quebra se os cartões voltarem a invadir a linha do objetivo."""
        cwd_original = Path.cwd()
        os.chdir(PROJECT_ROOT)
        try:
            ns = carregar_namespace(
                [
                    "setup",
                    "funcoes",
                    "metodos",
                    "experimentos",
                    "tabela_resultados",
                    "dashboard_preview",
                ]
            )
            geometria = ns["_geometria_dashboard"]()
            self.assertGreaterEqual(
                geometria["objetivo_y"] - geometria["cartoes_top"], 0.12
            )
        finally:
            os.chdir(cwd_original)

    def test_previa_vertical_tem_conteudo_em_todos_os_blocos(self):
        """Quebra se a composição ficar vazia, horizontal ou pequena para leitura."""
        cwd_original = Path.cwd()
        os.chdir(PROJECT_ROOT)
        try:
            ns = carregar_namespace(
                [
                    "setup",
                    "funcoes",
                    "metodos",
                    "experimentos",
                    "tabela_resultados",
                    "dashboard_preview",
                ]
            )
            with tempfile.TemporaryDirectory() as tempdir:
                caminho = Path(tempdir) / "dashboard.png"
                gerado = ns["gerar_dashboard_preview"](ns["df_resultados"], caminho)
                self.assertEqual(gerado, caminho)
                with Image.open(caminho) as imagem:
                    self.assertGreaterEqual(imagem.width, 1200)
                    self.assertGreater(imagem.height, imagem.width)
                    cinza = imagem.convert("L")
                    altura = cinza.height
                    for inicio, fim in ((0.0, 0.22), (0.30, 0.68), (0.72, 1.0)):
                        bloco = cinza.crop((0, int(inicio * altura), cinza.width, int(fim * altura)))
                        self.assertGreater(ImageStat.Stat(bloco).stddev[0], 5.0)
        finally:
            os.chdir(cwd_original)


if __name__ == "__main__":
    unittest.main()
