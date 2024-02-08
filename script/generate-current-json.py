import os
from git import Repo
from config import GITHUB_TOKEN, USER_NAME, BRANCH

def get_git_info(directory):
    try:
        repo = Repo(directory)
        remote_url = repo.remote().url
        branch = repo.active_branch.name
        return remote_url, branch
    except Exception as e:
        return None, None

def scan_directory(directory):
    for root, dirs, files in os.walk(directory):
        for dir_name in dirs:
            name=root.split('/')[-1]
            dir_path = os.path.join(root, dir_name)
            remote_url, branch = get_git_info(dir_path)
            
            if remote_url is not None and branch is not None:
                remote_url = remote_url.replace(USER_NAME+":"+GITHUB_TOKEN+"@", '')
                print(f"""
        {{
            "name": "{name}",
			"pip": "git+{remote_url}@{branch}#egg=openimis-be-{name}"
		}},
                      
        """)

if __name__ == "__main__":
    target_directory = "./src"
    scan_directory(target_directory)
