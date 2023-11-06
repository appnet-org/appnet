import os
import subprocess
from typing import List


def error_handling(res, msg):
    assert res.returncode == 0, f"{msg}\nError msg: {res.stderr.decode('utf-8')}"


def execute_remote_host(host: str, cmd: List[str]):
    res = subprocess.run(["ssh", host] + cmd, capture_output=True)
    error_handling(res, f"Error when executing command")
    return res.stdout.decode("utf-8")


def execute_remote_container(service: str, host: str, cmd: List[str]):
    print(f"Executing command {' '.join(cmd)} in hotel_{service.lower()}...")
    if os.getenv("DRY_RUN") == "1":
        return "xxx"
    res = subprocess.run(
        ["ssh", host, "docker", "exec", f"hotel_{service.lower()}"] + cmd,
        capture_output=True,
    )
    error_handling(res, f"Error when executing command {cmd} in container")
    return res.stdout.decode("utf-8")


def copy_remote_container(service: str, host: str, local_path: str, remote_path: str):
    print(f"Copy file {local_path} to hotel_{service.lower()}")
    if os.getenv("DRY_RUN") == "1":
        return
    filename = local_path.split("/")[-1]
    res = subprocess.run(
        ["rsync", "-avz", local_path, f"{host}:/tmp"], capture_output=True
    )
    error_handling(res, f"Error when rsync-ing file {local_path}")
    execute_remote_host(
        host,
        ["docker", "cp", f"/tmp/{filename}", f"hotel_{service.lower()}:{remote_path}"],
    )
    execute_remote_host(host, ["rm", "-r", f"/tmp/{filename}"])
