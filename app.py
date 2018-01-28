# pylint: disable=invalid-name
# pylint: disable=missing-docstring
import os
from flask import Flask, render_template
app = Flask(__name__)
app.debug = True

def getFiles():
    path = "images"
    files = []
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            files.append(file)
    return files

@app.route("/")
def index():
    images = getFiles()
    return render_template('home.html', images=images)

if __name__ == '__main__':
    app.run()
