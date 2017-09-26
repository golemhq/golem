import shutil
import subprocess
from subprocess import call
import os


current_dir = os.getcwd()

def kickstart_golem_gui():
    os.chdir(current_dir)
    call(["golem-admin", "createdirectory", "test"])
    os.chdir(os.path.join(current_dir, 'test'))
    call(['python', 'golem.py', 'createproject', 'test'])
    # call(['python', 'golem.py', 'gui', '-p', '8000'])
    p = subprocess.Popen("python golem.py gui -p 8000", shell=True)
    return p


def stop_golem_gui(p):
    p.kill()
    os.chdir(current_dir)
    shutil.rmtree(os.path.join(current_dir, 'test'))