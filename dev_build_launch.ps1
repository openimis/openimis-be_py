# Sync file
# Requires
# - Python
# - GIT

$base = "c:\dev\fs"
$branch = "develop"

$reposBranch ="openimis-be-contribution_py"`
,"openimis-be-contribution_plan_py"`
,"openimis-be-core_py"`
,"openimis-be-calculation_py"`
,"openimis-be-policyholder_py"`
,"openimis-be-contract_py"

# create base if not existing
if ( -Not (Test-Path -Path $base) ){
	mkdir $base
}


cd $base

if ( -Not (Test-Path -Path openimis-be_py) ){
	Invoke-Expression "git clone https://github.com/openimis/openimis-be_py.git --quiet"
}
cd openimis-be_py
# get the other file from git
#git checkout $branch --quiet -f


 $reposBranch | ForEach-Object  -Process {
	$array = $_.split('@')
	$repo = $array[0];
	
	$curBranch = if ($array.Count -eq 2) {$array[1]} else {$branch}
	Write-output "Pulling repository $repo, branch $curBranch"
	# FIXMEfetch the repository if not existing
	if ( -Not (Test-Path -Path $repo )){
		Invoke-Expression "git clone https://github.com/openimis/$repo.git --quiet"
	}
	# get the other file from git
	cd $repo

	git fetch
	git pull
	git checkout $curBranch  -f
	cd $base
} 

# build the front end

cd openimis-be_py



# assuming venv and openimis-be_py folders are on the same level
if ( -Not (Test-Path -Path ..\venv) ){
	Invoke-Expression "python -m venv ..\venv"
}
Invoke-Expression ..\venv\Scripts\Activate.ps1
$OPENIMIS_CONF='openimis.json '
pip install -r requirements.txt
python modules-requirements.py $OPENIMIS_CONF > modules-requirements.txt
pip install -r modules-requirements.txt
cd openIMIS
$SITE_ROOT='iapi'
$DB_NAME='IMISfs'
$DB_USER='IMISuser'
$DB_PASSWORD='IMISuser@1234'
$DB_HOST='127.0.0.1'
$DB_PORT='1433'
$DJANGO_PORT='8000'


[Environment]::SetEnvironmentVariable("SITE_ROOT", $SITE_ROOT)
[Environment]::SetEnvironmentVariable("REMOTE_USER_AUTHENTICATION", "True")
[Environment]::SetEnvironmentVariable("ROW_SECURITY", "False")
[Environment]::SetEnvironmentVariable("DEBUG", "True")
[Environment]::SetEnvironmentVariable("DB_NAME", $DB_NAME)
[Environment]::SetEnvironmentVariable("DB_USER", $DB_USER)
[Environment]::SetEnvironmentVariable("DB_PASSWORD", $DB_PASSWORD)
[Environment]::SetEnvironmentVariable("DB_HOST", $DB_HOST)
[Environment]::SetEnvironmentVariable("DB_PORT", $DB_PORT)
[Environment]::SetEnvironmentVariable("DJANGO_PORT", $DJANGO_PORT)
[Environment]::SetEnvironmentVariable("OPENIMIS_CONF", "../"$OPENIMIS_CONF)

python manage.py migrate
python manage.py runserver 0.0.0.0:$DJANGO_PORT



