from PIL import Image, ImageFont, ImageDraw
import colorsys
import datetime


def scale_coord(ref: int, v: int) -> int:
    return int(round((v / 1000) * ref))


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) / 255 for i in range(0, lv, lv // 3))


def shadow_for_color(color: str):
    (r, g, b) = hex_to_rgb(color)
    (h, s, v) = colorsys.rgb_to_hsv(r, g, b)
    (nr, ng, nb) = colorsys.hsv_to_rgb(h, 0, 1 - v)
    return '#' + ''.join('%02x' % i for i in list(map(lambda x: int(round(x * 255)), [nr, ng, nb])))


def parse_align(align: str) -> (str, str):
    if len(align) == 2:
        return align[0], align[1]
    else:
        aps = align.split(',', 1)
        if len(aps) == 2:
            return aps[0], aps[1]
        else:
            raise Exception("invalid text alignment " + align)


def draw_text(image: Image, align: str, text: str, size_sp: int, color: str, margin_h: int = 25) -> Image:
    w = image.width
    h = image.height
    px = size_sp * (w / 1000)
    shadow_col = shadow_for_color(color)
    fnt = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf", int(px))
    d = ImageDraw.Draw(image)
    sw = max(int(round(px * 0.05)), 2)
    tsw, tsh = d.textsize(text, fnt, stroke_width=sw)
    if align:
        av, ah = parse_align(align)
        margin = scale_coord(h, margin_h)
        # calc Y coord
        if av == "t":
            sy = margin
        elif av == "c":
            sy = h / 2 - tsh / 2
        elif av == "b":
            sy = h - margin - tsh
        else:
            try:
                sy = scale_coord(h, int(av))
            except Exception:
                raise Exception("invalid text alignment " + align)
        # calc X coord
        if ah == "l":
            sx = margin
        elif ah == "c":
            sx = w / 2 - tsw / 2
        elif ah == "r":
            sx = w - margin - tsw
        else:
            try:
                sx = scale_coord(w, int(ah))
            except Exception:
                raise Exception("invalid text alignment " + align)
    else:
        raise Exception("invalid arguments")
    d.text((sx, sy), text, font=fnt, fill=color, stroke_width=sw, stroke_fill=shadow_col)
    # d.polygon([(sx, sy), (sx + tsw, sy), (sx + tsw, sy + tsh), (sx, sy + tsh)], outline='#FF4545')
    return image


def draw_date(image: Image, align: str, date_format: str, size_sp: int, color: str,
               margin_h: int = 25) -> Image:
    now = datetime.datetime.now()
    date_time = now.strftime(date_format)
    return draw_text(image, align, date_time, size_sp, color, margin_h=margin_h)