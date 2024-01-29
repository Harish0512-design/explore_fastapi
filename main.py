from enum import Enum
from typing import Optional, Union

from fastapi import FastAPI
from pydantic import BaseModel, Field

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


@app.get("/files/{filepath:path}")
async def get_filepath(filepath: str):
    return {"filepath": filepath}


# optional query param
@app.get("/countries")
async def get_countries(country_name: Optional[str] = None):
    countries = [
        "India", "USA", "UK", "Australia"
    ]
    if country_name:
        if country_name in countries:
            return {"detail": "Country found"}
        else:
            return {"detail": "Country not found"}
    else:
        return {"detail": "No Query Param"}


@app.get("/states")
async def get_states(skip: int = 0, limit: int = 5):
    states = [
        "AP", "TS", "MH", "AS", "KA", "TN", "J&K", "OS"
    ]
    return {
        "states": states[skip:limit + 1]
    }


# request & Response payload
class Product(BaseModel):
    name: str
    price: float = Field(ge=100, description="Price should be greater than 100")
    description: Optional[str] = None
    tax: float = Field(default=0, ge=0, le=5000,
                       description="Tax should be greater than equal to 0 and less than equal to 5000")


# temporary list acting as a db
product_db = []


@app.post("/products")
async def create_product(product: Product):
    product.tax = product.price + ((5 / 100) * product.price)
    product = product.model_dump()
    product_db.append(product)
    return {
        'detail': product,
        'data': product_db
    }
