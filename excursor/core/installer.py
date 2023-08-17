"""Some convenience classes to make installing system software easier

Includes a utility class PythonDevel that sets up a development environment for python.  It does require at least a
python version 3.10 on the base system to run.  This can be run even on a minimal docker image as long as the python
requirement is met.

It will install the following:

- asdf: to manage different languages and platforms
- The system dependencies needed to build python from source
- python 3.11.4
- poetry to manage python projects
"""


from abc import ABC, abstractmethod
import asyncio
from asyncio.subprocess import Process
from dataclasses import dataclass, field
import os
from pathlib import Path
import platform
import shutil
from typing import Literal, TypeAlias

from excursor.core.process import Run


@dataclass(kw_only=True)
class Installer(ABC):
    os: str = field(init=False)
    arch: str = field(init=False)
    manager: str = field(init=False)
    install_cmd: str = field(init=False)
    uninstall_cmd: str = field(init=False)
    update_cmd: str = field(init=False)

    def extras(self, flags: str | list[str] | None, **extras) -> str:
        match flags:
            case None:
                flags = []
            case str():
                flags = flags.split(" ")
            case list():
                ...
        flags_str = " ".join(f"{f}" for f in flags)
        extra_cmds = " ".join(f"--{k} {v}" for k, v in extras.items())
        return f"{flags_str} {extra_cmds}"

    @abstractmethod
    async def is_installed(self, pkg: str) -> Path | None:
        ...

    # @override # Not available until 3.12

    async def install(
        self,
        pkgs: list[str],
        *,
        pw: str | None = None,
        flags: str | list[str] | None = None,
        **extras
    ) -> tuple[Run, Process]:
        extra_args = self.extras(flags, **extras)
        install = f"{'sudo ' if pw else ''}{self.manager} {self.install_cmd} {extra_args} {' '.join(pkgs)}"
        run = Run(cmd=install, args=[])
        proc = await run(pw=pw)
        return run, proc

    # @override
    async def uninstall(
        self,
        pkgs: list[str],
        *,
        pw: str | None = None,
        flags: str | list[str] | None = None,
        **extras
    ) -> tuple[Run, Process]:
        extra_args = self.extras(flags, extras)
        uninstall = f"{'sudo' if pw else ''}{self.manager} {self.uninstall_cmd} {extra_args} {' '.join(pkgs)}"
        run = Run(cmd=uninstall, args=[])
        proc = await run(pw=pw)
        return run, proc

    # @override
    async def update(
        self,
        pkgs: list[str],
        *,
        pw: str | None = None,
        flags: str | list[str] | None = None,
        **extras
    ) -> tuple[Run, Process]:
        extra_args = self.extras(flags, extras)
        install = f"{'sudo' if pw else ''}{self.manager} {self.update_cmd} {extra_args} {' '.join(pkgs)}"
        run = Run(cmd=install, args=[])
        proc = await run(pw=pw)
        return run, proc


@dataclass(kw_only=True)
class SysInstaller(Installer):
    distro: str = field(init=False)

    def __post_init__(self):
        uname = platform.uname()
        self.os = uname.system.lower()
        self.arch = uname.machine
        match self.os:
            case "linux":
                with open("/etc/os-release", "r") as rel_f:
                    rel_f.read()
                    # TODO: each distro has different contents.  need to determine the keys empirically
                    # For now, assume fedora
                    self.distro = "fedora"
                    self.manager = "dnf"
                    self.install_cmd = "install"
                    self.uninstall_cmd = "remove"
                    self.update_cmd = "upgrade"
            case "darwin":
                self.distro = "macos"
                self.manager = "brew"
                self.install_cmd = "install"
                self.uninstall_cmd = "uninstall"
                self.update_cmd = "update"

    async def is_installed(self, pkg: str) -> Path | None:
        which = Run(cmd=f"which {pkg}", shell=True)
        result = await which()
        if result.returncode != 0:
            return None
        else:
            return Path(which.output.strip())


PackageKeys: TypeAlias = Literal[
    "dev",  # development packages like autopep8, pytest, ruff
    "ds",  # datascience like pytorch and numpy
    "notebook",  # notebook deps like jupyter, matplotlib
    "data",  # data engineering deps like duckdb, polars, and pyarrow
]

PyProjectPkgs: dict[str, list[str]] = {
    "dev": ["autopep8", "pytest", "ruff", "pytest-asyncio"],
    "ds": ["torch", "numpy"],
    "notebook": ["jupyterlab", "matplotlib", "plotly", "ipywidgets"],
    "data": ["pyarrow", "duckdb", "polars"]
}


