from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import random

# ===========================================================================
# Configurações Gerais
# ===========================================================================
WIDTH = 1280      # Largura do “vídeo”
HEIGHT = 720      # Altura do “vídeo”
DURATION = 60     # Duração de cada quadro (ms)
N_FRAMES = 80     # Número total de quadros da animação

# ===========================================================================
# Parâmetros da Jogada
# ===========================================================================
#
# O fluxo será:
#  1) Jogador 1 cobra lateral (lado esquerdo).
#  2) Passes entre 6 jogadores (J1, J2, J3, J4, J5, J6).
#  3) J6 arremata para o gol.
#  4) Muda a câmera para a visão frontal do goleiro ao entrar o gol.
#

# Em frames (exemplo):
#   0-5   : Jogador 1 faz o arremesso lateral.
#   5-15  : Bola vai de J1 -> J2.
#   15-25 : Bola vai de J2 -> J3.
#   25-35 : Bola vai de J3 -> J4.
#   35-45 : Bola vai de J4 -> J5.
#   45-55 : Bola vai de J5 -> J6.
#   55-60 : J6 avança com a bola.
#   60-65 : J6 chuta -> Gol
#   65-80 : Câmera frontal do goleiro, bola na rede.

cobranca_lateral_end = 5
passes_frames = [5, 15, 25, 35, 45, 55]  # momentos em que termina cada passe
final_shot_start = 55
final_shot_end = 60
goal_frame = 65  # a partir daqui, câmera frontal

# Posições iniciais aproximadas dos jogadores que vão tocar a bola
players_positions = [
    (150, 90),  # J1 (cobra o lateral do lado esquerdo)
    (300, 250),  # J2
    (400, 350),  # J3
    (600, 300),  # J4
    (750, 380),  # J5
    (900, 340),  # J6 (quem finaliza)
]

# Posição aproximada do goleiro adversário (lado direito)
goalkeeper_pos = (1150, 360)

# Defensores adversários (estáticos ou com pequena movimentação)
defenders_positions = [
    [1000, 200],  # D1
    [1050, 520],  # D2
    [1100, 300],  # D3
]

# ===========================================================================
# Funções Auxiliares
# ===========================================================================

