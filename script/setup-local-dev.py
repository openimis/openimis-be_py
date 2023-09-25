from config import GITHUB_TOKEN, USER_NAME
from utils import parse_pip, walk_config_be
import os
import json
import git # pip install GitPython
from github import Github # pip install pyGithub

def main():
    g=Github(GITHUB_TOKEN)
    #assembly_fe='openimis/openimis-fe_js'
    assembly_be='openimis/openimis-be_py'
    #refresh openimis.json from git
    
    be_config = []
    repo = g.get_repo(assembly_be)
    be = json.loads(repo.get_contents("openimis.json", ref ='develop' ).decoded_content)
    be['modules'] = walk_config_be(g,be,clone_repo)
    # Writing to sample.json
    with open("../openimis.json", "w") as outfile:
        outfile.write(json.dumps(be, indent = 4, default=set_default) )
    
def clone_repo(repo,  module_name):
    path = os.path.join('../src/',module_name)
    remote = f"https://{USER_NAME}:{GITHUB_TOKEN}@{repo.git_url[6:]}"
    if os.path.exists(path):
        print(f"pulling {module_name}")
        git.Repo(path).remotes.origin.pull()
    else:
        print(f"cloning {module_name}")
        git.Repo.clone_from(remote, path)
    return {"name":f"{module_name}", "pip":f"{path} -e"} 

def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

if __name__ == '__main__':
    main()