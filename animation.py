from typing import Tuple, List
from PIL import Image, ImageDraw, ImageFont
from field import *
from ball import *
from player import *

ball = [(760, 780),(664, 692)]
pos = [
        # team 1
        [(760, 820, "black"), (780, 810, "black")], # p1, throw-in player, right winger
        [(646, 648, "black"), (664, 702, "black")], # p2, receiver of the throw-in, striker
        [(950, 560, "black"), (950, 590, "black")], # p3, left winger
        [(532, 575, "black"), (537, 579, "black")], # p4, left defender
        [(560, 770, "black"), (540, 770, "black")], # p5, right defender
        [(266, 648, "yellow"), (270, 648, "yellow")], # p6, keeper

        # team 2
        [(836, 770, "white"), (772, 760, "white")], # p1, left winger
        [(700, 630, "white"), (664, 638, "white")], # p2, striker
        [(1026, 540, "white"), (1026, 555, "white")], # p3, right winger
        [(1212, 660, "white"), (1216, 663, "white")], # p4, right defender
        [(947, 705, "white"), (950, 702, "white")], # p5, left defender
        [(1560, 632, "red"), (1555, 632, "red")], # p6, keeper
]

dimensions = (1920, 1080)

def draw_guide_lines(d: ImageDraw):
    imageHeight = dimensions[1]
    imageWidth = dimensions[0]

    numVetLines = 20
    for i in range(0,imageHeight, imageHeight // numVetLines):
        d.text((15,i), str(i), "black");
        d.line((0, i + 4) + (10, i + 4), "black");
    
    numHorLines = 50
    for i in range(0,imageWidth, imageWidth // numHorLines):
        d.text((i,imageHeight - 30), str(i), "black");
        d.line((i+5, imageHeight) + (i+5, imageHeight - 15), "black");


def create_image(dimensions: Tuple[int, int]):
    img = Image.new("RGBA", dimensions, "grey")
    d = ImageDraw.Draw(img)
    draw_guide_lines(d)
    return img

def draw_positions(d: ImageDraw, ball_pos: Tuple[int, int], players_pos: List[Tuple[int, int, str]]):
    draw_field(d)
    draw_ball(d, ball_pos[0], ball_pos[1])
    for i in range(len(players_pos)):
        draw_player(d, players_pos[i][2], players_pos[i][0], players_pos[i][1])
    
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
                ppos.append((pos[k][i][0] + step_x, pos[k][i][1] + step_y, pos[k][i][2]))

            img = create_image(dimensions)
            d = ImageDraw.Draw(img)
            draw_positions(d, bpos, ppos)
            img.save(f"frames/img-{frame_cnt:03}.png")
            frame_cnt += 1