def draw_field_gradient(img):
    """
    Aplica um gradiente verde no fundo para simular grama.
    """
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        # Variação de cor: verde “escuro” para verde “claro”
        ratio = y / HEIGHT
        r = int(34  - (34 - 0)*ratio)
        g = int(139 - (139 - 100)*ratio)
        b = int(34  - (34 - 20)*ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

def draw_stadium_elements(draw):
    """
    Desenha:
      - as quatro linhas laterais brancas do campo,
      - a linha do meio,
      - o círculo central,
      - as duas grandes áreas,
      - uma faixa simulando torcida no topo.
    """
    # 1) Linhas laterais do campo (contorno)
    line_width = 4
    # Topo
    draw.line([(0, 0), (WIDTH, 0)], fill="white", width=line_width)
    # Base
    draw.line([(0, HEIGHT), (WIDTH, HEIGHT)], fill="white", width=line_width)
    # Lateral esquerda
    draw.line([(0, 0), (0, HEIGHT)], fill="white", width=line_width)
    # Lateral direita
    draw.line([(WIDTH, 0), (WIDTH, HEIGHT)], fill="white", width=line_width)

    # 2) Linha do meio
    draw.line([(WIDTH/2, 0), (WIDTH/2, HEIGHT)], fill="white", width=3)
    
    # 3) Círculo central
    center_x, center_y = WIDTH/2, HEIGHT/2
    radius = 80
    draw.ellipse([(center_x - radius, center_y - radius),
                  (center_x + radius, center_y + radius)],
                 outline="white", width=3)
    
    # 4) Grandes áreas
    # Lado esquerdo (onde o time que cobra lateral está)
    draw.rectangle([(0+50, HEIGHT/2 - 100), (0+150, HEIGHT/2 + 100)],
                   outline="white", width=3)
    # Lado direito (gol adversário)
    draw.rectangle([(WIDTH-150, HEIGHT/2 - 100), (WIDTH-50, HEIGHT/2 + 100)],
                   outline="white", width=3)
    
    # 5) Simula torcida no topo
    draw.rectangle([(0, 0), (WIDTH, 60)], fill=(200, 200, 200))
    draw.text((WIDTH//2 - 40, 20), "Torcida", fill="black")

def draw_shadow(draw, x, y, radius=20, offset=5):
    """
    Desenha uma "sombra" elíptica por trás do jogador,
    para dar impressão de volume.
    """
    shadow_color = (0, 0, 0, 50)  # preto semi-transparente
    draw.ellipse([
        (x - radius + offset, y - radius + offset),
        (x + radius + offset, y + radius + offset)
    ], fill=shadow_color)

def draw_player(draw, x, y, color, label='adilson'):
    """
    Desenha um jogador com um círculo colorido + sombra básica.
    """
    radius = 20
    
    # Sombra
    draw_shadow(draw, x, y, radius=radius, offset=5)
    
    # Círculo do jogador
    draw.ellipse([(x - radius, y - radius), (x + radius, y + radius)],
                 fill=color, outline="black", width=2)
    
    # Opcional: texto acima da cabeça
    if label:
        draw.text((x - 10, y - 35), label, fill="white")

def draw_ball(draw, x, y):
    """
    Desenha a bola como um pequeno círculo branco com contorno e sombra.
    """
    radius = 10
    # Sombra
    draw_shadow(draw, x, y, radius=radius, offset=3)
    # Bola
    draw.ellipse([(x - radius, y - radius), (x + radius, y + radius)],
                 fill="white", outline="black", width=2)

def interpolate_position(current_frame, start_frame, end_frame, start_pos, end_pos):
    """
    Interpola (linearmente) a posição entre start_pos e end_pos 
    conforme o frame atual estiver entre start_frame e end_frame.
    """
    if current_frame <= start_frame:
        return start_pos
    if current_frame >= end_frame:
        return end_pos
    
    total = end_frame - start_frame
    progress = current_frame - start_frame
    alpha = progress / float(total)
    x = start_pos[0] + alpha * (end_pos[0] - start_pos[0])
    y = start_pos[1] + alpha * (end_pos[1] - start_pos[1])
    return (x, y)

def camera_transform(img, frame):
    """
    Transforma a imagem para simular a troca de câmera.
    1) Até goal_frame: visão ampla (imagem original).
    2) A partir de goal_frame: visão frontal do goleiro (zoom no gol).
    """
    if frame < goal_frame:
        # Visão ampla (sem recortes)
        return img
    else:
        # Visão frontal do goleiro -> recorta a região próxima ao gol
        crop_left = WIDTH - 400
        crop_top = HEIGHT//2 - 250
        crop_right = WIDTH
        crop_bottom = HEIGHT//2 + 250
        
        # Garantir que não estoure os limites
        crop_left = max(crop_left, 0)
        crop_top = max(crop_top, 0)
        crop_right = min(crop_right, WIDTH)
        crop_bottom = min(crop_bottom, HEIGHT)
        
        cropped = img.crop((crop_left, crop_top, crop_right, crop_bottom))
        
        # Redimensionar de volta para o tamanho original (zoom)
        return cropped.resize((WIDTH, HEIGHT), resample=Image.BICUBIC)

def random_defenders_movement(defenders, frame):
    """
    Dá uma movimentação aleatória (pequena) aos defensores,
    para parecer que estão se mexendo de leve.
    """
    # A cada frame, pequenos deslocamentos +/- 1 px
    if frame % 5 == 0:  # a cada 5 frames
        for i in range(len(defenders)):
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            defenders[i][0] += dx
            defenders[i][1] += dy

def animate_throw_in(draw, frame):
    """
    Desenha o jogador 1 fazendo a cobrança de lateral nos primeiros frames,
    com a bola acima da cabeça. Retorna um alpha (0..1) que indica 
    o 'progresso' da descida da bola.
    """
    if frame <= cobranca_lateral_end:
        # Ex.: bola indo de 40px acima da cabeça (frame 0)
        #      até a posição normal (frame cobranca_lateral_end).
        alpha = frame / float(cobranca_lateral_end)
        return alpha
    return 1.0

# ===========================================================================
# Geração dos Quadros
# ===========================================================================
frames = []

# Estado local para os defensores (movimentação leve)
local_defenders = [pos[:] for pos in defenders_positions]

for frame_index in range(N_FRAMES):
    # 1) Criar imagem base
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    
    # 2) Aplicar gradiente (grama)
    draw_field_gradient(img)
    
    # 3) Desenhar linhas, áreas e elementos do estádio
    draw = ImageDraw.Draw(img)
    draw_stadium_elements(draw)
    
    # 4) Movimentar defensores (pequenas variações)
    random_defenders_movement(local_defenders, frame_index)
    
    # 5) Desenhar equipe adversária (defensores + goleiro)
    # Defensores
    for j, (dx, dy) in enumerate(local_defenders):
        draw_player(draw, dx, dy, (220, 20, 60), label=f"D{j+1}")
    
    # Goleiro (leve movimento em determinados frames)
    gk_x, gk_y = goalkeeper_pos
    if final_shot_end <= frame_index < goal_frame:
        # Se mexendo antes do chute chegar
        gk_x += math.sin(frame_index * 0.2) * 5
    elif frame_index >= goal_frame:
        # No close do gol (pós-chute)
        gk_y += math.sin(frame_index * 0.3) * 5
    
    draw_player(draw, gk_x, gk_y, (220, 20, 60), label="GK")

    # 6) Desenhar time atacante (J1..J6) + posição da bola
    ball_pos = None
    
    # Animação do arremesso lateral (primeiros frames)
    throw_alpha = animate_throw_in(draw, frame_index)  # 0..1

    # Desenhar jogadores atacantes
    for i, (px, py) in enumerate(players_positions):
        # Pequena variação (simular passos)
        offset = math.sin(frame_index * 0.2 + i) * 3
        draw_player(draw, px, py + offset, (30, 144, 255), label=f"A{i+1}")
    
    # Definir posição da bola em cada momento:
    # a) 0 -> 5: bola no J1, descendo da cabeça até o pé
    if frame_index < passes_frames[0]:
        j1x, j1y = players_positions[0]
        offset = 40 * (1 - throw_alpha)  # 40px a 0px
        ball_pos = (j1x, j1y - offset)
    
    # b) Passes de jogador i -> i+1
    for i in range(len(passes_frames) - 1):
        start_f = passes_frames[i]
        end_f = passes_frames[i+1]
        if start_f <= frame_index < end_f:
            start_pos = players_positions[i]
            end_pos = players_positions[i+1]
            ball_pos = interpolate_position(frame_index, start_f, end_f, start_pos, end_pos)
            break
    
    # c) 55 -> 60: J6 avança em direção à área
    if final_shot_start <= frame_index < final_shot_end:
        start_pos = players_positions[-1]  # J6
        end_pos = (WIDTH - 150, HEIGHT//2) # chegando perto do gol
        ball_pos = interpolate_position(frame_index, final_shot_start, final_shot_end, start_pos, end_pos)
    
    # d) 60 -> 65: Chute final ao gol
    if final_shot_end <= frame_index < goal_frame:
        start_pos = (WIDTH - 150, HEIGHT//2)
        end_pos = (WIDTH - 70, HEIGHT//2)  # dentro do gol
        ball_pos = interpolate_position(frame_index, final_shot_end, goal_frame, start_pos, end_pos)
    
    # e) >= 65: bola já está dentro do gol
    if frame_index >= goal_frame:
        ball_pos = (WIDTH - 60, HEIGHT//2)
    
    # Desenha a bola se houver posição definida
    if ball_pos is not None:
        bx, by = ball_pos
        draw_ball(draw, bx, by)
    
    # 7) Aplicar transformação de câmera (ampla ou frontal)
    transformed_img = camera_transform(img, frame_index)
    
    # 8) Converter para RGB e armazenar
    frames.append(transformed_img.convert("RGB"))

# ===========================================================================
# Exportar para GIF
# ===========================================================================
frames[0].save(
    "futebol_animacao_lateral_realista.gif",
    save_all=True,
    append_images=frames[1:],
    loop=0,
    duration=DURATION
)

print("GIF 'futebol_animacao_lateral_realista.gif' gerado com sucesso!")