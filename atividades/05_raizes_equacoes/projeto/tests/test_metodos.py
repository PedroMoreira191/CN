import math
import unittest

import numpy as np

from conftest import NOTEBOOK_PATH, carregar_namespace


@unittest.skipUnless(NOTEBOOK_PATH.exists(), "notebook ainda não criado")
class TestMetodosNumericos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ns = carregar_namespace(["setup", "funcoes", "metodos"])

    def test_convergencia_nominal_dos_tres_metodos_para_f1(self):
        """Quebra se um método deixa de convergir ou omite o contrato comum."""
        resultados = [
            self.ns["bissecao"](self.ns["f1"], 1.0, 2.0),
            self.ns["newton"](self.ns["f1"], self.ns["df1"], 1.5),
            self.ns["secante"](self.ns["f1"], 1.0, 2.0),
        ]
        chaves = {
            "raiz",
            "iteracoes",
            "historico",
            "residuo",
            "convergiu",
            "mensagem",
            "passos",
        }
        for resultado in resultados:
            with self.subTest(resultado=resultado):
                self.assertIs(resultado["convergiu"], True)
                self.assertLess(resultado["residuo"], 1e-6)
                self.assertEqual(set(resultado), chaves)

    def test_historico_conta_apenas_novas_aproximacoes(self):
        """Quebra se os chutes iniciais forem contados como iterações."""
        newton = self.ns["newton"](self.ns["f1"], self.ns["df1"], 1.5)
        secante = self.ns["secante"](self.ns["f1"], 1.0, 2.0)
        self.assertEqual(len(newton["historico"]), newton["iteracoes"] + 1)
        self.assertEqual(len(secante["historico"]), secante["iteracoes"] + 2)

    def test_raiz_em_extremo_ou_chute_converge_sem_iterar(self):
        """Quebra se uma raiz inicial for ignorada e o método iterar desnecessariamente."""
        f = lambda x: x - 1.0
        df = lambda x: 1.0
        casos = [
            self.ns["bissecao"](f, 1.0, 2.0),
            self.ns["newton"](f, df, 1.0),
            self.ns["secante"](f, 1.0, 2.0),
        ]
        for resultado in casos:
            with self.subTest(resultado=resultado):
                self.assertIs(resultado["convergiu"], True)
                self.assertEqual(resultado["iteracoes"], 0)
                self.assertEqual(resultado["raiz"], 1.0)
                self.assertTrue(
                    "inicial" in resultado["mensagem"].lower()
                    or "extremo" in resultado["mensagem"].lower()
                )

    def test_bissecao_rejeita_intervalo_sem_mudanca_de_sinal(self):
        """Quebra se a bisseção prosseguir sem garantia de raiz."""
        resultado = self.ns["bissecao"](lambda x: x * x + 1.0, -1.0, 1.0)
        self.assertIs(resultado["convergiu"], False)
        self.assertIn("mudança de sinal", resultado["mensagem"].lower())

    def test_newton_rejeita_derivada_quase_nula(self):
        """Quebra se Newton dividir por derivada abaixo de ZERO_TOL."""
        resultado = self.ns["newton"](lambda x: x + 1.0, lambda x: 0.0, 0.0)
        self.assertIs(resultado["convergiu"], False)
        self.assertIn("derivada", resultado["mensagem"].lower())

    def test_secante_rejeita_denominador_quase_nulo(self):
        """Quebra se a Secante dividir por valores funcionais iguais."""
        resultado = self.ns["secante"](lambda x: 1.0, 0.0, 1.0)
        self.assertIs(resultado["convergiu"], False)
        self.assertIn("denominador", resultado["mensagem"].lower())

    def test_limite_de_iteracoes_retorna_falha(self):
        """Quebra se esgotar max_iter for tratado como convergência."""
        resultado = self.ns["newton"](
            lambda x: x * x - 2.0, lambda x: 2.0 * x, 10.0, max_iter=1
        )
        self.assertIs(resultado["convergiu"], False)
        self.assertEqual(resultado["iteracoes"], 1)
        self.assertIn("máximo", resultado["mensagem"].lower())

    def test_entradas_nao_finitas_retornam_falha(self):
        """Quebra se nan/inf escaparem como exceção ou falsa convergência."""
        for valor in (math.nan, math.inf):
            casos = [
                self.ns["bissecao"](lambda x: x - 1.0, valor, 2.0),
                self.ns["newton"](lambda x: x - 1.0, lambda x: 1.0, valor),
                self.ns["secante"](lambda x: x - 1.0, valor, 2.0),
            ]
            for resultado in casos:
                with self.subTest(valor=valor, resultado=resultado):
                    self.assertIs(resultado["convergiu"], False)
                    self.assertTrue(np.isnan(resultado["raiz"]))
                    self.assertIn("finito", resultado["mensagem"].lower())

    def test_passo_pequeno_sem_residuo_pequeno_nao_converge(self):
        """Quebra se o método usar OU em vez de E no critério de parada."""
        resultado = self.ns["newton"](
            lambda x: x + 10.0,
            lambda x: 1e12,
            0.0,
            tol=1e-6,
            max_iter=1,
        )
        self.assertLess(abs(resultado["historico"][-1] - resultado["historico"][-2]), 1e-6)
        self.assertGreater(resultado["residuo"], 1e-6)
        self.assertIs(resultado["convergiu"], False)


class TestNotebookAindaAusente(unittest.TestCase):
    def test_notebook_existe_para_expor_os_metodos(self):
        """Quebra enquanto o artefato que contém o código ainda não foi criado."""
        self.assertTrue(NOTEBOOK_PATH.exists(), f"Notebook não encontrado: {NOTEBOOK_PATH}")


if __name__ == "__main__":
    unittest.main()
