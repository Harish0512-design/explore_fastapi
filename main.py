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
