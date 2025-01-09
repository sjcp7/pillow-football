from PIL import Image, ImageDraw, ImageFont
from field import *

def draw_player(d: ImageDraw, color: str, x: int, y: int, scale: float = 0.7):
    head_radius = int(10 * scale)
    torso_height = int(40 * scale)
    # split the player frame in 5 (roughly) equal parts
    leg_spacing = (head_radius * 2) // 5
    leg_height = int(25 * scale)

    # for legacy reasons, we were getting the position of the upper left corner of the player
    # adjusting (x, y) to point to where the player's feet should be
    x -= head_radius // 2
    y -= head_radius * 2 + torso_height + leg_height

    # head
    d.circle((x + head_radius, y + head_radius), head_radius, "blue")
    y += 2 * head_radius

    # torso
    d.rectangle([(x, y), (x + 2 * head_radius, y + torso_height)], color)
    y += torso_height

    
    # left leg
    d.line([(x + leg_spacing, y), (x + leg_spacing, y + leg_height)], color, leg_spacing)

    #right leg
    d.line([(x + leg_spacing * 4, y), (x + leg_spacing * 4, y + leg_height)], color, leg_spacing)

