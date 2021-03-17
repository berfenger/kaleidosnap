import yaml
from PIL import Image


class Source:
    def __init__(self, _id, url, filters):
        self.id = _id
        self.url = url
        self.filters = filters
        
    def apply_filters(self, config, image: Image):
        im = image
        for tr in self.filters:
            im = tr.apply_to_image(config, im)
        return im


class Config:
    def __init__(self, sources: list[Source], mask_color: str):
        self.sources = sources
        self.mask_color = mask_color


def load_config(file) -> Config:
    with open(file, 'r') as stream:
        p = yaml.safe_load(stream)
        srcs = list(map(create_source, p['sources']))
        return Config(srcs, p['mask_color'] or '#000000')


def create_source(src: dict) -> Source:
    from image_filters import parse_image_filter
    return Source(src['id'], src['url'], list(map(parse_image_filter, src['filters'])))
