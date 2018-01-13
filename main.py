from pyfr_wrapper import msh2pyfrm
from pyfr_wrapper import pyfr_run
from pyfr_wrapper import pyfr_export
from flask import Flask, render_template, request
from model import Average
from werkzeug import secure_filename
import os

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

@app.route('/upload_msh', methods=['POST'])
def upload_msh():
    # Save uploaded file on server if it exists and is valid
    form = Average(request.form)
    pyfrm = None
    if request.files:
        file = request.files[form.filename.name]
        if file and allowed_file(file.filename):
            # Make a valid version of filename for any file system
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                   filename))

            pyfrm = msh2pyfrm(filename)

    return render_template("view.html", form=form, pyfrm=pyfrm)

@app.route('/run', methods=['POST'])
def run():
    form = Average(request.form)
    filename = request.form.get("filename")
    if os.path.isfile(os.path.join('mesh', filename +".pyfrm")):
        pyfr_run(filename)
        pyfr_export(filename)

    return render_template("view.html", form=form)


if __name__ == '__main__':
    app.run(debug=True)