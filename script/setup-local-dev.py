from config import GITHUB_TOKEN, USER_NAME, BRANCH
from utils import parse_pip, walk_config_be
import os
import json
import git  # pip install GitPython
from github import Github  # pip install pyGithub
import subprocess, sys

ref = BRANCH#"develop"
ref_assembly = BRANCH#"develop"


def main():
    g = Github(GITHUB_TOKEN)
    # assembly_fe='openimis/openimis-fe_js'
    assembly_be = "openimis/openimis-be_py"
    # refresh openimis.json from git

    be_config = []
    repo = g.get_repo(assembly_be)
    be = json.loads(
        repo.get_contents("openimis.json", ref=ref_assembly).decoded_content
    )
    be["modules"] = walk_config_be(g, be, clone_repo)
    # Writing to sample.json
    with open("../openimis-dev.json", "w") as outfile:
        outfile.write(json.dumps(be, indent=4, default=set_default))     
    install_modules()

def install_modules():
    print("installing dependencies and modules")
    root_path = os.path.abspath("../")
    command = f'pip install {root_path}/requirements.txt & python modules-requirements.py openimis-dev.json > modules-requirements.txt & pip install -r modules-requirements.txt'

    try:
        result = subprocess.check_output(command, shell = True, executable = "/bin/bash", stderr = subprocess.STDOUT)

    except subprocess.CalledProcessError as cpe:
        result = cpe.output
    return result


def clone_repo(repo, module_name):
    src_path = os.path.abspath("../src/")
    path = os.path.join(src_path, module_name)
    remote = f"https://{USER_NAME}:{GITHUB_TOKEN}@{repo.git_url[6:]}"
    if os.path.exists(path):

        repo_git = git.Repo(path)
        try:
            repo_git.git.checkout(ref)
            repo_git.remotes.origin.pull()
            print(f"{module_name} pulled and checked out")
        except:
            print(
                f"error while checking out {module_name} to {ref}, please ensure the local changes are commited"
            )
    else:
        print(f"cloning {module_name}")
        repo_git = git.Repo.clone_from(remote, path)
        repo_git.git.checkout(ref)
    return {"name": f"{module_name}", "pip": f"-e {path}"}


def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError


if __name__ == "__main__":
    main()