@dataclass
class PythonDevel:
    """Installs everything needed for python development

    - asdf: for python version management
    - poetry: for python dependency and virtual env management
    - vs code: IDE
        - pylance plugin
    - pyproject template
    """
    pw: str | None = None
    sys_installer: Installer = field(init=False)
    devel_libs: list[str] = field(init=False)

    def __post_init__(self):
        self.sys_installer = SysInstaller()
        match self.sys_installer.distro:
            case "fedora":
                self.devel_libs = [
                    "curl", "git", "make", "gcc", "patch", "zlib-devel", "bzip2", "bzip2-devel", "readline-devel",
                    "sqlite", "sqlite-devel", "openssl-devel", "tk-devel", "libffi-devel", "xz-devel", "libuuid-devel",
                    "gdbm-devel", "libnsl2-devel", "which"
                ]
            case "debian" | "ubuntu":
                self.devel_libs = [
                    "build-essential", "libssl-dev", "zlib1g-dev", "libbz2-dev", "libreadline-dev", "libsqlite3-dev",
                    "curl", "libncursesw5-dev", "xz-utils", "tk-dev", "libxml2-dev", "libxmlsec1-dev", "libffi-dev",
                    "liblzma-dev"
                ]
            case "macos":
                self.devel_libs = ["openssl", "readline", "sqlite3", "xz", "zlib", "tcl-tk"]

    async def shell(self) -> str:
        """Determine default shell type"""
        sh = Run("echo $SHELL")
        await sh()
        print(f"shell is {sh.output}")
        return sh.output.strip().split("/")[-1]

    async def _install_sysdeps(self):
        """Install system deps"""
        if self.sys_installer.distro == "linux":
            pass

        _, proc = await self.sys_installer.install(self.devel_libs, pw=self.pw, flags="-y")
        if self.sys_installer.distro == "macos":
            which = Run("xocde-select --version")
            _, proc = await which.run(throw=False)
            if proc.returncode != 0:
                await Run("xcode-select --install").run()

    async def _install_asdf(self):
        """Install asdf"""
        asdf_home = Path.home() / ".asdf"
        if asdf_home.exists():
            print(f"Deleting old {asdf_home}")
            shutil.rmtree(asdf_home)
        asdf = Run("git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.12.0")
        await asdf()
        shell = await self.shell()
        match shell:
            case "zsh":
                rc = ".zshrc"
            case "bash":
                rc = ".bashrc"
            case other:
                raise Exception(f"shell {other} is not supported")
        with open(Path.home() / rc, "+a") as zshrc:
            zshrc.write("\n. $HOME/.asdf/asdf.sh")
        print("wrote asdf to $HOME/.asdf")

        # Since we're running inside a python interpreter, the PATH hasn't actually changed, even if we source rc
        # so let's manually add them
        asdf_path = Path.home() / ".asdf"
        env = os.environ
        env["PATH"] = f"{asdf_path}/shims:{asdf_path}/bin:" + os.environ["PATH"]
        print(f"PATH is now {env['PATH']}")

        # Install asdf plugins for python, java and nodejs
        python_plugin = Run("asdf plugin add python https://github.com/danhper/asdf-python.git", env=env)
        await python_plugin()
        java_plugin = Run("asdf plugin add java https://github.com/halcyon/asdf-java.git", env=env)
        await java_plugin()
        nodejs_plugin = Run("asdf plugin add nodejs https://github.com/asdf-vm/asdf-nodejs.git", env=env)
        await nodejs_plugin()

        # Install python 3.11.4 through asdf and make it local
        install_python = Run("asdf install python 3.11.4", env=env)
        await install_python()
        local_python = Run("asdf local python 3.11.4", env=env)
        await local_python()

        # TODO: Install graalvm java
        # TODO: Install nodejs

    async def _install_poetry(self):
        # Make sure that we set python in our shell

        Run("curl -sSL https://install.python-poetry.org | python3 -").run()

    async def _create_venv(self, name="venv"):
        # Install pipx

        await Run(f"python3 -m venv {name}")

    async def _create_project(self, name: str, packages: list[PyProjectPkgs]):
        project_path = Path(name)
        if not project_path.exists():
            await Run(f"poetry new {name}").run()

        os.environ["PATH"]
        os.environ["PATH"] = ""

        for key in packages:
            for pkg in PyProjectPkgs[key]:
                cmd = f"poetry add --optional {pkg}"
                if key == "dev":
                    cmd = f"poetry add {pkg} -G dev"
                for pkg in PyProjectPkgs[key]:
                    await Run(cmd).run()


if __name__ == "__main__":
    from argparse import ArgumentParser

    def install(options: list[str]):
        pd = PythonDevel()
        # Determine which parts to do.  First, reduce to a set.  Next, order my the value
        opt_set = set(options)
        installation = [
            pd._install_sysdeps,
            pd._install_asdf,
            pd._install_poetry,
            pd._create_venv
        ]

        if "full" not in opt_set:
            if "sys" not in options:
                installation.remove(pd._install_sysdeps)
            if "asdf" not in options:
                installation.remove(pd._install_asdf)
            if "poetry" not in options:
                installation.remove(pd._install_poetry)
            if "venv" not in options:
                installation.remove(pd._create_venv)

        with asyncio.Runner() as runner:
            for fn in installation:
                runner.run(fn())

        # await pd._create_project("teaching", ["dev", "ds", "notebook" "data"])

    parser = ArgumentParser()
    parser.add_argument(
        "options",
        nargs="+",
        help="What parts to install",
        choices=["full", "sys", "asdf", "poetry", "venv"]
    )
    args = parser.parse_args()

    install(args.options)
