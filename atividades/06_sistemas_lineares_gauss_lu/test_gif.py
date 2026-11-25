from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import numpy as np
from fontTools.ttLib import TTFont
from PIL import Image


ROOT = Path(__file__).parent
MODULE_PATH = ROOT / "gerar_gif.py"


class GaussianEliminationGifTest(unittest.TestCase):
    def load_module(self):
        self.assertTrue(MODULE_PATH.exists(), "o gerador do GIF ainda não existe")
        spec = spec_from_file_location("gerar_gif_gauss", MODULE_PATH)
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_elimination_steps_reach_the_expected_solution(self):
        module = self.load_module()
        steps = module.gaussian_elimination_steps()

        np.testing.assert_allclose(
            steps[-1]["matrix"],
            np.array(
                [
                    [2.0, 1.0, -1.0, 8.0],
                    [0.0, 0.5, 0.5, 1.0],
                    [0.0, 0.0, -1.0, 1.0],
                ]
            ),
        )
        np.testing.assert_allclose(module.back_substitution(steps[-1]["matrix"]), [2, 3, -1])

    def test_generated_gif_is_hd_looping_and_complete(self):
        module = self.load_module()
        with TemporaryDirectory() as directory:
            output = Path(directory) / "gauss.gif"
            module.build_gif(output)

            with Image.open(output) as gif:
                self.assertEqual(gif.size, (1280, 720))
                self.assertGreaterEqual(gif.n_frames, 12)
                self.assertEqual(gif.info.get("loop"), 0)

                durations = []
                for frame_index in range(gif.n_frames):
                    gif.seek(frame_index)
                    durations.append(gif.info.get("duration", 0))
                self.assertGreaterEqual(sum(durations), 17_000)
                self.assertLessEqual(sum(durations), 21_000)

    def test_math_font_covers_every_special_symbol_used(self):
        module = self.load_module()
        self.assertTrue(hasattr(module, "MATH_FONT_PATH"))

        math_font = TTFont(module.MATH_FONT_PATH)
        codepoints = set().union(
            *(table.cmap.keys() for table in math_font["cmap"].tables)
        )
        required = "₁₂ᵀ‖✓←−·"
        missing = [character for character in required if ord(character) not in codepoints]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
