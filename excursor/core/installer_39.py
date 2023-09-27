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
from typing import Literal, Optional, TypeAlias, Union

from daak.process import Run

PackMan: TypeAlias = Literal["dnf", "apt", "brew"]
OsTypes: TypeAlias = Literal["mac", "linux", "unsupported"]
Distros: TypeAlias = Literal["mac", "fedora", "debian", "ubuntu", "centos", "amazon", "unsupported"]
Arches: TypeAlias = Literal["x86_64", "aarch64"]


@dataclass(kw_only=True)
class Installer(ABC):
    """Abstract base class that defines what an installer does"""
    os: OsTypes = field(init=False)
    arch: Arches = field(init=False)
    manager: PackMan = field(init=False)
    install_cmd: str = "install"
    uninstall_cmd: str = "uninstall"
    update_cmd: str = "update"
    upgrade_cmd: str = "upgrade"

    def extras(self, flags: Union[str, list[str], None], **extras: dict[str, str]) -> str:
        """Additional flags (optional args) and extra dict that will be added to a command

        Parameters
        ----------
        flags : str | list[str] | None
            str or list of flags to add to command

        Returns
        -------
        str
            Additional options to be added to command
        """
        if flags is None:
            flags = []
        elif isinstance(flags, str):
            flags = flags.split(" ")
        elif isinstance(flags, list):
            ...

        flags_str = " ".join(f"{f}" for f in flags)
        extra_cmds = " ".join(f"--{k} {v}" for k, v in extras.items())
        return f"{flags_str} {extra_cmds}"

    @abstractmethod
    async def is_installed(self, pkg: str) -> Union[Path, None]:
        ...

    # @override # Not available until 3.12

    async def install(
        self,
        pkgs: list[str],
        *,
        pw: Optional[str] = None,
        flags: Union[str, list[str], None] = None,
        **extras: dict[str, str]
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
        pw: Optional[str] = None,
        flags: Union[str, list[str], None] = None,
        **extras
    ) -> tuple[Run, Process]:
        extra_args = self.extras(flags, **extras)
        uninstall = f"{'sudo' if pw else ''}{self.manager} {self.uninstall_cmd} {extra_args} {' '.join(pkgs)}"
        run = Run(cmd=uninstall, args=[])
        proc = await run(pw=pw)
        return run, proc

    # @override
    async def update(
        self,
        pkgs: list[str],
        *,
        pw: Optional[str] = None,
        flags: Union[str, list[str], None] = None,
        **extras
    ) -> tuple[Run, Process]:
        extra_args = self.extras(flags, **extras)
        install = f"{'sudo' if pw else ''}{self.manager} {self.update_cmd} {extra_args} {' '.join(pkgs)}"
        run = Run(cmd=install, args=[])
        proc = await run(pw=pw)
        return run, proc


