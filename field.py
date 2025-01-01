from PIL import ImageDraw

# proportions from the real world are maintained through the drawings
# they are based on the bigger rectangle that makes the field
def draw_field(d: ImageDraw, field_width: int, origin: tuple[int,int]):
    field_heigth = field_width * (60/100.0)
    # the bigger rectangle
    d.rectangle(origin + (field_width + origin[0], field_heigth + origin[1]), "green", "white", 2)
    d.line((origin[0] + field_width / 2, origin[1]) + (origin[0] + field_width / 2, origin[1] + field_heigth), width=3)
    # center circle
    draw_center(d, (origin[0] + field_width / 2, origin[1] + field_heigth / 2), 9.15 * field_width / 120)
    # both penalty areas
    draw_penalty(d, (origin[0], origin[1]), field_width, field_heigth)
    # both goals
    draw_goal(d, (origin[0], origin[1]), field_width, field_heigth)
    # both goal areas
    draw_goal_area(d, (origin[0], origin[1]), field_width, field_heigth)

def draw_center(d: ImageDraw, center: tuple[int,int] | list[int], radius: int):
    d.ellipse((center[0] - radius, center[1] - radius) + (center[0] + radius, center[1] + radius), outline="white", width=3)

def draw_goal(d: ImageDraw, xy: tuple[int, int] | list[int], field_width: int, field_heigth: int):
    goal_width = 35
    goal_heigth = 10 * field_width / 120
    # left
    d.rectangle((xy[0] - goal_width, xy[1] + (field_heigth-goal_heigth)/2) + (xy[0], xy[1] + (field_heigth + goal_heigth) / 2), width=2)
    #right
    d.rectangle((xy[0] + field_width, xy[1] + (field_heigth-goal_heigth)/2) + (xy[0] + field_width + goal_width, xy[1] + (field_heigth + goal_heigth) / 2), width=2)

def draw_penalty(d: ImageDraw, xy: tuple[int, int] | list[int], field_width: int, field_heigth: int):
    penalty_height = 40.3 * field_width / 120
    penalty_width = 16.5 * field_width / 120

    # left
    d.rectangle((xy[0], xy[1] + (field_heigth - penalty_height) / 2) + (xy[0] + penalty_width, xy[1] + (field_heigth + penalty_height) / 2), outline="white", width=3)

    #rigth
    d.rectangle((xy[0] - penalty_width + field_width, xy[1] + (field_heigth - penalty_height)/2) + (xy[0] + field_width, xy[1] + (field_heigth + penalty_height) / 2), outline="white", width=3)

def draw_goal_area(d: ImageDraw, xy: tuple[int, int] | list[int], field_width: int, field_heigth: int):
    penalty_height = 18.32 * field_width / 120
    penalty_width = 5.5 * field_width / 120

    # left
    d.rectangle((xy[0], xy[1] + (field_heigth - penalty_height) / 2) + (xy[0] + penalty_width, xy[1] + (field_heigth + penalty_height) / 2), outline="white", width=3)

    #rigth
    d.rectangle((xy[0] - penalty_width + field_width, xy[1] + (field_heigth - penalty_height)/2) + (xy[0] + field_width, xy[1] + (field_heigth + penalty_height) / 2), outline="white", width=3)

