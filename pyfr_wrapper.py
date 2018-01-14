import os
import glob
import subprocess
import shlex

# pyfr import couette_flow_2d.msh couette_flow_2d.pyfrm
def msh2pyfrm(filename=None):
    input_msh = os.path.join('mesh', filename)
    name = os.path.splitext(input_msh)[0]
    output_msh = name + '.pyfrm'
    os.system("pyfr import " + input_msh +" " + output_msh)
    res_name = os.path.splitext(filename)[0]
    return res_name

# pyfr run -b cuda -p couette_flow_2d.pyfrm config.ini
def pyfr_run(mesh_filename=None, config_path="config/config.ini"):
    pyfrm = os.path.join('mesh', mesh_filename) + '.pyfrm'
    run_command("pyfr run -b openmp -p " + pyfrm +" " + config_path)
    return

# pyfr export couette_flow_2d.pyfrm couette_flow_2d-040.pyfrs couette_flow_2d-040.vtu -d 4
def pyfr_export(mesh_filename=None, config_path="config/config.ini"):
    pyfrm = os.path.join('mesh', mesh_filename) + '.pyfrm'
    pyfrs = mesh_filename + '-040.pyfrs'
    vtu = mesh_filename + '-040.vtu'
    run_command("pyfr export " + pyfrm + " " + pyfrs + " " + vtu + " -d 4")
    for filename in glob.glob(mesh_filename+"*"):
        if filename.endswith(".pyfrs"):
            os.remove(filename)
    return

def run_command(command):
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
        break
    rc = process.poll()
    return rc