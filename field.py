from PIL import ImageDraw

# proportions from the real world are maintained through the drawings
# they are based on the bigger rectangle that makes the field
print('PIL',PIL.__version__)
screen_width = 1920
field_height = 300
field_offset_x = 200 # the difference between the x value of the upper and lower lines of the field
field_lower_y = 810 # y coordinate of the lower line of the field
field_lower_x = 152 # y coordinate of the lower line of the field
left_m = -field_height/field_offset_x # slope of the left line of the field
right_m = - left_m # slope of the left line of the field

def draw_field(d: ImageDraw):
    draw_bigger_rectangle(d)
    draw_center(d)
    draw_penalty_circle(d, 390, field_lower_y - 22 - (field_height / 2), 120, 40)
    draw_penalty_circle(d, screen_width-390, field_lower_y - 22 - (field_height / 2), 120, 40)
    draw_goals(d)
    draw_penalty_boxes(d)
    draw_goal_boxes(d)
    d.ellipse((390, field_lower_y - 22 - (field_height / 2)), 10,fill="white")
def draw_penalty_boxes(d: ImageDraw):
    # left penalty box
    b = field_lower_y - (left_m * field_lower_x);
    x1 = 215
    x2 = x1 + 100
    box_width = 150
    d.polygon(((x1, x1*left_m + b), (x2, x2*left_m + b),(x2 + box_width, (x2*left_m + b)), (x1 + box_width, (x1*left_m + b))), width=3, outline="white",fill="green")

    # right penalty box
    b = field_lower_y - (right_m * (screen_width - field_lower_x))
    x1 = screen_width - x1
    x2 = x1 - 100
    d.polygon(((x1, x1*right_m + b), (x2, x2*right_m + b),(x2 - box_width, (x2*right_m + b)), (x1 - box_width, (x1*right_m + b))), width=3, outline="white",fill="green")

def draw_goal_boxes(d: ImageDraw):
    # left goal box
    b = field_lower_y - (left_m * field_lower_x);
    x1 = 237
    x2 = x1 + 55
    box_width = 70
    d.polygon(((x1, x1*left_m + b), (x2, x2*left_m + b),(x2 + box_width, (x2*left_m + b)), (x1 + box_width, (x1*left_m + b))), width=3, outline="white",fill="green")

    # right goal box
    b = field_lower_y - (right_m * (screen_width - field_lower_x))
    x1 = screen_width - x1
    x2 = x1 - 55
    d.polygon(((x1, x1*right_m + b), (x2, x2*right_m + b),(x2 - box_width, (x2*right_m + b)), (x1 - box_width, (x1*right_m + b))), width=3, outline="white",fill="green")

def draw_goals(d: ImageDraw):
    # left goal
    b = field_lower_y - (left_m * field_lower_x);
    x1 = 245
    x2 = x1 + 40
    goal_height = 70
    d.polygon(((x1, x1*left_m + b), (x2, x2*left_m + b),(x2, (x2*left_m + b) - goal_height), (x1, (x1*left_m + b) - goal_height)), width=3)
    tw = 30; # width of the triangle
    d.polygon(((x1, x1*left_m + b), (x1, (x1*left_m + b) - goal_height), (x1-tw, (x1-tw)*left_m + b + tw*left_m)), width=3);
    # right goal
    b = field_lower_y - (right_m * (screen_width-field_lower_x));
    x1 = screen_width - x1
    x2 = x1 - 40
    goal_height = 70
    d.polygon(((x1, x1*right_m + b), (x2, x2*right_m + b),(x2, (x2*right_m + b) - goal_height), (x1, (x1*right_m + b) - goal_height)), width=3)

    d.polygon(((x1, x1*right_m + b), (x1, (x1*right_m + b) - goal_height), (x1+tw, (x1+tw)*right_m + b - tw*right_m)), width=3);

def draw_penalty_circle(d: ImageDraw, cx: int, cy: int, width: int, height: int):
    d.ellipse((cx - width / 2, cy - height / 2) + (cx + width / 2, cy + height / 2), outline = "white", width=3)
    
def draw_center(d: ImageDraw):
    width = 300
    height = 100
    cx = screen_width / 2
    cy = 790 - (field_height / 2) # circle's center y coordinate
    d.ellipse((cx - width / 2, cy - height / 2) + (cx + width / 2, cy + height / 2), width=3)

def draw_bigger_rectangle(d: ImageDraw):
    d.polygon(((field_lower_x, field_lower_y), (field_lower_x + field_offset_x, field_lower_y -field_height), (screen_width - field_lower_x -  field_offset_x, field_lower_y -field_height), (screen_width - field_lower_x, field_lower_y)), fill="green", outline="white", width=3)
    d.line(((screen_width/2,field_lower_y),(screen_width/2, field_lower_y -field_height)), width=3, fill="white");
