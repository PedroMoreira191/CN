from pathlib import Path

import numpy as np
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 1280, 720
FONT_PATH = font_manager.findfont("DejaVu Sans")
FONT_BOLD_PATH = font_manager.findfont(
    font_manager.FontProperties(family="DejaVu Sans", weight="bold")
)
MATH_FONT_PATH = FONT_PATH
MATH_FONT_BOLD_PATH = FONT_BOLD_PATH

COLORS = {
    "bg_top": (9, 17, 31),
    "bg_bottom": (13, 27, 47),
    "surface": (20, 35, 58),
    "surface_alt": (25, 43, 70),
    "border": (56, 76, 105),
    "text": (244, 247, 252),
    "muted": (157, 174, 199),
    "blue": (76, 201, 240),
    "blue_soft": (25, 78, 105),
    "green": (101, 214, 173),
    "green_soft": (25, 78, 69),
    "yellow": (246, 200, 95),
    "yellow_soft": (92, 72, 31),
    "red": (255, 107, 107),
}


def font(size, weight="regular"):
    path = FONT_BOLD_PATH if weight in {"bold", "demi", "medium"} else FONT_PATH
    return ImageFont.truetype(path, size=size)


def math_font(size, bold=False):
    path = MATH_FONT_BOLD_PATH if bold else MATH_FONT_PATH
    return ImageFont.truetype(path, size=size)


FONTS = {
    "kicker": font(18, "demi"),
    "title": font(42, "bold"),
    "subtitle": font(22, "regular"),
    "section": font(28, "demi"),
    "body": font(24, "regular"),
    "body_bold": font(24, "demi"),
    "equation": font(35, "medium"),
    "matrix": font(29, "medium"),
    "matrix_small": font(24, "medium"),
    "hero": font(62, "bold"),
    "hero_small": font(44, "bold"),
    "label": font(16, "demi"),
    "small": font(17, "regular"),
    "small_bold": font(17, "demi"),
    "math": math_font(28),
    "math_large": math_font(35),
    "math_bold": math_font(28, bold=True),
}


def gaussian_elimination_steps():
    matrix = np.array(
        [
            [2.0, 1.0, -1.0, 8.0],
            [-3.0, -1.0, 2.0, -11.0],
            [-2.0, 1.0, 2.0, -3.0],
        ]
    )

    steps = [
        {
            "matrix": matrix.copy(),
            "operation": "Matriz aumentada inicial",
            "pivot": None,
            "target_row": None,
        }
    ]

    operations = [
        (1, 0, -1.5, "L₂ ← L₂ + 1,5 L₁"),
        (2, 0, -1.0, "L₃ ← L₃ + L₁"),
        (2, 1, 4.0, "L₃ ← L₃ − 4 L₂"),
    ]

    for target_row, pivot_row, multiplier, label in operations:
        matrix[target_row] -= multiplier * matrix[pivot_row]
        matrix[np.abs(matrix) < 1e-12] = 0.0
        steps.append(
            {
                "matrix": matrix.copy(),
                "operation": label,
                "pivot": (pivot_row, pivot_row),
                "target_row": target_row,
            }
        )
    return steps


def back_substitution(augmented_matrix):
    augmented_matrix = np.asarray(augmented_matrix, dtype=float)
    upper = augmented_matrix[:, :-1]
    right_side = augmented_matrix[:, -1]
    solution = np.zeros(len(right_side))

    for row in range(len(right_side) - 1, -1, -1):
        solution[row] = (
            right_side[row] - upper[row, row + 1:] @ solution[row + 1:]
        ) / upper[row, row]
    return solution


def text_width(draw, text, selected_font):
    box = draw.textbbox((0, 0), text, font=selected_font)
    return box[2] - box[0]


