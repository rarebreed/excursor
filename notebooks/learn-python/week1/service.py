from fastapi import FastAPI
from datetime import datetime

app = FastAPI()


@app.get("/time")
def date_now():
    return {"time": datetime.now().isoformat()}
