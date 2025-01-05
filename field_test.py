import math
import random
from PIL import Image, ImageDraw

##############################################################################
#                         CONSTANTES DO CAMPO (FIFA)
##############################################################################

FIELD_LENGTH = 105.0  # comprimento (em metros)
FIELD_WIDTH  = 68.0   # largura (em metros)

# Quatro cantos do retângulo REAL (sistema do campo)
pts_src = [
    (0.0,    0.0),    # canto superior esquerdo
    (105.0,  0.0),    # canto superior direito
    (0.0,    68.0),   # canto inferior esquerdo
    (105.0,  68.0)    # canto inferior direito
]

# Agora vamos definir um trapézio "maior" na imagem.
# Antes era algo como (300,200), (700,200), (100,450), (900,450).
# Vamos expandir para uma imagem maior e deixar o campo também mais aberto.
#
pts_dst = [
    (250.0, 150.0),   # top-left  (onde vai (0,0))
    (950.0, 150.0),   # top-right (onde vai (105,0))
    (100.0, 650.0),   # bottom-left  (onde vai (0,68))
    (1100.0, 650.0)   # bottom-right (onde vai (105,68))
]

##############################################################################
#                 CÁLCULO MANUAL DA HOMOGRAFIA (SEM NumPy)
##############################################################################
def compute_homography_4pts(src_pts, dst_pts):
    """
    Calcula os 8 parâmetros [h0..h7] da homografia 3x3
    (assumindo h8=1). Retorna lista [h0,h1,h2, h3,h4,h5, h6,h7].
    """
    A = []
    B = []
    for i in range(4):
        x, y = src_pts[i]
        X, Y = dst_pts[i]
        # Eq (X) e (Y):
        #   X = (h0*x + h1*y + h2) / (h6*x + h7*y + 1)
        #   Y = (h3*x + h4*y + h5) / (h6*x + h7*y + 1)
        # rearranjando cada uma dá 2 equações lineares.
        row1 = [ x, y, 1, 0, 0, 0, -x*X, -y*X ]
        B.append(X)
        row2 = [ 0, 0, 0, x, y, 1, -x*Y, -y*Y ]
        B.append(Y)
        A.append(row1)
        A.append(row2)

    h = solve_8x8(A, B)  # [h0..h7]
    return h

def solve_8x8(A, B):
    """
    Resolve o sistema linear 8x8 A*h = B por eliminação Gaussiana.
    A = list of lists (8x8), B = list(8).
    Retorna list(8) com a solução.
    """
    A_ = [row[:] for row in A]
    B_ = B[:]
    n = 8

    # Forward elimination
    for c in range(n):
        # achar pivô
        pivot = c
        maxval = abs(A_[c][c])
        for r in range(c+1, n):
            if abs(A_[r][c]) > maxval:
                pivot = r
                maxval = abs(A_[r][c])
        # se pivot != c, trocar
        if pivot != c:
            A_[c], A_[pivot] = A_[pivot], A_[c]
            B_[c], B_[pivot] = B_[pivot], B_[c]

        diag = A_[c][c]
        if abs(diag) < 1e-12:
            raise ValueError("Sistema degenerado ao encontrar homografia")

        # normalizar linha pivot
        for cc in range(c, n):
            A_[c][cc] /= diag
        B_[c] /= diag

        # Eliminar abaixo
        for r in range(c+1, n):
            factor = A_[r][c]
            for cc in range(c, n):
                A_[r][cc] -= factor * A_[c][cc]
            B_[r] -= factor * B_[c]

    # Back-substitution
    for c in range(n-1, -1, -1):
        for r in range(c-1, -1, -1):
            factor = A_[r][c]
            A_[r][c] = 0
            B_[r] -= factor * B_[c]

    return B_

##############################################################################
#        FUNÇÃO PARA PROJETAR PONTOS (x,y) --> (X,Y) COM A HOMOGRAFIA
##############################################################################
def project_point(H, x, y):
    """
    Aplica a homografia (h0..h7, h8=1) ao ponto (x,y).
    Retorna (X, Y).
    """
    h0,h1,h2,h3,h4,h5,h6,h7 = H
    denom = (h6*x + h7*y + 1.0)
    if abs(denom) < 1e-14:
        return (None, None)
    X = (h0*x + h1*y + h2) / denom
    Y = (h3*x + h4*y + h5) / denom
    return (X, Y)

