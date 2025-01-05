import math
import random
from PIL import Image, ImageDraw

##############################################################################
#                       PARÂMETROS DA ANIMAÇÃO
##############################################################################
FPS = 20                         # quadros por segundo
TOTAL_FRAMES = 240             # 240 frames → 60s
FRAME_DURATION_MS = 250         # 1/4s por frame
WIDTH, HEIGHT = 1280, 720

# PONTOS PARA CAMPO FIFA COM HOMOGRAFIA
FIELD_LENGTH = 105.0
FIELD_WIDTH  = 68.0
pts_src = [(0,0),(105,0),(0,68),(105,68)]
pts_dst = [
    (400.0, 150.0),  # topo esq
    (880.0, 150.0),  # topo dir
    (200.0, 600.0),  # base esq
    (1080.0,600.0)   # base dir
]

def compute_homography_4pts(src_pts, dst_pts):
    A,B=[],[]
    for i in range(4):
        x,y=src_pts[i]
        X,Y=dst_pts[i]
        A.append([x,y,1,0,0,0,-x*X,-y*X]); B.append(X)
        A.append([0,0,0,x,y,1,-x*Y,-y*Y]); B.append(Y)
    return solve_8x8(A,B)

def solve_8x8(A, B):
    A_=[row[:] for row in A]
    B_=B[:]
    n=8
    for c in range(n):
        pivot=c
        maxval=abs(A_[c][c])
        for r in range(c+1,n):
            if abs(A_[r][c])>maxval:
                pivot=r
                maxval=abs(A_[r][c])
        if pivot!=c:
            A_[c],A_[pivot]=A_[pivot],A_[c]
            B_[c],B_[pivot]=B_[pivot],B_[c]
        diag=A_[c][c]
        if abs(diag)<1e-14:
            raise ValueError("Homografia degenerada.")
        for cc in range(c,n):
            A_[c][cc]/=diag
        B_[c]/=diag
        for r in range(c+1,n):
            factor=A_[r][c]
            for cc in range(c,n):
                A_[r][cc]-=factor*A_[c][cc]
            B_[r]-=factor*B_[c]
    for c in range(n-1,-1,-1):
        for r in range(c-1,-1,-1):
            factor=A_[r][c]
            A_[r][c]=0
            B_[r]-=factor*B_[c]
    return B_


def project_point(h, x, y): 
    #explain this function
    # h is the homography matrix
    # x,y are the coordinates of the point in the source image
    # returns the coordinates of the point in the destination image
    # if the point is outside the image, returns (None,None)
    # h is a list of 8 elements
    # h0,h1,h2,h3,h4,h5,h6,h7
    # h0*x + h1*y + h2
    # h3*x + h4*y + h5
    # h6*x + h7*y + 1
    # X = (h0*x + h1*y + h2) / (h6*x + h7*y + 1)
    # Y = (h3*x + h4*y + h5) / (h6*x + h7*y + 1)
    (h0,h1,h2,h3,h4,h5,h6,h7)=h
    denom=h6*x+h7*y+1.0
    if abs(denom)<1e-14:
        return (None,None)
    X=(h0*x + h1*y + h2)/denom
    Y=(h3*x + h4*y + h5)/denom
    return (X,Y)

H_persp= compute_homography_4pts(pts_src,pts_dst)

##############################################################################
#                DESENHO ARQUIBANCADA, FUNDO, CAMPO
##############################################################################

def draw_crowd_and_bg(draw):
    stands_h=100
    draw.rectangle([0,0, WIDTH, stands_h], fill=(120,120,120))
    # torcedores
    rows=3
    cols=60
    dx=WIDTH//cols
    dy=stands_h//rows
    rr=3
    for r in range(rows):
        for c in range(cols):
            cx=c*dx+dx//2
            cy=r*dy+dy//2
            draw.ellipse([cx-rr,cy-rr,cx+rr,cy+rr], fill="white")

    # Faixa azul
    bar1=40
    draw.rectangle([0, stands_h, WIDTH, stands_h+bar1], fill="blue")
    stands_h+=bar1
    # Faixa vermelha
    bar2=20
    draw.rectangle([0, stands_h, WIDTH, stands_h+bar2], fill="red")
    stands_h+=bar2

    # Resto verde
    draw.rectangle([0, stands_h, WIDTH, HEIGHT], fill=(20,100,20))

