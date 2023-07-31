"""Some convenience classes to make installing system software easier
"""


from dataclasses import dataclass, field
import platform
from typing import NamedTuple

from excursor.core.process import Run


@dataclass
class Installer:
    os: str = field(init=False)
    arch: str = field(init=False)
    installer: str = field(init=False)

    def __post_init__(self):
        uname = platform.uname()
        self.os = uname.system.lower()
        self.arch = uname.machine
        match self.os:
            case "linux":
                # TODO: assume fedora for now
                self.installer = "dnf"
            case "macos":
                self.installer = "brew"
            case _:
                raise Exception("Unsupported OS")

    async def _determine_distro(self):
        cmd = Run("cat /etc/-os-release")
        await cmd()
        print(cmd.output)

    async def install_packages(self, pw: str, pkgs: list[str]):
        install = Run(f"sudo {self.installer}", args=pkgs)
        return await install()


@dataclass
class PythonDevel(Installer):
    devel_libs: list[str] = field(init=False)

    def __post_init__(self):
        ...


if __name__ == "__main__":
    installer = Installer()
    print(installer)
