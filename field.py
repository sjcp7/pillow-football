from PIL import Image, ImageDraw
import math
import random
from player import draw_player

# Proporções do mundo real mantidas através dos desenhos
# Baseadas no retângulo maior que faz o campo

screen_width = 1920
screen_height = 1080  # Definindo altura da tela
field_height = 300
number_standers = 100
field_offset_x = 200  # Diferença entre o valor x das linhas superior e inferior do campo
field_lower_y = 810  # Coordenada y da linha inferior do campo
field_lower_x = 152  # Coordenada x da linha inferior do campo
left_m = -field_height / field_offset_x  # Inclinação da linha esquerda do campo
right_m = -left_m  # Inclinação da linha direita do campo

def draw_field(d: ImageDraw):
    draw_grandstands(d)          # Desenha as arquibancadas
    draw_bigger_rectangle(d)
    draw_center(d)
    draw_penalty_circle(d, 390, field_lower_y - 22 - (field_height / 2), 120, 40)
    draw_penalty_circle(d, screen_width - 390, field_lower_y - 22 - (field_height / 2), 120, 40)
    draw_goals(d)
    draw_penalty_boxes(d)
    draw_goal_boxes(d)
    draw_circle(d, (390, field_lower_y - 22 - (field_height / 2)), 4, fill="white")
    draw_circle(d, (screen_width - 390, field_lower_y - 22 - (field_height / 2)), 4, fill="white")

def draw_grandstands(d: ImageDraw):
    """
    Desenha as arquibancadas nas laterais do campo e preenche todas as áreas de arquibancadas com standers.
    """
    # Definir as coordenadas do retângulo branco que representa áreas adicionais de arquibancadas
    stands_top_left = (0, 0)
    stands_bottom_right = (screen_width, field_lower_y - field_height - 5)

    # Desenhar o retângulo branco
    d.rectangle([stands_top_left, stands_bottom_right], fill="white", outline="white")
 
    # Definições das arquibancadas
    grandstand_width = 400  # Largura das arquibancadas
    grandstand_depth = 200  # Profundidade das arquibancadas

    # Cores para diversificar os standers
    colors = ["blue", "red", "yellow", "orange", "purple", "pink", "cyan", "magenta"]

    # Espaçamento entre standers
    x_spacing = 25
    y_spacing = 50

    # Preencher o retângulo branco com standers
    fill_rectangle_with_standers(
        d,
        stands_top_left,
        stands_bottom_right,
        colors,
        x_spacing,
        y_spacing
    )

    # Arquibancada Esquerda
    left_grandstand_x_start = 50  # Posição inicial no eixo x
    left_grandstand_y_start = field_lower_y - field_height - grandstand_depth  # Posição inicial no eixo y

  
    # Preencher a arquibancada esquerda com standers
    fill_rectangle_with_standers(
        d,
        (left_grandstand_x_start, left_grandstand_y_start),
        (left_grandstand_x_start + grandstand_width, left_grandstand_y_start + grandstand_depth),
        colors,
        x_spacing,
        y_spacing
    )

    # Arquibancada Direita
    right_grandstand_x_start = screen_width - 50 - grandstand_width  # Posição inicial no eixo x
    right_grandstand_y_start = field_lower_y - field_height - grandstand_depth  # Posição inicial no eixo y

    # Preencher a arquibancada direita com standers
    fill_rectangle_with_standers(
        d,
        (right_grandstand_x_start, right_grandstand_y_start),
        (right_grandstand_x_start + grandstand_width, right_grandstand_y_start + grandstand_depth),
        colors,
        x_spacing,
        y_spacing
    )

def fill_rectangle_with_standers(d: ImageDraw, top_left: tuple, bottom_right: tuple, colors: list, x_spacing: int, y_spacing: int):
    """
    Preenche um retângulo com standers organizados em uma grade com variações aleatórias.
    
    :param d: Objeto ImageDraw.
    :param top_left: Tupla (x, y) representando o canto superior esquerdo do retângulo.
    :param bottom_right: Tupla (x, y) representando o canto inferior direito do retângulo.
    :param colors: Lista de cores para os standers.
    :param x_spacing: Espaçamento horizontal entre standers.
    :param y_spacing: Espaçamento vertical entre standers.
    """
    x_start, y_start = top_left
    x_end, y_end = bottom_right

    for row in range(y_start, y_end, y_spacing):
        for col in range(x_start, x_end, x_spacing):
            # Adicionar pequenas variações nas posições
            x = col + random.randint(-5, 5)
            y = row + random.randint(-5, 5)
            
            color = random.choice(colors)
            scale = random.uniform(0.4, 1.2)  # Variar o tamanho dos standers
            
            draw_player(d, color, x, y, scale)

