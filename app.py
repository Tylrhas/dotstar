from flask import Flask, render_template, request
import os
# import asyncio
app = Flask(__name__)

HOST = '0.0.0.0'
PORT = 5000

duration   = int(request.get_json()['duration'])

def getFiles():
    path = "images"
    images = []
    for image in os.listdir(path):
        if os.path.isfile(os.path.join(path, image)):
            images.append(image)
    return images

@app.route("/")
def index():
    images = getFiles()
    return render_template('home.html', images=images)

    # Start the Flask App
if __name__ == '__main__':
	app.run(host=HOST, port=PORT, threaded=True)