##############################################################################
#        FUNÇÕES PARA DESENHAR AS LINHAS DO CAMPO (OFICIAIS FIFA)
##############################################################################

def draw_segment(draw, H, x1, y1, x2, y2, color="white", width=3):
    p1 = project_point(H, x1, y1)
    p2 = project_point(H, x2, y2)
    if None not in p1 and None not in p2:
        draw.line([p1, p2], fill=color, width=width)

def draw_rectangle(draw, H, xmin, ymin, xmax, ymax, color="white", width=3):
    c1 = project_point(H, xmin, ymin)
    c2 = project_point(H, xmax, ymin)
    c3 = project_point(H, xmax, ymax)
    c4 = project_point(H, xmin, ymax)
    if None not in c1 and None not in c2 and None not in c3 and None not in c4:
        draw.line([c1, c2, c3, c4, c1], fill=color, width=width)

def draw_circle(draw, H, cx, cy, radius, color="white", width=3, segments=60):
    pts = []
    for i in range(segments):
        ang = 2*math.pi*i/segments
        xx = cx + radius*math.cos(ang)
        yy = cy + radius*math.sin(ang)
        pp = project_point(H, xx, yy)
        if None not in pp:
            pts.append(pp)
    if len(pts) > 2:
        pts.append(pts[0])  # fecha
        draw.line(pts, fill=color, width=width)

##############################################################################
#                 DESENHAR O CAMPO FIFA EM PERSPECTIVA
##############################################################################
def draw_fifa_field(draw, H):
    """
    Desenha o campo (105×68) em perspectiva:
     - gramado
     - linhas laterais, fundo
     - meio-campo, círculo central
     - grandes áreas, pequenas áreas
     - marca do pênalti
    """
    # Gramado (quatro cantos)
    corners = [(0,0), (FIELD_LENGTH,0), (FIELD_LENGTH,FIELD_WIDTH), (0,FIELD_WIDTH)]
    poly = []
    for (x,y) in corners:
        p = project_point(H, x, y)
        if None not in p:
            poly.append(p)
    if len(poly) == 4:
        draw.polygon(poly, fill="green")

    # Linhas de fundo e laterais
    draw_segment(draw, H, 0,   0,   0,   FIELD_WIDTH)
    draw_segment(draw, H, FIELD_LENGTH, 0, FIELD_LENGTH, FIELD_WIDTH)
    draw_segment(draw, H, 0, 0, FIELD_LENGTH, 0)
    draw_segment(draw, H, 0, FIELD_WIDTH, FIELD_LENGTH, FIELD_WIDTH)

    # Meio-campo
    mid_x = FIELD_LENGTH/2.0
    draw_segment(draw, H, mid_x, 0, mid_x, FIELD_WIDTH)

    # Círculo central
    draw_circle(draw, H, cx=52.5, cy=34, radius=9.15, segments=60)

    # Grandes áreas
    draw_rectangle(draw, H,
                   xmin=0,        xmax=16.5,
                   ymin=34-20.16, ymax=34+20.16)
    draw_rectangle(draw, H,
                   xmin=105-16.5, xmax=105,
                   ymin=34-20.16, ymax=34+20.16)

    # Pequenas áreas
    draw_rectangle(draw, H,
                   xmin=0,  xmax=5.5,
                   ymin=34-9.16, ymax=34+9.16)
    draw_rectangle(draw, H,
                   xmin=105-5.5, xmax=105,
                   ymin=34-9.16, ymax=34+9.16)

    # Marcas do pênalti
    pen_left  = project_point(H, 11.0, 34.0)
    pen_right = project_point(H, 94.0, 34.0)
    r_px = 3
    if None not in pen_left:
        draw.ellipse([pen_left[0]-r_px, pen_left[1]-r_px,
                      pen_left[0]+r_px, pen_left[1]+r_px],
                     fill="white")
    if None not in pen_right:
        draw.ellipse([pen_right[0]-r_px, pen_right[1]-r_px,
                      pen_right[0]+r_px, pen_right[1]+r_px],
                     fill="white")