def draw_penalty_boxes(d: ImageDraw):
    # left penalty box
    b = field_lower_y - (left_m * field_lower_x)
    x1 = 215
    x2 = x1 + 100
    box_width = 150
    d.polygon(
        (
            (x1, x1 * left_m + b),
            (x2, x2 * left_m + b),
            (x2 + box_width, x2 * left_m + b),
            (x1 + box_width, x1 * left_m + b)
        ),
        width=3,
        outline="white",
        fill="green"
    )

    # right penalty box
    b = field_lower_y - (right_m * (screen_width - field_lower_x))
    x1 = screen_width - x1
    x2 = x1 - 100
    d.polygon(
        (
            (x1, x1 * right_m + b),
            (x2, x2 * right_m + b),
            (x2 - box_width, x2 * right_m + b),
            (x1 - box_width, x1 * right_m + b)
        ),
        width=3,
        outline="white",
        fill="green"
    )

def draw_goal_boxes(d: ImageDraw):
    # left goal box
    b = field_lower_y - (left_m * field_lower_x)
    x1 = 237
    x2 = x1 + 55
    box_width = 70
    d.polygon(
        (
            (x1, x1 * left_m + b),
            (x2, x2 * left_m + b),
            (x2 + box_width, x2 * left_m + b),
            (x1 + box_width, x1 * left_m + b)
        ),
        width=3,
        outline="white",
        fill="green"
    )

    # right goal box
    b = field_lower_y - (right_m * (screen_width - field_lower_x))
    x1 = screen_width - x1
    x2 = x1 - 55
    d.polygon(
        (
            (x1, x1 * right_m + b),
            (x2, x2 * right_m + b),
            (x2 - box_width, x2 * right_m + b),
            (x1 - box_width, x1 * right_m + b)
        ),
        width=3,
        outline="white",
        fill="green"
    )

def draw_goals(d: ImageDraw):
    # left goal
    b = field_lower_y - (left_m * field_lower_x)
    x1 = 245
    x2 = x1 + 40
    goal_height = 70
    d.polygon(
        (
            (x1, x1 * left_m + b),
            (x2, x2 * left_m + b),
            (x2, (x2 * left_m + b) - goal_height),
            (x1, (x1 * left_m + b) - goal_height)
        ),
        width=3
    )
    tw = 30  # largura do triângulo
    d.polygon(
        (
            (x1, x1 * left_m + b),
            (x1, (x1 * left_m + b) - goal_height),
            (x1 - tw, (x1 - tw) * left_m + b + tw * left_m)
        ),
        width=3
    )

    # right goal
    b = field_lower_y - (right_m * (screen_width - field_lower_x))
    x1 = screen_width - x1
    x2 = x1 - 40
    goal_height = 70
    d.polygon(
        (
            (x1, x1 * right_m + b),
            (x2, x2 * right_m + b),
            (x2, (x2 * right_m + b) - goal_height),
            (x1, (x1 * right_m + b) - goal_height)
        ),
        width=3
    )
    d.polygon(
        (
            (x1, x1 * right_m + b),
            (x1, (x1 * right_m + b) - goal_height),
            (x1 + tw, (x1 + tw) * right_m + b - tw * right_m)
        ),
        width=3
    )

def draw_penalty_circle(d: ImageDraw, cx: int, cy: int, width: int, height: int):
    d.ellipse(
        (cx - width / 2, cy - height / 2, cx + width / 2, cy + height / 2),
        outline="white",
        width=3
    )

def draw_center(d: ImageDraw):
    width = 300
    height = 100
    cx = screen_width / 2
    cy = 790 - (field_height / 2)  # coordenada y do centro do círculo
    d.ellipse(
        (cx - width / 2, cy - height / 2, cx + width / 2, cy + height / 2),
        outline="white",
        width=3
    )

def draw_bigger_rectangle(d: ImageDraw):
    d.polygon(
        (
            (field_lower_x, field_lower_y),
            (field_lower_x + field_offset_x, field_lower_y - field_height),
            (screen_width - field_lower_x - field_offset_x, field_lower_y - field_height),
            (screen_width - field_lower_x, field_lower_y)
        ),
        fill="green",
        outline="white",
        width=3
    )
    d.line(
        (
            (screen_width / 2, field_lower_y),
            (screen_width / 2, field_lower_y - field_height)
        ),
        width=3,
        fill="white"
    )

def draw_circle(d: ImageDraw, center: tuple, radius: int, fill: str):
    """Função auxiliar para desenhar círculos, já que ImageDraw não possui o método 'circle'."""
    x, y = center
    d.ellipse(
        (x - radius, y - radius, x + radius, y + radius),
        fill=fill,
        outline="white"
    )