def draw_centered(draw, text, y, selected_font, fill, center=WIDTH // 2):
    x = center - text_width(draw, text, selected_font) / 2
    draw.text((x, y), text, font=selected_font, fill=fill)


def rounded_box(draw, box, fill, outline=None, radius=22, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def background():
    image = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg_top"])
    pixels = image.load()
    for y in range(HEIGHT):
        fraction = y / (HEIGHT - 1)
        color = tuple(
            round(COLORS["bg_top"][channel] * (1 - fraction) + COLORS["bg_bottom"][channel] * fraction)
            for channel in range(3)
        )
        for x in range(WIDTH):
            pixels[x, y] = color

    draw = ImageDraw.Draw(image)
    for y in range(26, HEIGHT, 38):
        for x in range(28, WIDTH, 38):
            draw.ellipse((x, y, x + 2, y + 2), fill=(31, 50, 77))
    return image


def draw_progress(draw, phase):
    labels = ["Sistema", "Matriz", "Eliminação", "Triangular", "Substituição", "Verificação"]
    left, right, y = 72, WIDTH - 72, 665
    segment = (right - left) / len(labels)

    draw.line((left, y, right, y), fill=COLORS["border"], width=2)
    for index, label in enumerate(labels):
        x = left + segment * (index + 0.5)
        active = index <= phase
        dot_color = COLORS["blue"] if active else COLORS["border"]
        if index < phase:
            dot_color = COLORS["green"]
        draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=dot_color)
        label_color = COLORS["text"] if index == phase else COLORS["muted"]
        draw_centered(draw, label, y + 16, FONTS["label"], label_color, center=x)


def draw_header(draw, title, subtitle, phase):
    draw.text((72, 42), "CÁLCULO NUMÉRICO  •  ELIMINAÇÃO DE GAUSS", font=FONTS["kicker"], fill=COLORS["blue"])
    draw.text((72, 75), title, font=FONTS["title"], fill=COLORS["text"])
    draw.text((74, 128), subtitle, font=FONTS["subtitle"], fill=COLORS["muted"])
    draw_progress(draw, phase)


def format_number(value):
    if abs(value - round(value)) < 1e-10:
        return str(int(round(value))).replace("-", "−")
    return f"{value:.2f}".rstrip("0").rstrip(".").replace("-", "−").replace(".", ",")


def draw_matrix(
    draw,
    matrix,
    x,
    y,
    cell_width=105,
    cell_height=64,
    pivot=None,
    target_row=None,
    solved_row=None,
    small=False,
):
    rows, columns = matrix.shape
    selected_font = FONTS["matrix_small"] if small else FONTS["matrix"]
    total_width = columns * cell_width + 26
    total_height = rows * cell_height

    for row in range(rows):
        if row == target_row:
            rounded_box(
                draw,
                (x + 12, y + row * cell_height + 3, x + total_width - 12, y + (row + 1) * cell_height - 3),
                COLORS["yellow_soft"],
                radius=12,
            )
        if row == solved_row:
            rounded_box(
                draw,
                (x + 12, y + row * cell_height + 3, x + total_width - 12, y + (row + 1) * cell_height - 3),
                COLORS["green_soft"],
                radius=12,
            )

    if pivot is not None:
        pivot_row, pivot_column = pivot
        cell_left = x + 13 + pivot_column * cell_width
        cell_top = y + pivot_row * cell_height + 4
        rounded_box(
            draw,
            (cell_left, cell_top, cell_left + cell_width - 4, cell_top + cell_height - 8),
            COLORS["blue_soft"],
            outline=COLORS["blue"],
            radius=11,
            width=2,
        )

    for row in range(rows):
        for column in range(columns):
            value = format_number(matrix[row, column])
            center_x = x + 13 + column * cell_width + (cell_width - 4) / 2
            center_y = y + row * cell_height + cell_height / 2
            fill = COLORS["text"]
            if abs(matrix[row, column]) < 1e-12 and row > column:
                fill = COLORS["green"]
            draw_centered(draw, value, center_y - selected_font.size / 2 - 2, selected_font, fill, center=center_x)

    divider_x = x + 13 + (columns - 1) * cell_width - 7
    draw.line((divider_x, y + 6, divider_x, y + total_height - 6), fill=COLORS["yellow"], width=3)

    bracket_color = COLORS["muted"]
    left_x, right_x = x, x + total_width
    draw.line((left_x + 10, y, left_x, y, left_x, y + total_height, left_x + 10, y + total_height), fill=bracket_color, width=4)
    draw.line((right_x - 10, y, right_x, y, right_x, y + total_height, right_x - 10, y + total_height), fill=bracket_color, width=4)
    return total_width, total_height


def draw_operation_panel(draw, title, operation, explanation, accent="blue"):
    box = (785, 215, 1200, 525)
    rounded_box(draw, box, COLORS["surface"], COLORS["border"], radius=26, width=2)
    draw.text((825, 250), title.upper(), font=FONTS["label"], fill=COLORS[accent])
    draw.text((825, 300), operation, font=FONTS["math_bold"], fill=COLORS["text"])
    draw.line((825, 357, 1160, 357), fill=COLORS["border"], width=2)

    words = explanation.split()
    lines, line = [], ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if text_width(draw, candidate, FONTS["body"]) <= 325:
            line = candidate
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)

    for index, value in enumerate(lines):
        draw.text((825, 390 + index * 35), value, font=FONTS["body"], fill=COLORS["muted"])