##############################################################################
#                  DESENHO DA PLATEIA (ARQUIBANCADA)
##############################################################################
def draw_crowd(draw, box, rows=4, cols=40):
    (left, top, right, bottom) = box
    draw.rectangle([left, top, right, bottom], fill=(80,80,80))
    
    w = right - left
    h = bottom - top
    dx = w / float(cols)
    dy = h / float(rows)
    head_r = 3

    for r in range(rows):
        for c in range(cols):
            cx = left + (c+0.5)*dx
            cy = top  + (r+0.5)*dy
            # Varia um pouquinho
            cx += random.uniform(-dx*0.3, dx*0.3)
            cy += random.uniform(-dy*0.3, dy*0.3)
            color_head = random.choice(["white","beige","brown","pink","lightgray"])
            draw.ellipse([cx-head_r, cy-head_r, cx+head_r, cy+head_r], fill=color_head)

##############################################################################
#                FUNÇÕES PARA DESENHAR JOGADORES E BOLA
##############################################################################
def draw_player(draw, H, x_real, y_real, shirt_color="blue"):
    p = project_point(H, x_real, y_real)
    if None not in p:
        X, Y = p
        # Jogador simples
        head_size = 8
        # cabeça
        draw.ellipse([(X - head_size/2, Y - head_size),
                      (X + head_size/2, Y)],
                     fill="beige")
        # camisa
        draw.rectangle([(X - 5, Y), (X + 5, Y + 10)], fill=shirt_color)
        # shorts
        draw.rectangle([(X - 5, Y + 10), (X + 5, Y + 15)], fill="black")
        # pernas
        draw.line([(X - 2, Y + 15), (X - 2, Y + 25)], fill="black", width=2)
        draw.line([(X + 2, Y + 15), (X + 2, Y + 25)], fill="black", width=2)

def draw_ball(draw, H, x_real, y_real, radius_px=4):
    p = project_point(H, x_real, y_real)
    if None not in p:
        X, Y = p
        draw.ellipse([X - radius_px, Y - radius_px,
                      X + radius_px, Y + radius_px],
                     fill="white", outline="black")

##############################################################################
#                DESENHAR GOALS (TRAVES) ALTAS
##############################################################################
def draw_goals(draw, H, height_m=2.44, width_m=7.32):
    """
    Desenha gols mais "altos" na imagem.
    - No campo real, a trave tem 2.44 m de altura e 7.32 m de largura. 
      Mas aqui vamos fingir que são "mais altas" — ex. 4 m no 'mundo real',
      para que a projeção as faça parecer bem altas.
    - A posição do gol é na linha de fundo, centrado em y=34.
    - height_m: podemos usar 4.0 ou 5.0 para simular "altas".
    """

    # Gol esquerdo: 
    #    no x=0, centrado em y=34, 
    #    vai de y=34 - (width_m/2) até y=34 + (width_m/2) (largura no chão)
    #    e altura = height_m (vertical).
    # Vamos discretizar 4 cantos e desenhar um retângulo.

    y_top = 34 - (width_m / 2)
    y_bottom = 34 + (width_m / 2)

    # Subimos a trave: (x=0), mas há a parte de cima (x=0, y=34±...),
    # e a parte de trás? Precisamos simular que a trave recua um pouco no 'x' negativo.
    # Mas para simplificar, vamos desenhar só um retângulo vertical "atrás" da linha.

    # 4 cantos:
    # canto inferior esquerdo = (x=-0.5, y=y_bottom)
    # canto inferior direito  = (x=0,    y=y_bottom)
    # canto superior direito  = (x=0,    y=y_top)
    # canto superior esquerdo = (x=-0.5, y=y_top)
    # mas com height_m "custom" para ficar mais alto.

    # Se quisermos a trave + alta, trocamos height_m=4.0, etc.
    x_inner = 0.0
    x_outer = -0.5  # recuo de 0.5 m para a "profundidade" do gol
    # Ou se quiser recuo maior, -1.0

    # Ajustar a parte de cima com +height_m no EIXO Z seria ideal em 3D,
    # mas aqui não temos 3D. Então vamos fingir que "subir" no "desenho" 
    # é outro truque.  Para mostrar "altura", 
    # iremos deslocar o ponto superior "um pouco pra cima" no mundo real (y < 0).
    # Entretanto, sem uma simulação 3D real, não fica perfeito.
    # SIMPLIFICANDO: 
    # desenhar retângulo no plano do chão, mas com height_m substituindo
    # a "distância" no eixo y. Assim, fica "mais alto" no 2D.
    # (Na verdade, é só um "gol maior" no chão.)
    
    # Vamos apenas tornar o "gol" no 2D maior no 'vertical do y' 
    # (como se fosse mais largo no campo).
    
    # Então, definimos y_top' = 34 - (width_m/2) - "height_m"
    # e y_bottom' = 34 + (width_m/2)
    # Assim o retângulo é maior verticalmente.
    
    # (em metros)
    y_top_alt = (34 - (width_m/2) - height_m)
    y_bottom_alt = (34 + (width_m/2))

    # Então definimos 4 cantos do retângulo do gol esquerdo:
    corners_left = [
        (x_outer, y_bottom_alt),  # inferir esq
        (x_inner, y_bottom_alt),  # inferir dir
        (x_inner, y_top_alt),     # sup dir
        (x_outer, y_top_alt)      # sup esq
    ]
    
    # Projeta e desenha polígono
    poly_left = []
    for (xx,yy) in corners_left:
        p = project_point(H, xx, yy)
        if None not in p:
            poly_left.append(p)
    if len(poly_left) == 4:
        draw.polygon(poly_left, fill=(100,100,100))

    # Gol direito (x=105):
    # mesmo raciocínio, mas com x_inner=105, x_outer=105+0.5
    x_inner = 105.0
    x_outer = 105.5
    corners_right = [
        (x_inner, y_bottom_alt),
        (x_outer, y_bottom_alt),
        (x_outer, y_top_alt),
        (x_inner, y_top_alt)
    ]
    poly_right = []
    for (xx,yy) in corners_right:
        p = project_point(H, xx, yy)
        if None not in p:
            poly_right.append(p)
    if len(poly_right) == 4:
        draw.polygon(poly_right, fill=(100,100,100))