@dataclass(kw_only=True)
class SysInstaller(Installer):
    """Installer of system dependencies (think brew, dnf, apt, etc)
    """
    distro: Distros = field(init=False)

    def __post_init__(self):
        self.get_system()

        match self.os:
            case "linux":
                with open("/etc/os-release", "r") as rel_f:
                    for line in rel_f.readlines():
                        if line.startswith("NAME"):
                            if "fedora" in line:
                                self.distro = "fedora"
                                self.manager = "dnf"
                            elif "debian" in line:
                                self.distro = "debian"
                                self.manager = "apt"
                                self.uninstall_cmd = "remove"
                            elif "ubuntu" in line:
                                self.distro = "ubuntu"
                                self.manager = "apt"
                                self.uninstall_cmd = "remove"
                            elif "centos" in line:
                                self.distro = "centos"
                                self.manager = "dnf"
                            elif "amazon" in line:
                                self.distro = "amazon"
                                self.manager = "dnf"
                            else:
                                self.distro = "unsupported"
                                self.manager = "apt"
                    # TODO: each distro has different contents.  need to determine the keys empirically
                    # For now, assume fedora
                    self.distro = "fedora"
                    self.manager = "dnf"
            case "darwin":
                self.distro = "mac"
                self.manager = "brew"


    def get_system(self):
        uname = platform.uname() 
        system = uname.system.lower()
        arch = uname.machine
        match [system, arch]:
            case ["linux", "x86_64"]:
                self.os = "linux"
                self.arch = "x86_64"
            case ["linux", "aarch64"]:
                self.os = "linux"
                self.arch = "aarch64"
            case ["darwin", "x86_64"]:
                self.os = "mac"
                self.arch = "aarch64"
            case ["darwin", "aarch64"]:
                self.os = "mac"
                self.arch = "aarch64"
            case _:
                self.os = "unsupported"
                self.arch = "x86_64"


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
    pw: Optional[str] = None
    sys_installer: SysInstaller = field(init=False)
    devel_libs: list[str] = field(init=False)
    local_bin_path: bool = False

    def __post_init__(self):
        self.sys_installer = SysInstaller()
        dist = self.sys_installer.distro 
        if dist in ("fedora", "amazon"):
            self.devel_libs = [
                "curl", "git", "make", "gcc", "patch", "zlib-devel", "bzip2", "bzip2-devel", "readline-devel",
                "sqlite", "sqlite-devel", "openssl-devel", "tk-devel", "libffi-devel", "xz-devel", "libuuid-devel",
                "gdbm-devel", "libnsl2-devel", "which"
            ]
        elif dist in ("debian", "ubuntu"):
            self.devel_libs = [
                "build-essential", "libssl-dev", "zlib1g-dev", "libbz2-dev", "libreadline-dev", "libsqlite3-dev",
                "curl", "libncursesw5-dev", "xz-utils", "tk-dev", "libxml2-dev", "libxmlsec1-dev", "libffi-dev",
                "liblzma-dev"
            ]
        elif dist == "macos":
            self.devel_libs = ["openssl", "readline", "sqlite3", "xz", "zlib", "tcl-tk"]
        else:
            print("This OS type is unsupported")
            raise Exception("Unsupported OS")

    async def shell(self) -> str:
        """Determine default shell type"""
        sh = Run("echo $SHELL")
        await sh()
        print(f"shell is {sh.output}")
        return sh.output.strip().split("/")[-1]

    async def which(self, prog: str) -> tuple[str, int | None]:
        runner, proc = await Run(f"which {prog}").run(throw=False)
        return runner.output, proc.returncode

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

    def set_asdf_path(self):
        # Since we're running inside a python interpreter, the PATH hasn't actually changed, even if we source rc
        # so let's manually add them
        asdf_path = Path.home() / ".asdf"
        env = os.environ
        env["PATH"] = f"{asdf_path}/shims:{asdf_path}/bin:" + os.environ["PATH"]
        print(f"PATH is now {env['PATH']}")
        return env
    
    def set_local_path(self):
        local_path = Path.home() / ".local"
        env = os.environ
        env["PATH"] = f"{local_path}/bin:" + os.environ["PATH"]
        print(f"PATH is now {env['PATH']}")
        return env

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
        env = self.set_asdf_path()

        # Install asdf plugins for python, java and nodejs
        python_plugin = Run("asdf plugin add python https://github.com/danhper/asdf-python.git", env=env)
        await python_plugin()
        java_plugin = Run("asdf plugin add java https://github.com/halcyon/asdf-java.git", env=env)
        await java_plugin()
        nodejs_plugin = Run("asdf plugin add nodejs https://github.com/asdf-vm/asdf-nodejs.git", env=env)
        await nodejs_plugin()

        # Get the most recent python version

        # Install python 3.11.4 through asdf and make it local
        install_python = Run("asdf install python 3.11.5", env=env)
        await install_python()
        local_python = Run("asdf local python 3.11.5", env=env)
        await local_python()

        # TODO: Install graalvm java
        # TODO: Install nodejs

    async def _install_poetry(self):
        # Make sure that we set python in our shell

        await Run("curl -sSL https://install.python-poetry.org | python3 -").run()

    async def _create_venv(self, name="venv"):
        # Install pipx
        env = self.set_asdf_path()
        await Run("pip install --user pipx",env=env).run()
        await Run("pipx ensurepath", env=env).run()
        
        # Since we're running inside a python interpreter, the PATH hasn't actually changed, even if we source rc
        # so let's manually add them
        env = self.set_local_path()
        await Run("pipx install virtualenv", env=env).run()
        await Run(f"virtualenv -p python3.11.5 {name}").run()

    async def _create_project(self, name: str, packages: dict[str, list[str]] = PyProjectPkgs):
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
