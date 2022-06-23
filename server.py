from PIL import Image
import requests
from io import BytesIO
import os
from typing import Optional
from flask import Flask, send_file, json, request
from waitress import serve
from config import load_config, Source
import image_filters

# load env config
try:
    config_file = os.environ['CONFIG_FILE']
except Exception:
    config_file = "./config.yml"

try:
    server_port = int(os.environ['PORT'])
except Exception:
    server_port = 8080

# load config
config = load_config(config_file)


def source_by_id(srcs: list[Source], sid: str) -> Optional[Source]:
    for s in srcs:
        if s.id == sid:
            return s
    return None


def url_to_image(url: str) -> Image:
    if url.startswith("file://"):
        return Image.open(url[7::])
    else:
        response = requests.get(url)
        return Image.open(BytesIO(response.content))


# http server
app = Flask(__name__)


@app.route('/')
def health():
    return "ok"


@app.route('/sources')
def source_list():
    data = list(map(lambda x: x.id, config.sources))
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


@app.route('/source/<sourceid>')
def source(sourceid):
    passthrough: bool = request.args.get('passthrough') or False
    src = source_by_id(config.sources, sourceid)
    if src:
        try:
            with url_to_image(src.url) as im:
                if not passthrough:
                    im = image_filters.apply_filters(src, config, im)
                output = BytesIO()
                im.save(output, format="JPEG")
                output.seek(0)
                return send_file(output, mimetype="image/jpeg")
        except:
            return "Could not get remote image", 500
    else:
        return "Invalid source ID", 404


if __name__ == '__main__':
    print("using config file %s" % config_file)
    print("listening on port %d" % server_port)
    serve(app, host='0.0.0.0', port=server_port)
