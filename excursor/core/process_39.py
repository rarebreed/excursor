"""This is a python 3.9 compatible version of process.py that doesn't use match or any other 3.10+ feature
"""

import asyncio
from asyncio.subprocess import Process
from dataclasses import dataclass, field
from pathlib import Path
from subprocess import PIPE
import time
from typing import IO, Any

from excursor.func import Maybe


@dataclass
class Run:
    cmd: str
    args: list[str] = field(default_factory=list)
    stdin: int | IO[Any] | None = None
    stdout: int | IO[Any] = PIPE
    stderr: int | IO[Any] = PIPE
    shell: bool = False
    cwd: str | Path | None = None
    bufsize = 0
    text: bool | None = None
    sudo: bool = False
    output: str = ""

    def __post_init__(self):
        if self.cmd.startswith("sudo") and not self.sudo:
            self.sudo = True

        # If there's a space in command, we have to run as a shell command
        if " " in self.cmd:
            self.shell = True

    def __call__(self, *, pw: str | None = None):
        if self.shell:
            return self._run_shell(pw=pw)
        else:
            return self._run_exec(pw=pw)

    async def run(self, *, pw: str | None = None, throw=True):
        proc = await self(pw=pw)
        if throw and proc.returncode != 0:
            raise Exception(f"Process failed with exit code {proc.returncode}")
        return self, proc

    async def _run_exec(self, *, pw: str | None):
        cmd = self.cmd
        args = self.args
        if self.sudo:
            cmd = "sudo"
            args = ["-S", "-k", self.cmd, *self.args]
        print(f"Running command: {cmd} {' '.join(args)}")

        proc = await asyncio.create_subprocess_exec(
            cmd,
            *args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            start_new_session=True,
            cwd=self.cwd
        )
        return await self._get_output(proc, pw)

    async def _run_shell(self, *, pw: str | None):
        cmd = [self.cmd, *self.args]
        cmd = " ".join(cmd)
        if self.sudo:
            cmd = "sudo -S -k " + cmd.replace("sudo ", "")

        print(f"Running command: {cmd}")

        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            start_new_session=True,
            cwd=self.cwd
        )
        return await self._get_output(proc, pw)

    async def _get_output(self, proc: Process, pw: str | None):
        # Read the lines in stderr
        if self.sudo and type(pw) == "str":
            while True:
                if proc.stderr is None:
                    time.sleep(1)
                    continue
                line = await proc.stderr.readuntil(b": ")
                line = line.decode()

                if proc.stdin is None:
                    break

                if self.sudo and line.startswith("[sudo]"):
                    print(line)
                    proc.stdin.write(f"{pw}\n".encode())
                    break
        elif self.sudo and pw is None:
            raise Exception("self.sudo was True, but no password was provided")
        else:
            ...

        while True:
            m_stdout = Maybe(inner=proc.stdout)
            m_stderr = Maybe(inner=proc.stderr)
            out = (m_stdout
                   .map_async(lambda o: o.readline())
                   .map(lambda b: b.decode()))
            if out.inner is not None:
                self.output += out.inner
                print(out, end="")

            err = (m_stderr
                   .map_async(lambda o: o.readline())
                   .map(lambda b: b.decode()))
            if err.inner is not None:
                self.output += err.inner
                print(err, end="")

            if proc.stdout is not None and proc.stdout.at_eof():
                break

        return proc


if __name__ == "__main__":

    async def main():
        run = Run(cmd="ls", args=["-al", "/usr/local"], shell=True)
        # with asyncio.Runner() as launcher:
        #     coro = run()
        #     launcher.run(coro)

        # Run all the subprocesses concurrently
        multi = await asyncio.gather(
            run(),
        )
        # note, we don't have to return multi
        print(multi[0])
    # asyncio.run(main())

    run = Run(cmd="sudo dnf", args=["update", "-y"])
    with asyncio.Runner() as launcher:
        pw = input("Password: ")
        launcher.run(run(pw=pw))