def draw_field_fifa(draw):
    # gramado
    corners=[(0,0),(105,0),(105,68),(0,68)]
    poly=[]
    for (xx,yy) in corners:
        p=project_point(H_persp, xx,yy)
        if None not in p:
            poly.append(p)
    if len(poly)==4:
        draw.polygon(poly, fill=(30,150,50))

    def seg(x1,y1,x2,y2):
        p1=project_point(H_persp,x1,y1)
        p2=project_point(H_persp,x2,y2)
        if None not in p1 and None not in p2:
            draw.line([p1,p2], fill="white", width=3)

    seg(0,0,0,68)
    seg(105,0,105,68)
    seg(0,0,105,0)
    seg(0,68,105,68)
    seg(52.5,0, 52.5,68)

    # círculo central
    def circle(cx,cy,r, segs=60):
        pts=[]
        for i in range(segs):
            ang=2*math.pi*i/segs
            xx=cx+r*math.cos(ang)
            yy=cy+r*math.sin(ang)
            pp=project_point(H_persp, xx,yy)
            if None not in pp:
                pts.append(pp)
        if len(pts)>2:
            pts.append(pts[0])
            draw.line(pts, fill="white", width=3)
    circle(52.5,34,9.15)

    # áreas
    def rect(xmin,ymin,xmax,ymax):
        c1=project_point(H_persp,xmin,ymin)
        c2=project_point(H_persp,xmax,ymin)
        c3=project_point(H_persp,xmax,ymax)
        c4=project_point(H_persp,xmin,ymax)
        if all(pt[0] is not None for pt in [c1,c2,c3,c4]):
            draw.line([c1,c2,c3,c4,c1], fill="white", width=3)
    rect(0,34-20.16,16.5,34+20.16)
    rect(105-16.5,34-20.16,105,34+20.16)
    rect(0,34-9.16,5.5,34+9.16)
    rect(105-5.5,34-9.16,105,34+9.16)

    # ponto penalti
    def dot(px,py):
        p=project_point(H_persp, px,py)
        if None not in p:
            rr=4
            draw.ellipse([p[0]-rr,p[1]-rr, p[0]+rr,p[1]+rr], fill="white")
    dot(11,34)
    dot(94,34)

def draw_player_persp(draw, x_m, y_m, shirt="blue"):
    p=project_point(H_persp, x_m,y_m)
    if None not in p:
        (X,Y)=p
        head=8
        draw.ellipse([X-head/2,Y-head, X+head/2,Y], fill="beige")
        draw.rectangle([X-5,Y, X+5,Y+12], fill=shirt)
        draw.rectangle([X-5,Y+12, X+5,Y+17], fill="black")
        draw.line([X-2,Y+17, X-2,Y+27], fill="black", width=3)
        draw.line([X+2,Y+17, X+2,Y+27], fill="black", width=3)

def draw_ball_persp(draw, x_m, y_m, r=5):
    p=project_point(H_persp, x_m,y_m)
    if None not in p:
        (X,Y)=p
        draw.ellipse([X-r,Y-r, X+r,Y+r], fill="white", outline="black")

##############################################################################
#     CÂMERA FRONTAL
##############################################################################

