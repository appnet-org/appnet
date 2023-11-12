"""
Utility functions for executing commands in remote hosts/containers.
"""
import os
import subprocess
from typing import List


def error_handling(res, msg):
    """Output the given error message and the stderr contents if the subprocess exits abnormally.

    Args:
        res (CompletedProcess[bytes]): the returned object from subproces.run().
        msg: error message printed before the stderr contents.
    """
    assert res.returncode == 0, f"{msg}\nError msg: {res.stderr.decode('utf-8')}"


def execute_remote_host(host: str, cmd: List[str]) -> str:
    """Execute commands on remote host.

    Args:
        host: hostname.
        cmd: A list including the command and all options.

    Returns:
        The output of the command, or "xxx"if "--dry_run" is provided.
    """
    if os.getenv("DRY_RUN") == "1":
        return "xxx"
    print(f"Executing command {' '.join(cmd)} on host {host}...")
    res = subprocess.run(["ssh", host] + cmd, capture_output=True)
    error_handling(res, f"Error when executing command")
    return res.stdout.decode("utf-8")


def execute_remote_container(service: str, host: str, cmd: List[str]) -> str:
    """Execute commands in remote docker container.

    Args:
        service: Service name (determines the container name).
        host: hostname.
        cmd: A list including the command and all options.

    Returns:
        The output of the command, or "xxx"if "--dry_run" is provided.
    """
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
    """Copy local files/directories into remote containers.

    Args:
        service: Servie name.
        host: hostname.
        local_path: Path to the local file/directory.
        remote_path: The target path in the remote container.
    """
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
