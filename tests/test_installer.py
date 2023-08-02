

import pytest
from excursor.core.installer import PythonDevel, SysInstaller


def test_sys_installer():
    installer = SysInstaller()
    print(installer)


@pytest.mark.asyncio
async def test_py_devel():
    pd = PythonDevel()
    extras = pd.sys_installer.extras("-y", foo="bar")
    assert extras == "-y --foo bar"

    proc = await pd.sys_installer.install(pd.devel_libs, flags="-y")
    assert proc.returncode == 0