def draw_scene_frontal(draw):
    draw.rectangle([0,0,WIDTH,HEIGHT], fill=(30,130,30))
    w=100
    h=120
    gx0=WIDTH-w
    gx1=WIDTH
    gy0=(HEIGHT//2)-60
    gy1=gy0+h
    draw.rectangle([gx0,gy0,gx1,gy1], fill=(160,160,160))

def draw_player_frontal(draw, x_rel, y_rel, shirt="blue"):
    head=12
    X,Y=x_rel,y_rel
    draw.ellipse([X-head/2,Y-head, X+head/2,Y], fill="beige")
    draw.rectangle([X-6,Y, X+6,Y+15], fill=shirt)
    draw.rectangle([X-6,Y+15, X+6,Y+20], fill="black")
    draw.line([X-3,Y+20, X-3,Y+30], fill="black", width=3)
    draw.line([X+3,Y+20, X+3,Y+30], fill="black", width=3)

def draw_ball_frontal(draw, x_rel, y_rel, r=7):
    draw.ellipse([x_rel-r,y_rel-r, x_rel+r,y_rel+r],
                 fill="white", outline="black")

##############################################################################
#   JOGADORES SE MOVEM, J6 PERTO DA BALIZA
##############################################################################

def lerp(a,b,t): return a+(b-a)*t

# 6 jogadores time A
playersA_start = [
    (5,30),
    (15,40),
    (25,34),
    (40,20),
    (60,50),
    (80,34)  # j6
]
playersA_end   = [
    (8,32),
    (18,38),
    (28,36),
    (45,25),
    (64,48),
    (100,35) # j6 final
]
gk_start = (105,34)
gk_end   = (105,36)

def get_playerA_pos(i, frame):
    t= frame/140.0  # movemos só até frame 140, pois 140~150 será fade out
    if t>1: t=1
    (x1,y1)=playersA_start[i]
    (x2,y2)=playersA_end[i]
    return (lerp(x1,x2,t), lerp(y1,y2,t))

def get_gk_pos(frame):
    t= frame/140.0
    if t>1: t=1
    (x1,y1)= gk_start
    (x2,y2)= gk_end
    return (lerp(x1,x2,t), lerp(y1,y2,t))

def get_ball_persp(frame):
    path= playersA_end
    total_passes= len(path)-1 # 5
    frames_limit=140  # até 140
    frames_per_pass= frames_limit/total_passes
    pass_idx= int(frame//frames_per_pass)
    if pass_idx>=total_passes:
        pass_idx= total_passes-1
    frac_in = (frame - pass_idx*frames_per_pass)/frames_per_pass
    (x1,y1)= path[pass_idx]
    (x2,y2)= path[pass_idx+1]
    return (lerp(x1,x2, frac_in), lerp(y1,y2, frac_in))

def get_player6_frontal(frame_idx):
    # 150..160 => fade in
    local_f=frame_idx-160  # a ação real do chute ~160..239
    total_f= (240-160)
    if local_f<0: local_f=0
    t= local_f/total_f
    if t>1: t=1
    x1=200; y1=HEIGHT//2
    x2=210; y2=HEIGHT//2
    return (lerp(x1,x2,t), lerp(y1,y2,t))

def get_gk_frontal(frame_idx):
    local_f= frame_idx-160
    total_f=80
    if local_f<0: local_f=0
    t= local_f/total_f
    if t>1: t=1
    x1=WIDTH-90; y1=HEIGHT//2
    x2=WIDTH-85; y2=HEIGHT//2+10
    return (lerp(x1,x2,t), lerp(y1,y2,t))

def get_ball_frontal(frame_idx):
    # do frame 160..239
    local_f= frame_idx-160
    total_f=80
    if local_f<0: local_f=0
    t= local_f/total_f
    if t>1: t=1
    x1=200; y1=HEIGHT//2
    x2=WIDTH-110; y2=HEIGHT//2
    return (lerp(x1,x2,t), lerp(y1,y2,t))

##############################################################################
#      FADE OUT / FADE IN
##############################################################################

def blend_with_black(img, alpha):
    """
    Retorna uma nova imagem: blend da `img` com "black" 
    com fator alpha (0..1).
    alpha=0 => sem escurecer
    alpha=1 => totalmente preto
    """
    # Criar uma "black" do mesmo tamanho e usar Image.blend
    black_img = Image.new("RGB", img.size, "black")
    return Image.blend(img, black_img, alpha)

def blend_with_frontal(frontal_img, alpha):
    """
    Se quisermos "fade in" a frontal a partir de preto (por ex),
    alpha=0 => totalmente preto,
    alpha=1 => frontal_img
    """
    black_img = Image.new("RGB", frontal_img.size, "black")
    return Image.blend(black_img, frontal_img, alpha)

##############################################################################
#               GERA FRAMES
##############################################################################

def make_frame(idx):
    img= Image.new("RGB",(WIDTH,HEIGHT),(0,0,0))
    d= ImageDraw.Draw(img)

    # ***Fase 1***: 0..139 => Perspectiva normal
    # ***Fase 2***: 140..149 => fade out
    # ***Fase 3***: 150..159 => fade in frontal
    # ***Fase 4***: 160..239 => frontal

    if idx<=139:
        # Perspectiva normal
        draw_crowd_and_bg(d)
        draw_field_fifa(d)

        for iA in range(6):
            (px,py)= get_playerA_pos(iA,idx)
            draw_player_persp(d, px,py,"blue")
        (gx,gy)= get_gk_pos(idx)
        draw_player_persp(d, gx,gy, "red")
        (bx,by)= get_ball_persp(idx)
        draw_ball_persp(d, bx,by,5)

        return img

    elif 140<=idx<=149:
        # Cria a imagem do campo (perspectiva) em "estado final" do frame 139
        # mas a bola/jogadores também param de se mover (ou movem até 140).
        # Então chamamos as mesmas funcoes com frame=140
        temp_img= Image.new("RGB",(WIDTH,HEIGHT),"black")
        d2= ImageDraw.Draw(temp_img)
        draw_crowd_and_bg(d2)
        draw_field_fifa(d2)

        for iA in range(6):
            (px,py)= get_playerA_pos(iA,140)
            draw_player_persp(d2, px,py,"blue")
        (gx,gy)= get_gk_pos(140)
        draw_player_persp(d2, gx,gy, "red")
        (bx,by)= get_ball_persp(140)
        draw_ball_persp(d2, bx,by,5)

        # alpha = 0..1 em 10 quadros
        local_f= idx-140
        alpha= local_f/10.0
        # alpha=0 => sem escurecer, alpha=1 => total black
        final_img= blend_with_black(temp_img, alpha)
        return final_img

    elif 150<=idx<=159:
        # camera frontal "fade in"
        # geramos a imagem frontal do frame 150? 
        # mas animamos jogador6, goleiro e bola?
        # decerto tudo "congelado" no "início" da frontal? 
        # ou podemos ir movendo? 
        # Vamos supor que 150..159 => from black => frontal do frame 160?
        # Para simplificar, usar "frontal do frame 160" e fazer fade in
        # pois 160 e adiante é a "câmera frontal real".

        # Gerar a camera frontal do frame=160
        temp_img= Image.new("RGB",(WIDTH,HEIGHT),"black")
        d2= ImageDraw.Draw(temp_img)
        draw_scene_frontal(d2)
        # jogador6
        (x6,y6)= get_player6_frontal(160)  # pos final no inicio da frontal
        draw_player_frontal(d2, x6,y6, "blue")
        # goleiro
        (gx,gy)= get_gk_frontal(160)
        draw_player_frontal(d2, gx,gy, "red")
        # bola
        (bx,by)= get_ball_frontal(160)
        draw_ball_frontal(d2, bx,by, 7)

        # alpha=0 => black, alpha=1 => camera frontal
        local_f= idx-150
        alpha= local_f/10.0
        final_img= blend_with_frontal(temp_img, alpha)
        return final_img

    else:
        # idx>=160 => frontal "normal"
        # jogador6, goleiro, bola
        draw_scene_frontal(d)
        (x6,y6)= get_player6_frontal(idx)
        draw_player_frontal(d, x6,y6, "blue")
        (gx,gy)= get_gk_frontal(idx)
        draw_player_frontal(d, gx,gy, "red")
        (bx,by)= get_ball_frontal(idx)
        draw_ball_frontal(d, bx,by, 7)

        return img

def main():
    frames=[]
    for i in range(TOTAL_FRAMES):
        fr= make_frame(i)
        frames.append(fr)

    frames[0].save(
        "futebol_transicao_camera.webp",
        save_all=True,
        append_images=frames[1:],
        format="WEBP",
        duration=FRAME_DURATION_MS,
        loop=0,
        method=6,
        quality=80
    )
    print("Gerado futebol_transicao_camera.webp (~60s) com fade out/in na mudança de câmera")

if __name__=="__main__":
    main()
