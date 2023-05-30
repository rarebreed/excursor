"""This module contains classes to help execute subprocesses asynchronously.  This allows one to execute and grab
the child process output and continue with other tasks.
"""

import asyncio
from asyncio import Future, SubprocessTransport
from dataclasses import dataclass, field
from pathlib import Path
from subprocess import PIPE
from typing import IO, Any, Self


@dataclass
class ChildProcess(asyncio.SubprocessProtocol):
    exit_future: Future
    save = False
    encoding = "utf8"
    data = bytearray()
    show_out = True

    def pipe_data_received(self, fd: int, data: bytes):
        self.data += data
        if self.show_out:
            print(data.decode(self.encoding), end=None)

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
        match [ret, throw]:
            case [None, _]:
                print("Process has not finished yet")
            case [code, True] if code != val:
                raise Exception(f"Process failed with exit code {code} which was not success of {val}")
            case [code, False] if code != val:
                print(f"Process failed with exit code {code} which was not success of {val}")
            case _:
                print(f"Process was successful with exit code {code}")
                successful = True
        return successful


@dataclass
class Run:
    program: str | None = None
    args: list[str] = field(default_factory=list)
    stdin: int | IO[Any] | None = None
    stdout: int | IO[Any] = PIPE
    stderr: int | IO[Any] = PIPE
    shell = False
    cwd: str | Path | None = None
    bufsize = 0
    text: bool | None = None

    def w_program(self, prog: str) -> Self:
        self.program = prog
        return self

    def w_args(self, *args: str) -> Self:
        self.args = args
        return self

    def w_stdin(self, pipe: int | IO[Any]) -> Self:
        self.stdin = pipe
        return self

    def w_stdout(self, pipe: int | IO[Any]) -> Self:
        self.stdout = pipe
        return self

    def w_stderr(self, pipe: int | IO[Any]) -> Self:
        self.stderr = pipe
        return self

    def w_cwd(self, dir: str | Path) -> Self:
        self.cwd = dir
        return self

    def w_shell(self, sh: bool) -> Self:
        self.shell = sh
        return self

    def w_busize(self, size: int) -> Self:
        self.bufsize = size
        return self

    def w_text(self, txt: bool) -> Self:
        self.text = txt
        return self

    def build(self):
        if not self.program:
            raise Exception("Must supply a cmd string")
        return self

    async def run(self):
        self.build()
        loop = asyncio.get_running_loop()
        exit_future = Future(loop=loop)

        kwargs = self.__dict__.copy()
        cmd: str = kwargs.pop("program")
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


if __name__ == "__main__":

    async def main():
        runner = Run()
        proc = await (runner.w_program("iostat")
                      .w_args("2", "2")
                      .build()
                      .run())
        proc.is_ok()

        runner = Run()
        proc2 = await (runner.w_program("echo 'hi sean' > hi.text")
                       .w_shell(True)
                       .run())
        proc2.is_ok()

    with asyncio.Runner() as launcher:
        launcher.run(main())
