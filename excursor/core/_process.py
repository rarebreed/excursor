"""This module contains classes to help execute subprocesses asynchronously.  This allows one to execute and grab
the child process output and continue with other tasks.
"""

import asyncio
from asyncio.subprocess import Process
from dataclasses import dataclass, field
import os
from os import _Environ
from pathlib import Path
from subprocess import PIPE
from typing import IO, Any, Coroutine, Literal, Self


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
    env: _Environ[str] | None = field(repr=False, default=None)

    def __post_init__(self):
        if self.cmd.startswith("sudo") and not self.sudo:
            self.sudo = True

        # If there's a space in command, we have to run as a shell command
        if " " in self.cmd:
            self.shell = True

        if self.env is None:
            self.env = os.environ

    def __call__(self, *, pw: str | None = None) -> Coroutine[Any, Any, Process]:
        if self.shell:
            return self._run_shell(pw=pw)
        else:
            return self._run_exec(pw=pw)

    async def run(self, *, pw: str | None = None, throw=True) -> tuple[Self, Process]:
        proc = await self(pw=pw)
        if throw and proc.returncode != 0:
            raise Exception(f"Process failed with exit code {proc.returncode}")
        return self, proc

    async def _run_exec(self, *, pw: str | None) -> Process:
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
            cwd=self.cwd,
            env=self.env
        )
        return await self._get_output(proc, pw)

    async def _run_shell(self, *, pw: str | None) -> Process:
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
            cwd=self.cwd,
            env=self.env
        )
        return await self._get_output(proc, pw)

    async def _read_stream(self, proc: Process, stream: Literal["stdout", "stderr"]):
        std_stream = proc.stdout if stream == "stdout" else proc.stderr
        while std_stream is not None and not std_stream.at_eof():
            out = await std_stream.readline()
            out = out.decode()
            self.output += out
            print(out, end="")

    async def _get_output(self, proc: Process, pw: str | None) -> Process:
        # Read the lines in stderr
        match[self.sudo, pw]:
            case[True, str()]:
                while True:
                    if proc.stderr is None:
                        break
                    line = await proc.stderr.readuntil(b": ")
                    line = line.decode()

                    if self.sudo and line.startswith("[sudo]"):
                        print(line)
                    if proc.stdin is None:
                        raise Exception("no stdin on child process")
                    else:
                        proc.stdin.write(f"{pw}\n".encode())
                        break
            case[True, None]:
                raise Exception(
                    "self.sudo was True, but no password was provided")
            case _:
                ...

        out_task = asyncio.create_task(self._read_stream(proc, "stdout"))
        err_task = asyncio.create_task(self._read_stream(proc, "stderr"))
        await out_task
        await err_task

        return proc


__all__ = ["Run"]


if __name__ == "__main__":
    async def run1():
        runner1 = Run("iostat", ["2", "2"])
        await runner1.run()

    async def run2():
        runner2 = Run("echo 'hi sean' > hi.text", shell=True)
        await runner2.run()

    async def main():
        run = Run(cmd="ls", args=["-al", "/usr/local"], shell=True)
        # with asyncio.Runner() as launcher:
        #     coro = run()
        #     launcher.run(coro)

        # Run all the subprocesses concurrently
        multi = await asyncio.gather(
            run2(),
            run(),
            # run1(),
        )
        # note, we don't have to return multi
        print(multi[1].stdout)
    asyncio.run(main())

    # run = Run(cmd="sudo dnf", args=["update", "-y"])
    # with asyncio.Runner() as launcher:
    #     pw = input("Password: ")
    #     launcher.run(run(pw=pw))
