from PIL import Image, ImageDraw
from config import Config, Source


def scale_coord(ref: int, v: int) -> int:
    return int(round((v / 1000) * ref))


class ImageFilter:
    def apply_to_image(self, config: Config, image: Image):
        raise NotImplementedError()


class RotateImageFilter(ImageFilter):
    def __init__(self, params: str):
        try:
            self.degrees = float(params)
        except Exception:
            raise Exception("invalid rotate params " + params)
    
    def apply_to_image(self, config: Config, image: Image):
        return image.rotate(self.degrees)


class CropImageFilter(ImageFilter):
    def __init__(self, params: str):
        cl = list(map(lambda x: int(x), params.split(",")))
        self.p1x = cl[0]
        self.p1y = cl[1]
        self.p2x = cl[2]
        self.p2y = cl[3]
    
    def apply_to_image(self, config: Config, image: Image):
        w = image.width
        h = image.height
        sp1x = scale_coord(w, self.p1x)
        sp1y = scale_coord(h, self.p1y)
        sp2x = scale_coord(w, self.p2x)
        sp2y = scale_coord(h, self.p2y)
        box = (sp1x, sp1y, sp2x, sp2y)
        return image.crop(box)


class DownscaleImageFilter(ImageFilter):
    def __init__(self, params: str):
        try:
            self.max_size = int(params)
        except Exception:
            raise Exception("invalid resize params " + params)
            
    def apply_to_image(self, config: Config, image: Image):
        w = image.width
        h = image.height
        if self.max_size > w and self.max_size > h:
            return image
        else:
            if w > self.max_size:
                sc = self.max_size / w
            else:
                sc = self.max_size / h
            return image.resize((int(round(w * sc)), int(round(h * sc))), Image.LANCZOS)


class UpscaleImageFilter(ImageFilter):
    def __init__(self, params: str):
        try:
            self.min_size = int(params)
        except Exception:
            raise Exception("invalid resize params " + params)
            
    def apply_to_image(self, config: Config, image: Image):
        w = image.width
        h = image.height
        if self.min_size < w and self.min_size < h:
            return image
        else:
            if w < self.min_size:
                sc = self.min_size / w
            else:
                sc = self.min_size / h
            return image.resize((int(round(w * sc)), int(round(h * sc))), Image.LANCZOS)


class MaskImageFilter(ImageFilter):
    def __init__(self, params: str):
        plist = list(map(lambda x: int(x), params.split(",")))
        if len(plist) % 2 != 0:
            raise Exception("invalid mask params. number of params must be even (x,y per point)")
        elif len(plist) < 4:
            raise Exception("invalid mask params. at least 2 points must be defined")
        self.points = list(zip(plist[::2], plist[1::2]))
        # convert 2 points to rectangle (clockwise polygon)
        if len(self.points) == 2:
            self.points = [self.points[0], (self.points[1][0], self.points[0][1]),
                           self.points[1], (self.points[0][0], self.points[1][1])]
    
    def apply_to_image(self, config: Config, image: Image):
        w = image.width
        h = image.height
        scaled_points = list(map(lambda x: (scale_coord(w, x[0]), scale_coord(h, x[1])), self.points))
        d = ImageDraw.Draw(image)
        d.polygon(scaled_points, fill=config.mask_color)
        return image


class GreyscaleImageFilter(ImageFilter):
    def apply_to_image(self, config: Config, image: Image):
        return image.convert('L')


def parse_image_filter(s: str) -> ImageFilter:
    try:
        i = s.find(':')
        if i > 0:
            slug = s[0:i]
            params = s[i + 1:]
        else:
            slug = s
            params = ""
        if slug == 'rotate':
            return RotateImageFilter(params)
        elif slug == 'crop':
            return CropImageFilter(params)
        elif slug == 'downscale':
            return DownscaleImageFilter(params)
        elif slug == 'upscale':
            return UpscaleImageFilter(params)
        elif slug == 'mask':
            return MaskImageFilter(params)
        elif slug == 'greyscale':
            return GreyscaleImageFilter()
        else:
            raise Exception("Invalid image filter " + s)
    except Exception:
        raise Exception("Invalid image filter " + s)


def apply_filters(source: Source, config: Config, image: Image):
    im = image
    for tr in source.filters:
        im = tr.apply_to_image(config, im)
    return im
