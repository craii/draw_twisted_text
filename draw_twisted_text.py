# - * - coding:utf-8 - * -
#  作者：Elias Cheung
#  编写时间：2022/7/12  14:43
from PIL import Image, ImageFont, ImageDraw
from typing import Union, List, NewType
from datetime import datetime
from math import ceil, floor

Picture = NewType("Picture", Image)


def draw_text(text: str, font_family: str, font_size: int = 50,
              text_color: Union[str, tuple] = (0, 0, 0), location: tuple = None,
              bg_color: Union[str, tuple] = "white") -> List[Picture]:
    """
    :param location: location on image where the text would be written onto, if None, it will be reset to(0,2*font_size)
    :param font_family: src of ttf file (win or mac), or name of built-in fonts(ios);
    :param text: text that you want to draw;
    :param text_color: text color, in pattern (r, g, b) or string white, green, ..., e.t.c.;
    :param font_size: font size;
    :param bg_color: canvas color, in pattern (r, g, b) or string white, green, ..., e.t.c.;
    :return: 2 picture in a list; twisted one (1st) and just-crop one (2nd);
    """
    print(f"【{datetime.now()}】创建画板")
    print(f"【{datetime.now()}】开始绘制正文")

    font = ImageFont.truetype(font_family, font_size)
    image = Image.new(mode="RGB", size=(len(text) * font_size, len(text) * font_size), color=bg_color)

    draw = ImageDraw.Draw(image)
    location = (0, 2 * font_size) if location is None else location
    draw.text(location, text, fill=text_color, font=font)

    crop_image = image.crop((0, int(1.8 * font_size), len(text) * font_size, int(3.2 * font_size)))
    twisted_image = crop_image.resize(size=(ceil(len(text)) * font_size, 50 * font_size))

    print(f"【{datetime.now()}】正文绘制完毕")
    return [twisted_image, crop_image]


def refine_drew_text_image(image: Picture, font_size: int = 50,
                           text_color: Union[str, tuple] = (0, 0, 0),
                           bg_color: Union[str, tuple] = (255, 255, 255)) -> Picture:
    """
    :param text_color: text color, in pattern (r, g, b) or string white, green, ..., e.t.c.;
                       MUST BE THE SAME COLOR AS THE ONE YOU USED TO DRAW TEXT WITH FUNCTION draw_text();
    :param bg_color: text color, in pattern (r, g, b) or string white, green, ..., e.t.c.;
                     MUST BE THE SAME COLOR AS THE ONE YOU USED WITH FUNCTION draw_text();
    :param image: image to be refined, come from function draw_text();
    :param font_size: MUST BE EQUAL TO THE FONT SIZE USED IN FUNCTION draw_text();
    :return: refined picture
    """

    print(f"【{datetime.now()}】开始优化图片")
    #  核心部分,
    for w in range(image.width):
        for h in range(image.height):
            r_, g_, b_ = image.getpixel((w, h))
            _r, _g, _b = text_color
            if (r_, g_, b_, 0) != (_r, _g, _b, 0):
                image.putpixel((w, h), bg_color)

    print(f"【{datetime.now()}】准备输出优化效果图")
    new_image = Image.new(mode="RGB", size=(45 * font_size, 100 * font_size), color=bg_color)
    new_image.paste(image, (18 * font_size, 0))

    print(f"【{datetime.now()}】计算输出效果图边界尺寸")
    coordinates_y, coordinates_x = list(), list()
    for w in range(new_image.width):
        for h in range(new_image.height):
            r_, g_, b_ = new_image.getpixel((w, h))
            if (r_, g_, b_) != (255, 255, 255):
                coordinates_y.append(h)
                coordinates_x.append(w)

    text_start_y = min(coordinates_y)
    text_end_y = max(coordinates_y)
    text_start_x = min(coordinates_x)
    text_end_x = max(coordinates_x)

    crop_box = (text_start_x - 2 * font_size,
                text_start_y - 2 * font_size,
                text_end_x + 2 * font_size,
                text_end_y + 2 * font_size)
    print(f"【{datetime.now()}】确定新边界", crop_box)

    new_image = new_image.crop(crop_box)
    return new_image


def concatenate_images(*images: Picture, strategy: str = "MAX",
                       bg_color: Union[str, tuple] = (255, 255, 255)) -> Picture:
    """
    :param bg_color: background color used as concatenated images; better be THE SAME as used in draw_text() and
                    refine_drew_text_image()
    :param images: one or more image(s) to be concatenated
    :param strategy: MAX or MIN, if MAX, concatenated picture's WIDTH will be set to the LARGEST width of image in image
                    tuple, vice versa;
    :return: concatenated picture
    """
    images: tuple = images
    images_width = [image.width for image in images]
    images_height = [image.height for image in images]

    max_width, min_width = max(images_width), min(images_width)

    new_image_height = sum(images_height) + 50
    new_image_width = max_width if strategy == "MAX" else min_width

    images = tuple(map(lambda img: img.resize(size=(new_image_width, floor(new_image_width * img.height / img.width))),
                       images))

    new_image = Image.new(mode="RGB", size=(new_image_width, new_image_height), color=bg_color)

    current_y = 0
    for image in images:
        new_image.paste(image, (0, current_y))
        current_y += image.height

    return new_image


if __name__ in "__main__":
    lyris = "生成从充电口才能看清的图片"
    string = "闭上一只眼看从充电口哦"
    font_src = "w6.ttf"  # pc/mac 可用ttf文件的路径替代，ios可使用系统中已安装的字体，输入名称即可

    pic = draw_text(text=lyris, font_family=font_src)
    pic[0].show()
    print("上图为中间临时产物，优化中，请耐心等待结果～")

    mod_pic = refine_drew_text_image(pic[0])
    mod_pic.show()

    hint = draw_text(text=string, font_family=font_src)

    last = concatenate_images(pic[0], hint[1], strategy="MAX")
    last.show()
    last.save(f"{lyris}_{datetime.now()}.png")