def render_cover():
    image = background()
    draw = ImageDraw.Draw(image)
    draw.text((72, 50), "CÁLCULO NUMÉRICO", font=FONTS["kicker"], fill=COLORS["blue"])
    draw.text((72, 185), "Resolvendo um", font=FONTS["hero_small"], fill=COLORS["muted"])
    draw.text((72, 245), "sistema linear", font=FONTS["hero"], fill=COLORS["text"])
    draw.text((75, 330), "Eliminação de Gauss + substituição regressiva", font=FONTS["subtitle"], fill=COLORS["blue"])

    rounded_box(draw, (760, 130, 1200, 525), COLORS["surface"], COLORS["border"], radius=32, width=2)
    equations = ["2x + y − z = 8", "−3x − y + 2z = −11", "−2x + y + 2z = −3"]
    for index, equation in enumerate(equations):
        draw_centered(draw, equation, 205 + index * 85, FONTS["equation"], COLORS["text"], center=980)
    draw_centered(draw, "objetivo: encontrar x, y e z", 470, FONTS["small"], COLORS["muted"], center=980)
    draw.text((72, 622), "PASSO A PASSO  •  3 INCÓGNITAS  •  SOLUÇÃO EXATA", font=FONTS["label"], fill=COLORS["green"])
    return image


def render_system():
    image = background()
    draw = ImageDraw.Draw(image)
    draw_header(draw, "1. O sistema linear", "Três equações e três incógnitas", 0)

    rounded_box(draw, (185, 205, 820, 555), COLORS["surface"], COLORS["border"], radius=28, width=2)
    equations = ["2x + y − z = 8", "−3x − y + 2z = −11", "−2x + y + 2z = −3"]
    for index, equation in enumerate(equations):
        color = COLORS["text"] if index == 0 else COLORS["muted"]
        draw.text((255, 255 + index * 88), equation, font=FONTS["equation"], fill=color)

    rounded_box(draw, (865, 255, 1115, 505), COLORS["blue_soft"], COLORS["blue"], radius=125, width=3)
    draw_centered(draw, "Ax = b", 332, FONTS["hero_small"], COLORS["text"], center=990)
    draw_centered(draw, "forma matricial", 415, FONTS["small"], COLORS["blue"], center=990)
    return image


def render_matrix_scene(title, subtitle, phase, matrix, pivot=None, target_row=None, operation=None, explanation=None, accent="blue"):
    image = background()
    draw = ImageDraw.Draw(image)
    draw_header(draw, title, subtitle, phase)
    draw_matrix(draw, matrix, 90, 250, cell_width=155, cell_height=76, pivot=pivot, target_row=target_row)
    if operation:
        draw_operation_panel(draw, "Operação elementar", operation, explanation, accent=accent)
    else:
        draw_operation_panel(
            draw,
            "Leitura",
            "[ A  |  b ]",
            "A barra separa os coeficientes das incógnitas dos termos independentes.",
            accent="yellow",
        )
    return image


def render_triangular(matrix):
    image = background()
    draw = ImageDraw.Draw(image)
    draw_header(draw, "Sistema triangular superior", "Os elementos abaixo da diagonal agora são zero", 3)
    draw_matrix(draw, matrix, 110, 245, cell_width=145, cell_height=74)
    draw_operation_panel(
        draw,
        "Objetivo alcançado",
        "U x = c",
        "A última equação contém apenas z. Agora resolvemos de baixo para cima.",
        accent="green",
    )
    return image


