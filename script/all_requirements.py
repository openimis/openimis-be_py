import os
import subprocess


def install_modules():
    print("installing dependencies and modules")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    commands = [f'pip install -r {script_dir}/../requirements.txt',
                f'python {script_dir}/modules-requirements.py {script_dir}/../openimis-dev.json > {script_dir}/modules-requirements.txt',
                f'pip install -r {script_dir}/modules-requirements.txt']

    try:
        for command in commands:
            print(f"Running: {command}")
            result = subprocess.check_output(command, shell = True, executable = "/bin/bash", stderr = subprocess.STDOUT)
            

    except subprocess.CalledProcessError as cpe:
        result = cpe.output
    except Exception as e:
        print(e)
    return result

if __name__ == "__main__":
    install_modules()