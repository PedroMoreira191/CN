import os
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from conftest import PROJECT_ROOT, carregar_namespace


class TestAnimacoes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cwd_original = Path.cwd()
        os.chdir(PROJECT_ROOT)
        cls.ns = carregar_namespace(
            [
                "setup",
                "funcoes",
                "metodos",
                "animacao_bissecao",
                "animacao_newton",
                "animacao_secante",
            ]
        )
        cls.tempdir = tempfile.TemporaryDirectory()
        destino = Path(cls.tempdir.name)

        cls.resultados = {
            "bissecao_f2.gif": cls.ns["bissecao"](cls.ns["f2"], 1.0, 2.0),
            "newton_f2.gif": cls.ns["newton"](cls.ns["f2"], cls.ns["df2"], 1.5),
            "secante_f2.gif": cls.ns["secante"](cls.ns["f2"], 1.0, 2.0),
        }
        cls.caminhos = {
            "bissecao_f2.gif": cls.ns["animar_bissecao"](
                cls.ns["f2"], cls.resultados["bissecao_f2.gif"], (0.8, 2.1), destino / "bissecao_f2.gif"
            ),
            "newton_f2.gif": cls.ns["animar_newton"](
                cls.ns["f2"], cls.ns["df2"], cls.resultados["newton_f2.gif"], (0.8, 2.1), destino / "newton_f2.gif"
            ),
            "secante_f2.gif": cls.ns["animar_secante"](
                cls.ns["f2"], cls.resultados["secante_f2.gif"], (0.8, 2.1), destino / "secante_f2.gif"
            ),
        }

    @classmethod
    def tearDownClass(cls):
        cls.tempdir.cleanup()
        os.chdir(cls.cwd_original)

    def test_gifs_sao_criados_com_nomes_dimensoes_e_formato_corretos(self):
        """Quebra se um gerador não produzir um GIF legível para o dashboard."""
        for nome, caminho in self.caminhos.items():
            with self.subTest(nome=nome):
                self.assertEqual(caminho.name, nome)
                self.assertTrue(caminho.exists())
                with Image.open(caminho) as imagem:
                    self.assertEqual(imagem.format, "GIF")
                    self.assertGreaterEqual(imagem.width, 800)
                    self.assertGreaterEqual(imagem.height, 500)
                    self.assertGreater(getattr(imagem, "n_frames", 1), 1)

    def test_gifs_tem_quadro_por_iteracao_e_pausa_final(self):
        """Quebra se passos forem omitidos ou o quadro final desaparecer rápido demais."""
        for nome, caminho in self.caminhos.items():
            resultado = self.resultados[nome]
            with self.subTest(nome=nome), Image.open(caminho) as imagem:
                n_frames = getattr(imagem, "n_frames", 1)
                duracoes = []
                for indice in range(n_frames):
                    imagem.seek(indice)
                    duracoes.append(imagem.info.get("duration", 0))
                self.assertGreaterEqual(n_frames, resultado["iteracoes"])
                self.assertGreaterEqual(duracoes[-1], duracoes[0])

    def test_caminho_relativo_cria_diretorio_de_destino(self):
        """Quebra se a animação depender de uma pasta absoluta já existente."""
        with tempfile.TemporaryDirectory() as tempdir:
            original = Path.cwd()
            os.chdir(tempdir)
            try:
                relativo = Path("saida") / "bissecao.gif"
                resultado = self.ns["bissecao"](self.ns["f2"], 1.0, 2.0, max_iter=3)
                caminho = self.ns["animar_bissecao"](
                    self.ns["f2"], resultado, (0.8, 2.1), relativo
                )
                self.assertEqual(caminho, relativo)
                self.assertTrue(relativo.exists())
            finally:
                os.chdir(original)


if __name__ == "__main__":
    unittest.main()
