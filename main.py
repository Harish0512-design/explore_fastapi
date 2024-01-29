from enum import Enum

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/users/{userid}")
async def get_users(userid: int):
    return {"userid": userid}


@app.get("/users/str/{userid}")
async def get_str_user(userid: str):
    return {"userid": userid}


class ModelBase(str, Enum):
    nlp = "nlp"
    dl = "dl"
    ml = "ml"


@app.get("/courses/{course_id}")
async def get_course(course_id: str):

    if course_id == ModelBase.nlp:
        return {"course": "You bought Natural Language Processing Course"}

    elif course_id == ModelBase.dl:
        return {"course": "You bought Deep Learning Course"}

    elif course_id == ModelBase.ml:
        return {"course": "You bought Machine Learning Course"}

    else:
        return {"course": "Invalid Course Id"}
