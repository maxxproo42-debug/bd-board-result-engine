from PIL import Image

im = Image.open('bteb_captcha.png')
print('Size:', im.size, 'Mode:', im.mode)

# Let's print ASCII representation of the image
w, h = im.size
pixels = im.convert('L').load()
for y in range(0, h, 2):
    line = "".join("#" if pixels[x, y] < 128 else " " for x in range(w))
    print(line)
