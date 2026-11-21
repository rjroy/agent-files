"""Linux filesystem and shell isolation for the benchmark's OpenCode runtime."""

import ctypes as c
import errno
import os
from pathlib import Path
import re
import shlex
import shutil
import stat


SYSTEM_PATH = "/usr/bin:/bin"
SYSTEM_FILES = ("/usr", "/bin", "/lib", "/lib64", "/etc/ld.so.cache",
                "/etc/passwd", "/etc/group", "/etc/nsswitch.conf")
NETWORK_FILES = ("/etc/ssl/certs", "/etc/ca-certificates", "/etc/resolv.conf", "/etc/hosts")
RESERVED = {".agents", ".claude", ".git", ".opencode", "agents.md", "claude.md",
            "opencode.json", "opencode.jsonc", "bunfig.toml", ".env", ".envrc"}


def _mount_points():
    # is_mount() cannot identify same-device bind mounts on Linux.
    with open("/proc/self/mountinfo", encoding="utf-8") as mountinfo:
        return {Path(re.sub(r"\\([0-7]{3})", lambda match: chr(int(match[1], 8)), line.split()[4]))
                for line in mountinfo}


def check_workspace(workspace, repository):
    if workspace.is_relative_to(repository) or repository.is_relative_to(workspace):
        raise RuntimeError("OpenCode isolation: the workspace must be outside the repository")
    if not workspace.is_dir():
        raise RuntimeError("OpenCode isolation: workspace is not a directory")
    parent = workspace.parent.stat()
    if parent.st_uid != os.getuid() or parent.st_mode & 0o077:
        raise RuntimeError("OpenCode isolation: workspace needs a private, caller-owned parent directory")
    # OpenCode v2.3.2 checks file permission paths lexically. No pre-existing
    # links (including mount points) can borrow the case's relative permissions.
    device = workspace.stat().st_dev
    mounts = _mount_points()
    if workspace in mounts:
        raise RuntimeError("OpenCode isolation: workspace is already a mount point")
    pending = [workspace]
    while pending:
        for item in pending.pop().iterdir():
            info = item.lstat()
            if item.name.lower() in RESERVED or item.name.lower().startswith(".env."):
                raise RuntimeError("OpenCode isolation: workspace contains configuration or instructions")
            if (stat.S_ISLNK(info.st_mode) or info.st_dev != device or item in mounts
                    or "\\" in item.name):
                raise RuntimeError("OpenCode isolation: workspace contains a link or mount")
            if stat.S_ISDIR(info.st_mode):
                pending.append(item)
            elif not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise RuntimeError("OpenCode isolation: workspace contains a special or linked file")


def bubblewrap():
    path = shutil.which("bwrap", path=SYSTEM_PATH)
    if not path:
        raise RuntimeError("OpenCode isolation requires Linux bubblewrap")
    return path


def base_mounts(bwrap):
    result = [bwrap, "--die-with-parent", "--new-session", "--unshare-user",
              "--unshare-pid", "--unshare-ipc", "--proc", "/proc", "--dev", "/dev",
              "--tmpfs", "/tmp"]
    for path in SYSTEM_FILES:
        result.extend(("--ro-bind-try", path, path))
    return result


def server_command(bwrap, binary, runtime, workspace, coding):
    result = base_mounts(bwrap)
    for name in NETWORK_FILES:
        value = Path(name)
        if value.exists():
            result.extend(("--ro-bind", str(value.resolve()), name))
    return [*result, "--bind", str(runtime), str(runtime),
            "--ro-bind", str(binary), str(binary),
            "--bind" if coding else "--ro-bind", str(workspace), str(workspace),
            "--chdir", str(workspace), "--", str(binary)]


def write_seccomp_filter(path):
    """Deny link/node creation and kernel paths around the mount boundary."""
    try:
        seccomp = c.CDLL("libseccomp.so.2")
    except OSError:
        raise RuntimeError("OpenCode isolation requires libseccomp.so.2") from None
    seccomp.seccomp_init.argtypes = [c.c_uint32]
    seccomp.seccomp_init.restype = c.c_void_p
    seccomp.seccomp_release.argtypes = [c.c_void_p]
    seccomp.seccomp_syscall_resolve_name.argtypes = [c.c_char_p]
    seccomp.seccomp_rule_add.argtypes = [c.c_void_p, c.c_uint32, c.c_int, c.c_uint]
    seccomp.seccomp_export_bpf.argtypes = [c.c_void_p, c.c_int]
    allow = 0x7FFF0000  # SCMP_ACT_ALLOW
    reject = 0x00050000 | errno.EPERM  # SCMP_ACT_ERRNO(EPERM)
    rules = seccomp.seccomp_init(allow)
    if not rules:
        raise RuntimeError("OpenCode isolation could not start a seccomp filter")
    try:
        denied = ("symlink", "symlinkat", "link", "linkat", "mknod", "mknodat",
                  "unshare", "setns", "io_uring_setup", "io_uring_enter", "io_uring_register")
        for name in denied:
            syscall = seccomp.seccomp_syscall_resolve_name(name.encode())
            # libseccomp can return a negative pseudo-number for emulated or
            # ABI-absent syscalls; its rule API expands/ignores it as appropriate.
            if syscall == -1 or seccomp.seccomp_rule_add(rules, reject, syscall, 0):
                raise RuntimeError(f"OpenCode isolation could not block {name}")
        with path.open("wb") as output:
            if seccomp.seccomp_export_bpf(rules, output.fileno()):
                raise RuntimeError("OpenCode isolation could not export its seccomp filter")
    finally:
        seccomp.seccomp_release(rules)


def shell_launcher(bwrap, runtime, workspace):
    seccomp = runtime / "shell.bpf"
    write_seccomp_filter(seccomp)
    command = [*base_mounts(bwrap), "--unshare-net", "--disable-userns",
               "--clearenv", "--setenv", "PATH", SYSTEM_PATH, "--setenv", "HOME", "/tmp",
               "--setenv", "GIT_CONFIG_NOSYSTEM", "1", "--setenv", "GIT_CONFIG_GLOBAL", "/dev/null",
               "--bind", str(workspace), str(workspace), "--seccomp", "3"]
    launcher = runtime / "bash"  # OpenCode selects shell conventions by basename.
    launcher.write_text(
        "#!/bin/sh\n"
        "set -eu\n"
        'here=$(pwd -P)\n'
        f'case "$here/" in {shlex.quote(str(workspace))}/*) ;; *) exit 125 ;; esac\n'
        f"exec 3<{shlex.quote(str(seccomp))}\n"
        f"exec {shlex.join(command)} --chdir \"$here\" -- /bin/bash --noprofile --norc \"$@\"\n",
        encoding="utf-8",
    )
    launcher.chmod(0o700)
    return launcher