##############################################################################
#                                MAIN
##############################################################################

def main():
    # 1) Calcular homografia para nosso novo trapezoide
    h_coefs = compute_homography_4pts(pts_src, pts_dst)  # [h0..h7]

    # 2) Criar imagem maior
    W, H_img = 1200, 800
    img = Image.new("RGB", (W, H_img), "white")
    draw = ImageDraw.Draw(img)

    # 3) Arquibancada (parte de cima)
    stands_box = (0, 0, W, 160)
    draw_crowd(draw, stands_box, rows=5, cols=60)

    # 4) Faixas coloridas (azul + vermelha)
    bar_height = 40
    top_bar_y = stands_box[3]  # 160
    draw.rectangle([0, top_bar_y, W, top_bar_y + bar_height], fill="blue")
    draw.rectangle([0, top_bar_y + bar_height, W, top_bar_y + bar_height + 10], fill="red")

    # 5) Desenhar o campo FIFA (em perspectiva)
    global h_vec
    h_vec = h_coefs
    draw_fifa_field(draw, h_vec)

    # 6) Desenhar gols "altos"
    #    Vamos usar, por exemplo, height_m=4.0 (traves de 4m)
    #    A largura continua ~7.32 m, mas você pode ajustar se quiser "extra-largo".
    draw_goals(draw, h_vec, height_m=4.0, width_m=7.32)

    # 7) Jogadores em algumas posições
    draw_player(draw, h_vec, x_real=10,   y_real=30, shirt_color="blue")
    draw_player(draw, h_vec, x_real=15,   y_real=40, shirt_color="blue")
    draw_player(draw, h_vec, x_real=52.5, y_real=20, shirt_color="red")
    draw_player(draw, h_vec, x_real=90,   y_real=34, shirt_color="green")
    draw_player(draw, h_vec, x_real=90,   y_real=50, shirt_color="yellow")

    # 8) Bola
    draw_ball(draw, h_vec, x_real=12, y_real=30, radius_px=6)

    # 9) Salvar
    img.save("campo_fifa_expandido_balizas_altas.png")
    print("OK: campo_fifa_expandido_balizas_altas.png gerada!")

if __name__ == "__main__":
    main()