def render_back_substitution(matrix, variable, equation, result, solved_row, detail):
    image = background()
    draw = ImageDraw.Draw(image)
    draw_header(draw, f"Substituição regressiva: {variable}", "Resolvendo da última equação para a primeira", 4)
    draw_matrix(draw, matrix, 90, 255, cell_width=128, cell_height=68, solved_row=solved_row, small=True)

    rounded_box(draw, (685, 220, 1195, 545), COLORS["surface"], COLORS["border"], radius=28, width=2)
    draw.text((730, 260), "EQUAÇÃO ATUAL", font=FONTS["label"], fill=COLORS["green"])
    draw.text((730, 312), equation, font=FONTS["math"], fill=COLORS["text"])
    draw.text((730, 380), detail, font=FONTS["body"], fill=COLORS["muted"])
    rounded_box(draw, (730, 435, 1145, 510), COLORS["green_soft"], COLORS["green"], radius=18, width=2)
    draw_centered(draw, result, 451, FONTS["section"], COLORS["text"], center=937)
    return image


def render_solution(solution):
    image = background()
    draw = ImageDraw.Draw(image)
    draw_header(draw, "Solução encontrada", "As três incógnitas foram determinadas", 4)

    values = [("x", solution[0]), ("y", solution[1]), ("z", solution[2])]
    for index, (variable, value) in enumerate(values):
        left = 120 + index * 365
        rounded_box(draw, (left, 225, left + 315, 495), COLORS["surface"], COLORS["border"], radius=30, width=2)
        draw_centered(draw, variable, 265, FONTS["section"], COLORS["blue"], center=left + 157)
        draw_centered(draw, format_number(value), 330, FONTS["hero"], COLORS["text"], center=left + 157)
        draw_centered(draw, "valor exato", 432, FONTS["small"], COLORS["muted"], center=left + 157)
    return image


def render_verification(solution):
    image = background()
    draw = ImageDraw.Draw(image)
    draw_header(draw, "5. Verificação", "Substituímos a solução no sistema original", 5)

    rounded_box(draw, (95, 220, 1185, 545), COLORS["surface"], COLORS["border"], radius=30, width=2)
    draw.text((145, 265), "A · x", font=FONTS["section"], fill=COLORS["blue"])
    draw.text((270, 265), "=", font=FONTS["section"], fill=COLORS["muted"])
    draw.text((335, 265), "b", font=FONTS["section"], fill=COLORS["yellow"])

    matrix = np.array([[2, 1, -1], [-3, -1, 2], [-2, 1, 2]], dtype=float)
    right_side = matrix @ solution
    draw.text((145, 340), f"A · [ 2,  3,  −1 ]ᵀ  =  [ {format_number(right_side[0])},  {format_number(right_side[1])},  {format_number(right_side[2])} ]ᵀ", font=FONTS["math_large"], fill=COLORS["text"])
    rounded_box(draw, (145, 430, 1135, 505), COLORS["green_soft"], COLORS["green"], radius=18, width=2)
    draw_centered(draw, "Resíduo:  ‖Ax − b‖₂ = 0   ✓", 446, FONTS["math_bold"], COLORS["text"], center=640)
    return image


def render_final(solution):
    image = background()
    draw = ImageDraw.Draw(image)
    draw.text((72, 52), "RESULTADO FINAL", font=FONTS["kicker"], fill=COLORS["green"])
    draw_centered(draw, "Sistema resolvido", 145, FONTS["hero_small"], COLORS["text"])
    draw_centered(draw, "Eliminação de Gauss + substituição regressiva", 215, FONTS["subtitle"], COLORS["muted"])

    rounded_box(draw, (245, 305, 1035, 500), COLORS["surface"], COLORS["green"], radius=32, width=3)
    vector = f"( x, y, z ) = ( {format_number(solution[0])}, {format_number(solution[1])}, {format_number(solution[2])} )"
    draw_centered(draw, vector, 360, FONTS["hero_small"], COLORS["text"])
    draw_centered(draw, "solução exata verificada", 445, FONTS["small_bold"], COLORS["green"])
    draw_centered(draw, "A sequência de operações preserva o conjunto de soluções.", 585, FONTS["body"], COLORS["muted"])
    return image


