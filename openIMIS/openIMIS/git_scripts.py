import git
import json
import os


from os import path
from django.conf import settings
from openIMIS.openimisapps import openimis_apps


def create_release_branches_backend(version):
    """
       function to create release branches 'release/<version>'
       for all backend modules presented in openimis.json
    """
    output_messages = []
    # modules = openimis_apps()
    # TODO temporary value for modules for test
    modules = ['calculation_rule-fs_income_percentage', 'report', 'policyholder', 'contribution_plan', 'calculation']
    directory = path.abspath(path.join(settings.BASE_DIR, "../.."))
    release_branch = f'release/{version}'
    for module in modules:
        try:
            repo_name = f'openimis-be-{module}_py'
            # check if repo exist - if no - clone to local
            if not path.exists(f'{directory}/{repo_name}'):
                git.Repo.clone_from(
                    f'https://github.com/openimis/openimis-be-{module}_py.git',
                    f'{directory}/{repo_name}'
                )
            local_repo = git.Repo(f'{directory}/{repo_name}')
            current_branch = local_repo.active_branch
            if current_branch != 'develop':
                local_repo.git.checkout('develop')
            # create release branch if not exist in local repo
            if release_branch not in local_repo.branches:
                local_repo.git.branch(release_branch)
            local_repo.git.checkout(release_branch)
            # pull changes from develop
            local_repo.git.pull("origin", 'develop')
            # push branch to remote branch
            local_repo.git.push("origin", release_branch)
            # back to branch previously assigned
            local_repo.git.checkout(current_branch)
            output_messages.append({
                'module': module,
                'message': f'Operation succeded'
            })
        except Exception as exc:
            output_messages.append({
                'module': module,
                'message': f'Operation failed: {exc}'
            })
    return output_messages


def create_release_branches_frontend(version):
    """
       function to create release branches 'release/<version>'
       for all frontend modules presented in openimis.json
    """
    output_messages = []
    # check if main frontend module is presented locally.
    directory = path.abspath(path.join(settings.BASE_DIR, "../.."))
    if not path.exists(f'{directory}/openimis-fe_js'):
        raise Exception("Main assembly frontend module not presented locally")

    # take the module names from fe openimis.json
    modules = []
    with open(f'{directory}/openimis-fe_js/openimis.json') as json_file:
        json_data = json.load(json_file)
        for module in json_data['modules']:
            module_name = module['npm'].split('/')[1].split('@')[0]
            modules.append(module_name)

    # TODO temporary value for modules for test
    modules = ['fe-payment']
    release_branch = f'release/{version}'

    for module in modules:
        try:
            repo_name = f'openimis-{module}_js'
            # check if repo exist - if no - clone to local
            if not path.exists(f'{directory}/{repo_name}'):
                git.Repo.clone_from(
                    f'https://github.com/openimis/openimis-{module}_js.git',
                    f'{directory}/{repo_name}'
                )
            local_repo = git.Repo(f'{directory}/{repo_name}')
            current_branch = local_repo.active_branch
            if current_branch != 'develop':
                local_repo.git.checkout('develop')
            # create release branch if not exist in local repo
            if release_branch not in local_repo.branches:
                local_repo.git.branch(release_branch)
            local_repo.git.checkout(release_branch)
            # pull changes from develop
            local_repo.git.pull("origin", 'develop')
            # push branch to remote branch
            local_repo.git.push("origin", release_branch)
            # back to branch previously assigned
            local_repo.git.checkout(current_branch)
            output_messages.append({
                'module': module,
                'message': f'Operation succeded'
            })
        except Exception as exc:
            output_messages.append({
                'module': module,
                'message': f'Operation failed: {exc}'
            })
    return output_messages
