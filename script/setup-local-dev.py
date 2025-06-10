from config import GITHUB_TOKEN, USER_NAME, BRANCH
from utils import parse_pip, walk_config_be
import os
import json
import git  # pip install GitPython
from github import Github  # pip install pyGithub
import sys
from all_requirements import install_modules
ref_assembly = BRANCH#"develop"
MODE = None
if len(sys.argv) > 1:
    MODE = sys.argv[1]

def main():
    if GITHUB_TOKEN:
        g = Github(GITHUB_TOKEN)
    else: # Anonymous
        g = Github()
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



def get_remote(repo, mode = None):
    if mode == 'ssh':
        remote = f"git@github.com:openimis/openimis-be_py.git"
    elif GITHUB_TOKEN:
        remote = f"https://{USER_NAME}:{GITHUB_TOKEN}@{repo.git_url[6:]}"
    else:
        remote = f"https://{repo.git_url[6:]}"
    return remote

def clone_repo(repo, module_name, ref='develop'):
    src_path = os.path.abspath("../../")
    path = os.path.join(src_path, module_name)
    remote = get_remote(repo, MODE)

    if os.path.exists(path):
        repo_git = git.Repo(path)
        try:
            repo_git.remotes.origin.fetch(ref)
            repo_git.git.checkout(ref)
            repo_git.remotes.origin.pull()
            print(f"{module_name} pulled and checked out")
        except Exception as e:
            print(f"error while checking out {module_name} to {ref}:\n{e}")
    else:
        print(f"cloning {module_name}")
        repo_git = git.Repo.clone_from(remote, path)
        repo_git.remotes.origin.fetch(ref)
        repo_git.git.checkout(ref)
    return {"name": f"{module_name}", "pip": f"-e {path}"}


def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError


if __name__ == "__main__":
    main()
