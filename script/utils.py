import re

def parse_pip(pip_str):
    if "https://github.com" in pip_str:
        match =  re.search(r'github.com/(.+).git',pip_str )
        return match.group(1)
    else:
        print("Error name not found")
    
def parse_npm(npm_str):
    if "https://github.com" in npm_str:
        match =  re.search(r'github.com/(.+).git',npm_str )
        return match.group(1)
    else:
        match =  re.search(r'@openimis/(.+)@',npm_str )
    
def walk_config_be(g,be, callback):
    res = []
    for module in be['modules']:
        module_name = parse_pip(module['pip'])
        if module_name is not None:
            repo = g.get_repo(module_name)
            r = callback(repo,module['name'])
            if r is not None:
                res.append(r)
                
    return res
