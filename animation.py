from typing import Tuple, List
from PIL import Image, ImageDraw, ImageFont
from field import *
from ball import *
from player import *

ball = [(760, 780),(664, 692), (955, 585), (525, 579), (278, 648), (434, 760)]
pos = [
        # team 1
        [(760, 820, "black"), (780, 810, "black"), (874, 760, "black"), (880, 760, "black"), (798, 760, "black"), (798, 760, "black")], # p1, throw-in player, right winger
        [(646, 648, "black"), (664, 702, "black"), (722, 700, "black"), (800, 665, "black"), (836, 665, "black"), (690, 665, "black")], # p2, receiver of the throw-in, striker
        [(950, 560, "black"), (950, 590, "black"), (950, 590, "black"), (798, 590, "black"), (787, 590, "black"), (799, 590, "black")], # p3, left winger
        [(532, 575, "black"), (537, 579, "black"), (540, 579, "black"), (535, 579, "black"), (530, 577, "black"), (500, 598, "black")], # p4, left defender
        [(560, 770, "black"), (540, 770, "black"), (543, 768, "black"), (460, 768, "black"), (442, 768, "black"), (428, 760, "black")], # p5, right defender
        [(266, 648, "yellow"), (270, 648, "yellow"), (275, 648, "yellow"), (282, 648, "yellow"), (286, 648, "yellow"), (286, 648, "yellow")], # p6, keeper

        # team 2
        [(836, 770, "white"), (772, 760, "white"), (730, 757, "white"), (600, 757, "white"), (572, 757, "white"), (558, 757, "white")], # p1, left winger
        [(700, 630, "white"), (664, 638, "white"), (669, 638, "white"), (615, 625, "white"), (494, 640, "white"), (484, 655, "white")], # p2, striker
        [(1026, 540, "white"), (1026, 555, "white"), (990, 565, "white"), (830, 565, "white"), (800, 585, "white"), (785, 596, "white")], # p3, right winger
        [(1212, 660, "white"), (1216, 663, "white"), (1140, 657, "white"), (1064, 635, "white"), (1031, 620, "white"), (1022, 620, "white")], # p4, right defender
        [(947, 705, "white"), (950, 702, "white"), (960, 697, "white"), (1026, 740, "white"), (1030, 740, "white"), (1027, 740, "white")], # p5, left defender
        [(1560, 632, "red"), (1555, 632, "red"), (1560, 639, "red"), (1560, 639, "red"), (1552, 640, "red"), (1552, 640, "red")], # p6, keeper
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
    num_frames = 25
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



