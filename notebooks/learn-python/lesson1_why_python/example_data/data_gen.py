from datetime import datetime, timedelta, timezone
from random import randint, random
from typing import Literal, TypeAlias
from pydantic import BaseModel

TestState: TypeAlias = Literal["pass", "fail", "skip", "error"]


class TestResult(BaseModel):
    executed_on: datetime
    result: TestState
    duration: float
    data_path: str
    fail_messge: str | None = None
    exception: str | None = None


class TestSuite(BaseModel):
    tests: dict[str, TestResult]


def make_test_result(days_ago: int, hours: int):
    now = datetime.now(tz=timezone.utc)
    # days_ago = randint(0,30)
    # hours = randint(0, 24)
    executed_on = now - timedelta(days=days_ago, hours=hours)
    results: list[TestState] = ["pass", "fail", "skip", "error"]
    result = results[randint(0, 3)]
    exceptions = ["NullPointerException on foo",
                  "ClientException with status 400"]
    fail_messages = ["expected True but found False",
                     "Did not meet the minimum required value"]
    exception = None
    fail_msg = None
    match result:
        case "error":
            exception = exceptions[randint(0, 1)]
        case "fail":
            fail_msg = fail_messages[randint(0, 1)]
        case _:
            ...

    duration = random() * 60
    ymd_hms = executed_on.strftime("%Y-%m-%d-%H-%M-%S")
    data_path = f"s3: //my-bucket/test_results/{ymd_hms}.json"

    return TestResult(
        executed_on=executed_on,
        result=result,
        duration=duration,
        data_path=data_path,
        exception=exception,
        fail_messge=fail_msg
    )


def make_suite():
    tests = ["test_example_1", "test_it_works", "test_dt_endpoint", "test_service"]
    with open("test-runs.ndjson", "w") as test_f:
        for t in range(100):
            hours = randint(0, 24)
            test_results = {tests[randint(0, 3)]: make_test_result(t, hours) for _ in range(5)}
            suite = TestSuite(tests=test_results)
            test_f.write(suite.model_dump_json() + "\n")


if __name__ == "__main__":
    make_suite()
