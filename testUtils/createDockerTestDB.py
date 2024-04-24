import os
import subprocess
import sys
from time import sleep


def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return process.returncode, stdout.decode(), stderr.decode()


def setup_db():
    # Commands to run your Docker container
    docker_compose = """
    version: '3.8'
    services:
      dbTest:
        container_name: {project_name}-dbTestPSQL
        image: ghcr.io/openimis/openimis-pgsql:latest
        environment:
          - POSTGRES_PASSWORD={db_password}
          - POSTGRES_DB={db_name}
          - POSTGRES_USER={db_user}
          - INIT_MODE={init_mode}
        healthcheck:
          test: pg_isready -U {db_user} -d {db_name}
          interval: 10s
          timeout: 5s
          retries: 5
          start_period: 30s
        ports:
          - {db_host}:5432
        restart: always
        networks:
          openimis-net:
    networks:
      openimis-net:
        driver: bridge
    """.format(
        project_name='openIMIS',
        db_password=os.environ.get('DB_PASSWORD', 'IMISuserP@s'),
        db_name=os.environ.get('DB_NAME', "test_generated_imis"),
        db_user=os.environ.get('DB_USER', 'user'),
        init_mode='demo',
        db_host=os.environ.get('DB_HOST', 5559)
    )
    with open("docker-compose-test.yml", "w") as file:
        file.write(docker_compose)

    return run_command(["docker-compose", "-f", "docker-compose-test.yml", "up", "-d"])


def teardown_db():
    # Commands to stop and remove the Docker container
    return run_command(["docker-compose", "-f", "docker-compose-test.yml", "down"])


if __name__ == "__main__":
    if sys.argv[1] == "setup":
        teardown_db()
        code, out, err = setup_db()
        sleep(10)
    elif sys.argv[1] == "teardown":
        code, out, err = teardown_db()
    else:
        print("Invalid command")
        sys.exit(1)

    if code != 0:
        print("Error ", err)
        sys.exit(code)
    else:
        print("Success ", out)
