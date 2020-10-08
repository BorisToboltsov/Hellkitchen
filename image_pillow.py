from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import settings


def image(txt, color):
    """Создание картинки с текстом"""
    if color == 'red':
        img = Image.open(settings.RED)
    elif color == 'green':
        img = Image.open(settings.GREEN)
    else:
        return
    draw = ImageDraw.Draw(img)
    font_size = 50
    txt_n = txt
    if color == 'green':
        txt_n = txt.replace(' ', '\n')
    font = ImageFont.truetype(settings.SET_FONT, size=font_size)
    draw.text((20, 20), txt_n, (0, 0, 0), font=font)
    img_path = settings.IMG_PATH + txt + '.jpg'
    img.save(img_path)
    return img_path