def storyboard():
    steps = gaussian_elimination_steps()
    triangular = steps[-1]["matrix"]
    solution = back_substitution(triangular)

    scenes = [
        (render_cover(), 1300),
        (render_system(), 1200),
        (
            render_matrix_scene(
                "2. Matriz aumentada",
                "Organizamos os coeficientes e o vetor b",
                1,
                steps[0]["matrix"],
            ),
            1100,
        ),
        (
            render_matrix_scene(
                "Primeiro pivô",
                "O valor 2 guiará as eliminações na primeira coluna",
                2,
                steps[0]["matrix"],
                pivot=(0, 0),
                operation="p₁ = 2",
                explanation="Usaremos a primeira linha para criar zeros nas posições (2,1) e (3,1).",
            ),
            800,
        ),
        (
            render_matrix_scene(
                "Zerando a posição (2,1)",
                "A segunda linha é atualizada sem alterar a solução",
                2,
                steps[1]["matrix"],
                pivot=(0, 0),
                target_row=1,
                operation=steps[1]["operation"],
                explanation="O coeficiente −3 é eliminado. A nova segunda linha começa com zero.",
                accent="yellow",
            ),
            1100,
        ),
        (
            render_matrix_scene(
                "Zerando a posição (3,1)",
                "Aplicamos o mesmo pivô à terceira linha",
                2,
                steps[2]["matrix"],
                pivot=(0, 0),
                target_row=2,
                operation=steps[2]["operation"],
                explanation="O coeficiente −2 desaparece. A primeira coluna está concluída.",
                accent="yellow",
            ),
            1100,
        ),
        (
            render_matrix_scene(
                "Segundo pivô",
                "Agora trabalhamos na segunda coluna",
                2,
                steps[2]["matrix"],
                pivot=(1, 1),
                operation="p₂ = 0,5",
                explanation="A segunda linha elimina o único termo restante abaixo da diagonal.",
            ),
            800,
        ),
        (
            render_matrix_scene(
                "Zerando a posição (3,2)",
                "A matriz chega à forma triangular superior",
                2,
                steps[3]["matrix"],
                pivot=(1, 1),
                target_row=2,
                operation=steps[3]["operation"],
                explanation="O coeficiente 2 é eliminado. Todos os termos abaixo da diagonal são zero.",
                accent="yellow",
            ),
            1200,
        ),
        (render_triangular(triangular), 1000),
        (
            render_back_substitution(
                triangular,
                "z",
                "−z = 1",
                "z = −1",
                2,
                "A última equação tem apenas uma incógnita.",
            ),
            1000,
        ),
        (
            render_back_substitution(
                triangular,
                "y",
                "0,5y + 0,5(−1) = 1",
                "y = 3",
                1,
                "Substituímos z = −1 na segunda equação.",
            ),
            1050,
        ),
        (
            render_back_substitution(
                triangular,
                "x",
                "2x + 3 − (−1) = 8",
                "x = 2",
                0,
                "Com y e z conhecidos, resolvemos a primeira equação.",
            ),
            1050,
        ),
        (render_solution(solution), 1200),
        (render_verification(solution), 1300),
        (render_final(solution), 1500),
    ]
    return scenes


def build_gif(output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    scenes = storyboard()

    frames = []
    durations = []
    transition_duration = 60
    transition_steps = 3

    for index, (scene, hold_duration) in enumerate(scenes):
        if index > 0:
            previous = scenes[index - 1][0]
            for step in range(1, transition_steps + 1):
                fraction = step / (transition_steps + 1)
                frames.append(Image.blend(previous, scene, fraction))
                durations.append(transition_duration)
        frames.append(scene)
        durations.append(hold_duration)

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
        optimize=True,
    )
    return output_path


if __name__ == "__main__":
    destination = Path(__file__).with_name("figuras") / "eliminacao_gauss.gif"
    print(build_gif(destination).resolve())
