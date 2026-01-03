from typing import Literal, TypeAlias
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone

app = FastAPI()


TimeUnits: TypeAlias = Literal["days", "hours", "minutes", "seconds"]
TimeDelta: TypeAlias = dict[TimeUnits, float]


class Interval(BaseModel):
    from_delta: TimeDelta = {}
    until_delta: TimeDelta = {}


@app.get("/dt/time")
def date_now():
    return {"time": datetime.now().isoformat()}


@app.get("/dt/time_from")
def date_from(days_back: int):
    now = datetime.now(tz=timezone.utc)
    start = now - timedelta(days=days_back)
    return {"time": start.isoformat()}


@app.post("/dt/interval")
def get_interval(interval: Interval):
    now = datetime.now(tz=timezone.utc)
    start = now - timedelta(**interval.from_delta)
    end = now - timedelta(**interval.until_delta)
    if start > end:
        raise HTTPException(status_code=400, detail="from_delta must be greater than until_delta")
    return {"interval": f"{start.isoformat()}/{end.isoformat()}"}
