import os
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from conftest import PROJECT_ROOT, carregar_namespace


class TestResultadosPrincipais(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cwd_original = Path.cwd()
        os.chdir(PROJECT_ROOT)
        cls.ns = carregar_namespace(
            [
                "setup",
                "funcoes",
                "metodos",
                "experimentos",
                "tabela_resultados",
                "validacao_resultados",
                "experimento_f4",
            ]
        )

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.cwd_original)

    def test_configuracao_contem_os_doze_casos_do_pdf(self):
        """Quebra se um método/função ou valor inicial do enunciado desaparecer."""
        configuracoes = self.ns["CONFIGURACOES"]
        self.assertEqual(len(configuracoes), 4)
        self.assertEqual(sum(len(item["casos"]) for item in configuracoes), 12)
        esperados = {
            "f1": {"bissecao": (1.0, 2.0), "newton": (1.5,), "secante": (1.0, 2.0)},
            "f2": {"bissecao": (1.0, 2.0), "newton": (1.5,), "secante": (1.0, 2.0)},
            "f3": {"bissecao": (0.0, 1.0), "newton": (0.5,), "secante": (0.0, 1.0)},
            "f4": {"bissecao": (-2.0, -1.0), "newton": (-2.0,), "secante": (-2.0, -1.0)},
        }
        observados = {
            item["nome"]: {caso["metodo"]: tuple(caso["iniciais"]) for caso in item["casos"]}
            for item in configuracoes
        }
        self.assertEqual(observados, esperados)

    def test_tabela_contem_doze_resultados_convergentes(self):
        """Quebra se a matriz completa não for executada ou ocultar uma falha."""
        df = self.ns["df_resultados"]
        self.assertEqual(len(df), 12)
        self.assertEqual(df.groupby("Função").size().tolist(), [3, 3, 3, 3])
        self.assertTrue((df["Resultado"] == "Convergiu").all())
        self.assertTrue((df["|f(x)| final"] < 1e-6).all())

    def test_raizes_e_iteracoes_correspondem_a_referencia_independente(self):
        """Quebra se fórmula, critério ou contagem de iterações forem alterados."""
        raizes = {
            "f1": np.sqrt(2.0),
            "f2": 1.5213797068045676,
            "f3": 0.5671432904097838,
            "f4": -1.7692923542386314,
        }
        iteracoes = {
            ("f1", "Bisseção"): 21,
            ("f1", "Newton"): 4,
            ("f1", "Secante"): 6,
            ("f2", "Bisseção"): 22,
            ("f2", "Newton"): 3,
            ("f2", "Secante"): 7,
            ("f3", "Bisseção"): 20,
            ("f3", "Newton"): 3,
            ("f3", "Secante"): 5,
            ("f4", "Bisseção"): 21,
            ("f4", "Newton"): 4,
            ("f4", "Secante"): 7,
        }
        for (nome, metodo), resultado in self.ns["resultados_detalhados"].items():
            with self.subTest(nome=nome, metodo=metodo):
                delta = 5e-7 if metodo == "Bisseção" else 5e-10
                self.assertAlmostEqual(resultado["raiz"], raizes[nome], delta=delta)
                self.assertEqual(resultado["iteracoes"], iteracoes[(nome, metodo)])

    def test_validacao_recalcula_residuos_com_as_funcoes_originais(self):
        """Quebra se o status convergente discordar do resíduo recalculado."""
        funcoes = {nome: self.ns[nome] for nome in ("f1", "f2", "f3", "f4")}
        for (nome, _), resultado in self.ns["resultados_detalhados"].items():
            self.assertLess(abs(funcoes[nome](resultado["raiz"])), self.ns["TOL"])
        self.assertTrue(self.ns["validacao_ok"])

    def test_newton_em_f4_com_x0_zero_forma_ciclo_e_nao_converge(self):
        """Quebra se o experimento adicional for misturado ou mascarado."""
        resultado = self.ns["resultado_f4_ciclo"]
        self.assertIs(resultado["convergiu"], False)
        self.assertEqual(resultado["iteracoes"], 100)
        self.assertEqual(resultado["historico"][:5], [0.0, 1.0, 0.0, 1.0, 0.0])

    def test_csv_preserva_as_sete_colunas_e_os_valores_numericos(self):
        """Quebra se a exportação divergir do DataFrame mostrado no notebook."""
        caminho = PROJECT_ROOT / "resultados.csv"
        self.assertTrue(caminho.exists())
        lido = pd.read_csv(caminho)
        original = self.ns["df_resultados"].reset_index(drop=True)
        self.assertEqual(lido.columns.tolist(), original.columns.tolist())
        self.assertEqual(len(lido), 12)
        pd.testing.assert_frame_equal(lido, original, check_exact=False, rtol=1e-14, atol=1e-15)


if __name__ == "__main__":
    unittest.main()
