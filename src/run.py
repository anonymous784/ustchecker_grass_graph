from flask import Flask, request
from main import grass_image_view

app = Flask(__name__)


@app.route('/')
def _entrypoint():
    # return hello_world(request)
    return grass_image_view(request)


if __name__ == '__main__':
    app.run(debug=True)
