"""This is a python 3.9 compatible version of process.py that doesn't use match or any other 3.10+ feature
"""

import asyncio
from asyncio.subprocess import Process
from dataclasses import dataclass, field
from pathlib import Path
from subprocess import PIPE
from typing import IO, Any


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
                line = await proc.stderr.readuntil(b": ")
                line = line.decode()

                if self.sudo and line.startswith("[sudo]"):
                    print(line)
                    proc.stdin.write(f"{pw}\n".encode())
                    break
        elif self.sudo and pw is None:
            raise Exception("self.sudo was True, but no password was provided")
        else:
            ...

        while True:
            out = await proc.stdout.readline()
            out = out.decode()
            self.output += out
            print(out, end="")

            err = await proc.stderr.readline()
            err = err.decode()
            self.output += err
            print(err, end="")

            if proc.stdout.at_eof():
                break

        return proc


if __name__ == "__main__":
    async def run1():
        runner1 = Run("iostat", ["2", "2"])
        await runner1.launch()

    async def run2():
        runner2 = Run("echo 'hi sean' > hi.text", shell=True)
        await runner2.launch()

    async def main():
        run = Run(cmd="ls", args=["-al", "/usr/local"], shell=True)
        # with asyncio.Runner() as launcher:
        #     coro = run()
        #     launcher.run(coro)

        # Run all the subprocesses concurrently
        multi = await asyncio.gather(
            run2(),
            run(),
            run1(),
        )
        # note, we don't have to return multi
        print(multi[2])
    # asyncio.run(main())

    run = Run(cmd="sudo dnf", args=["update", "-y"])
    with asyncio.Runner() as launcher:
        pw = input("Password: ")
        launcher.run(run(pw=pw))
