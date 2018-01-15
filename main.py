import pygmsh

from pyfr_wrapper import msh2pyfrm
from pyfr_wrapper import pyfr_run
from pyfr_wrapper import pyfr_export
import configparser
from flask import Flask, render_template, redirect, request, send_file, url_for
from model import Average
from werkzeug import secure_filename
import os
import meshio
import numpy as np
import fileinput
import sys

# Application object
app = Flask(__name__)

# Relative path of directory for uploaded files
UPLOAD_DIR = 'mesh/'

app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
app.secret_key = 'MySecretKey'

if not os.path.isdir(UPLOAD_DIR):
    os.mkdir(UPLOAD_DIR)

# Allowed file types for file upload
ALLOWED_EXTENSIONS = set(['msh'])

def allowed_file(filename):
    """Does filename have the right extension?"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    form = Average(request.form)
    return render_template("view.html", form=form, pyfrm=None)

@app.route('/pygmsh', methods=['POST'])
def pyGmsh():
    PyGmsh = request.form.get("PyGmsh")
    geom = pygmsh.built_in.Geometry()
    exec(PyGmsh)

    points, cells, point_data, cell_data, field_data = pygmsh.generate_mesh(geom)
    #points, cells, _, _, _ = pygmsh.generate_mesh(geom)
    meshio.write('mesh.vtu', points, cells, cell_data=cell_data)
    return send_file("mesh.vtu")

@app.route('/upload_msh', methods=['POST'])
def upload_msh():
    # Save uploaded file on server if it exists and is valid
    form = Average(request.form)
    pyfrm = None
    if request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            # Make a valid version of filename for any file system
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                   filename))

            pyfrm = msh2pyfrm(filename)

    return redirect(url_for('index') + '#calc')

@app.route('/config', methods=['POST'])
def upload_config():

    keys = ["gamma", "mu", "Pr", "cp", "Uw", "H", "Pc", "Tw", "rho", "u", "v", "w", "p" ]
    for line in fileinput.input("config/config.ini", inplace=1):
        if line.startswith("["):
            if "constants" in line or "soln-ics" in line:
                check = True
            else:
                check = False
        if check is True:
            for i,key in enumerate(keys):
                if line.startswith(key + " = "):
                    line = key + " = " + request.form.get(key) + "\n"
        sys.stdout.write(line)


    return render_template("view.html", pyfrm=True)

@app.route('/run', methods=['POST'])
def run():
    filename = request.form.get("filename")
    if os.path.isfile(os.path.join('mesh', filename +".pyfrm")):
        pyfr_run(filename)
        pyfr_export(filename)

    return send_file(filename + "-040.vtu")


if __name__ == '__main__':
    app.run(debug=True)
