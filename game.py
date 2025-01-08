from PIL import Image, ImageDraw, ImageFont
from field import *

#14 inch resolution
imageHeight = 1080
imageWidth = 1920

img = Image.new("RGBA", (imageWidth, imageHeight), "white")
d = ImageDraw.Draw(img)
# Draw guide lines
numVetLines = 20
for i in range(0,imageHeight, imageHeight // numVetLines):
    d.text((15,i), str(i), "black");
    d.line((0, i + 4) + (10, i + 4), "black");

numHorLines = 50
for i in range(0,imageWidth, imageWidth // numHorLines):
    d.text((i,imageHeight - 30), str(i), "black");
    d.line((i+5, imageHeight) + (i+5, imageHeight - 15), "black");

draw_field(d)
img.show()
