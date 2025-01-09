from typing import Tuple, List
from PIL import Image, ImageDraw, ImageFont
from field import *
from ball import *
from player import *

ball = [(760, 760),(664, 702)]
pos = [
        [(760, 760), (760, 760)],
        [(646, 648), (664, 702)],
]

dimensions = (1920, 1080)

def create_image(dimensions: Tuple[int, int]):
    img = Image.new("RGBA", dimensions, "grey")
    return img

def draw_positions(d: ImageDraw, ball_pos: Tuple[int, int], players_pos: List[Tuple[int, int]]):
    draw_field(d)
    draw_ball(d, ball_pos[0], ball_pos[1])
    for i in range(len(players_pos)):
        draw_player(d, "black", players_pos[i][0], players_pos[i][1])
    
def animate():
    num_frames = 10
    frame_cnt = 0
    for i in range(len(pos[0])-1):
        for j in range(num_frames):
            ppos = [];
            for k in range (len(pos)):
                bpos = (ball[i][0] + j * (ball[i+1][0] - ball[i][0])/num_frames, ball[i][1] + j*(ball[i+1][1] - ball[i][1])/num_frames)
                step_x = j * (pos[k][i + 1][0] - pos[k][i][0]) / num_frames
                step_y = j * (pos[k][i + 1][1] - pos[k][i][1]) / num_frames
                ppos.append((pos[k][i][0] + step_x, pos[k][i][1] + step_y))

            img = create_image(dimensions)
            d = ImageDraw.Draw(img)
            draw_positions(d, bpos, ppos)
            img.save(f"frames/{frame_cnt}.png")
            frame_cnt += 1



