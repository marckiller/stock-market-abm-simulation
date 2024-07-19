import os
import subprocess
import sys

def create_virtual_environment(env_name='venv'):
    if not os.path.exists(env_name):
        subprocess.call([sys.executable, '-m', 'venv', env_name])
        print(f"Virtual environment '{env_name}' created.")
    else:
        print(f"Virtual environment '{env_name}' already exists.")


def activate_virtual_environment(env_name='venv'):
    activate_venv_command = f"source {env_name}/bin/activate"
    print(f"To activate venv run command: {activate_venv_command}")
    return activate_venv_command


def install_requirements(env_name='venv'):
    requirements_file = 'requirements.txt'
    if os.path.exists(requirements_file):
        subprocess.call([os.path.join(env_name, 'bin', 'pip'), 'install', '-r', requirements_file])
        print(f"Installed requirements from {requirements_file}.")
    else:
        print(f"No {requirements_file} file found.")

if __name__ == '__main__':
    venv_name = 'venv'
    create_virtual_environment(venv_name)
    activate_command = activate_virtual_environment(venv_name)
    install_requirements(venv_name)
    print("\nSetup completed.")
    print(f"To activate virtual environment run command: \n{activate_command}")

