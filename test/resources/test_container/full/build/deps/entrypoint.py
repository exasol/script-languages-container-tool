#!/usr/bin/python3

# FIXME - Move to pytest-exasol-slc

import os
import pwd
import grp
import stat
import subprocess
import sys
USER_NAME = os.getenv("USER_NAME", "test_runner")
HOST_UID = int(os.getenv("HOST_UID", "1000"))
HOST_GID = int(os.getenv("HOST_GID", "1000"))
DOCKER_SOCKET = os.getenv("DOCKER_SOCKET", "/var/run/docker.sock")
DOCKER_GROUP_NAME = os.getenv("DOCKER_GROUP_NAME", "docker")
PYTHON_BINARY = "/usr/bin/python3"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def get_docker_gid(default: int = 998) -> int:
    try:
        st = os.stat(DOCKER_SOCKET)
        if stat.S_ISSOCK(st.st_mode):
            return st.st_gid
    except FileNotFoundError:
        pass
    return default


def ensure_group(name: str, gid: int) -> None:
    """
    Ensure a group exists with the requested name and GID.

    Cases handled:
    - group exists with same name and same GID: do nothing
    - group exists with same name but different GID: modify it
    - group does not exist, but another group already uses the GID: fail loudly
    - group does not exist and GID is free: create it
    """
    try:
        existing = grp.getgrnam(name)
        if existing.gr_gid != gid:
            run(["groupmod", "-g", str(gid), name])
        return
    except KeyError:
        pass

    try:
        grp.getgrgid(gid)
        raise RuntimeError(f"GID {gid} is already in use by another group")
    except KeyError:
        run(["groupadd", "-g", str(gid), name])


def ensure_primary_group(name: str, gid: int) -> None:
    try:
        grp.getgrgid(gid)
    except KeyError:
        run(["groupadd", "-g", str(gid), name])


def ensure_user(name: str, uid: int, gid: int) -> None:
    try:
        existing = pwd.getpwnam(name)
        if existing.pw_uid != uid or existing.pw_gid != gid:
            run(["usermod", "-u", str(uid), "-g", str(gid), name])
    except KeyError:
        run([
            "useradd",
            "-m",
            "-u", str(uid),
            "-g", str(gid),
            "-s", "/bin/bash",
            name,
        ])


def add_user_to_group(name: str, group: str) -> None:
    try:
        run(["usermod", "-aG", group, name])
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Failed to add {name} to group {group}") from exc


def fix_home_ownership(name: str, uid: int, gid: int) -> None:
    home_dir = f"/home/{name}"
    if os.path.isdir(home_dir):
        run(["chown", "-R", f"{uid}:{gid}", home_dir])


def drop_privileges(name: str) -> None:
    pw = pwd.getpwnam(name)
    os.initgroups(name, pw.pw_gid)
    os.setgid(pw.pw_gid)
    os.setuid(pw.pw_uid)


def main() -> None:
    docker_gid = get_docker_gid()

    ensure_group(DOCKER_GROUP_NAME, docker_gid)
    ensure_primary_group(USER_NAME, HOST_GID)
    ensure_user(USER_NAME, HOST_UID, HOST_GID)

    add_user_to_group(USER_NAME, "sudo")
    add_user_to_group(USER_NAME, DOCKER_GROUP_NAME)

    fix_home_ownership(USER_NAME, HOST_UID, HOST_GID)

    drop_privileges(USER_NAME)

    os.execv(PYTHON_BINARY, [PYTHON_BINARY, *sys.argv[1:]])


if __name__ == "__main__":
    main()
