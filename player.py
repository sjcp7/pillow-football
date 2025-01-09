from PIL import Image, ImageDraw, ImageFont
from field import *


def draw_player(d: ImageDraw, color: 'string', x: 'int', y: 'int', scale: 'float'):
    # head
    head_radius = int(10 * scale)
    d.circle((x + head_radius, y + head_radius), head_radius, "blue")
    y += 2 * head_radius

    # torso
    torso_height = int(40 * scale)
    d.rectangle([(x, y), (x + 2 * head_radius, y + torso_height)], color)
    y += torso_height

    # split the player frame in 5 (roughly) equal parts
    leg_spacing = (head_radius * 2) // 5
    leg_height = int(25 * scale)
    
    # left leg
    d.line([(x + leg_spacing, y), (x + leg_spacing, y + leg_height)], color, leg_spacing)

    #right leg
    d.line([(x + leg_spacing * 4, y), (x + leg_spacing * 4, y + leg_height)], color, leg_spacing)

