from PIL import Image, ImageDraw, ImageFont

def draw_ball(d: ImageDraw, x: int, y:int):
    d.circle((x,y), 8, fill="white", outline="black", width=3)
