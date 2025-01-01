from PIL import Image, ImageDraw
from field import *

#14 inch resolution
imageHeight = 1080
imageWidth = 1920

img = Image.new("RGBA", (imageWidth, imageHeight), "grey")
d = ImageDraw.Draw(img)
draw_field(d, 1080, (60,60)) 
img.show()
