"""
# Creating a pytest plugin

This is a rough outline of how to create a pytest plugin

- Find the hook functions that you will want to insert behavior into
- If you define your own function with the same name as a pytest hook, pytest will invoke it
    - In a class method, you can wrap it with @pytest.hookimpl()
        - A hookimpl must be a generator (yield, and not return)
    - the class can hold fields/state
- Define your own pytest_configure
    - with the passed in config object, call its config.pluginmanager(pluginobj, name)
- It is fairly common to define your own pytest_addoption to add CLI options
"""


from typing import Mapping, Tuple, TypeAlias
from pytest import TestReport, CollectReport, Config
import pytest

CustomReport: TypeAlias = Tuple[str, str, str | Tuple[str, Mapping[str, bool]]]


class PluginReporter:

    def __init__(self):
        self.name: str = "PluginReporter"

    @pytest.hookimpl(hookwrapper=True)
    def pytest_report_teststatus(
        self,
        report: CollectReport | TestReport,
        config: Config
    ):
        print("report teststatus")
        match report:
            case CollectReport():
                ...
            case TestReport():
                print(f"nodeid = {report.nodeid}")
                print(f"location = {report.location}")
                print(f"outcome = {report.outcome}")
        plugin = config.pluginmanager.get_plugin("plugin.reporter")
        if plugin is not None:
            print(f"============ {plugin.name} ===============")
        yield


def pytest_configure(config: Config):
    plugin = PluginReporter()
    config.pluginmanager.register(plugin, "plugin.reporter")
