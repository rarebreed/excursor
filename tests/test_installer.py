

import pytest
from excursor.core.installer import PythonDevel, SysInstaller


def test_sys_installer():
    installer = SysInstaller()
    print(installer)


@pytest.mark.asyncio
async def test_py_devel():
    pd = PythonDevel()
    extras = pd.sys_installer.extras("-y", foo="bar", baz="10")
    assert extras == "-y --foo bar --baz 10"

    _, proc = await pd.sys_installer.install(pd.devel_libs, flags="-y")
    assert proc.returncode == 0


def savings(
    salary: float,  # 144000
    r: float,  # .033
    savings: float,  # 320000
    s: float = .08,  # .08
    inp: float = .17,  # .17
    years: int = 14  # 13
):
    bonus = 0
    total_bonus = 0
    for i in range(years):
        salary = salary * (1.0 + r)
        savings = (savings + (salary * inp)) * (1.0 + s)
        bonus = salary * .13 * 1.2
        total_bonus += bonus
        print(f"In {2025 + i} {salary=}, {savings=}, {bonus=}, and {total_bonus=}")
