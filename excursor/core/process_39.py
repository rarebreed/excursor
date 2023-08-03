"""This is a python 3.9 compatible version of process.py that doesn't use match or any other 3.10+ feature
"""

import asyncio
from asyncio import Future, SubprocessTransport
from asyncio.subprocess import Process
from dataclasses import dataclass, field
from pathlib import Path
from subprocess import PIPE
from typing import IO, Any


@dataclass
class ChildProcess(asyncio.SubprocessProtocol):
    exit_future: Future
    save = False
    encoding = "utf8"
    data = bytearray()
    show_out = True

    def pipe_data_received(self, fd: int, data: bytes):
        if self.save:
            self.data += data
        if self.show_out:
            print(f"{fd}: " + data.decode(self.encoding), end=None)

    def process_exited(self):
        self.exit_future.set_result(True)


@dataclass
class ProcessResult:
    future: Future
    proto: ChildProcess
    transport: SubprocessTransport

    def is_done(self):
        return self.future.done()

    def exit_code(self):
        return self.transport.get_returncode()

    def output(self) -> str:
        return self.proto.data.decode(self.encoding)

    def is_ok(self, val=0, throw=False):
        ret = self.exit_code()

        successful = False

        if ret is None:
            print("Process has not finished yet")
        elif ret != val and throw:
            raise Exception(f"Process failed with exit code {ret} which was not success of {val}")
        elif ret != val and not throw:
            print(f"Process failed with exit code {ret} which was not success of {val}")
        else:
            print(f"Process was successful with exit code {ret}")
            successful = True
        return successful


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

    def w_cmd(self, prog: str) -> "Run":
        self.cmd = prog
        return self

    def w_args(self, *args: str) -> "Run":
        self.args = args
        return self

    def w_stdin(self, pipe: int | IO[Any]) -> "Run":
        self.stdin = pipe
        return self

    def w_stdout(self, pipe: int | IO[Any]) -> "Run":
        self.stdout = pipe
        return self

    def w_stderr(self, pipe: int | IO[Any]) -> "Run":
        self.stderr = pipe
        return self

    def w_cwd(self, dir: str | Path) -> "Run":
        self.dir = dir
        return self

    def w_shell(self, sh: bool) -> "Run":
        self.shell = sh
        return self

    def w_busize(self, size: int) -> "Run":
        self.bufsize = size
        return self

    def w_text(self, txt: bool) -> "Run":
        self.text = txt
        return self

    def build(self):
        if not self.cmd:
            raise Exception("Must supply a cmd string")
        return self

    async def launch(self):
        self.build()
        loop = asyncio.get_running_loop()
        exit_future = Future(loop=loop)

        kwargs = self.__dict__.copy()
        cmd: str = kwargs.pop("cmd")
        kwargs.pop("sudo")
        args: list[str] = kwargs.pop("args")

        runner = loop.subprocess_exec
        if self.shell:
            cmd = f"{cmd} {' '.join(args)}"
            args = []
            runner = loop.subprocess_shell

        print(f"Executing: {cmd} {kwargs}")

        transport, protocol = await runner(
            lambda: ChildProcess(exit_future),
            cmd,
            *args,
            **kwargs
        )

        await exit_future
        transport.close()
        return ProcessResult(future=exit_future, proto=protocol, transport=transport)

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
        proc = await runner1.launch()
        proc.is_ok()

    async def run2():
        runner2 = Run("echo 'hi sean' > hi.text", shell=True)
        proc2 = await runner2.launch()
        proc2.is_ok()

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
