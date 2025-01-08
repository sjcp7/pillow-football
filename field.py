from PIL import ImageDraw

# proportions from the real world are maintained through the drawings
# they are based on the bigger rectangle that makes the field

height = 300
offset_x = 200

def draw_goals(d: ImageDraw):
    m = -height/offset_x # slope of the left line of the field
    b = 810 - (m * 152);
    x1 = 152
    x2 = 352
    d.polygon(((x1, x1*m + b), (x2, x2*m + b),(x2, (x2*m + b) - 100), (x1, (x1*m + b) - 100)), width=3)
def draw_center(d: ImageDraw):
    cx = 1920 / 2
    cy = 790 - (height / 2) # circle's center y coordinate
    d.ellipse((cx - 150, cy - 50) + (cx + 150, cy + 50), width=3)

def draw_bigger_rectangle(d: ImageDraw):
    d.polygon(((152, 810), (152 + 2 * offset_x, 810 - height), (1920 - 152 - 2 * offset_x, 810 - height), (1920 - 152, 810)), fill="green", outline="white", width=3)
    d.line(((1920/2,810),(1920/2, 810 - height)), width=3, fill="white");

def draw_field(d: ImageDraw):
    draw_bigger_rectangle(d)
    draw_center(d)
    draw_goals(d)
    
