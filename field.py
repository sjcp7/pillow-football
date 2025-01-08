from PIL import ImageDraw

# proportions from the real world are maintained through the drawings
# they are based on the bigger rectangle that makes the field

def draw_bigger_rectangle(d: ImageDraw):
    offset_x = 200
    height = 200
    d.polygon(((152, 810), (152 + 2 * offset_x, 810 - height), (1920 - 152 - 2 * offset_x, 810 - height), (1920 - 152, 810)), fill="green", outline="white", width=3)
    d.line(((1920/2,810),(1920/2, 810 - height)), width=3, fill="white");

def draw_field(d: ImageDraw):
    draw_bigger_rectangle(d)
    
