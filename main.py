import datetime
from enum import Enum
from typing import Optional, Union, Set, List

from fastapi import FastAPI, HTTPException, Depends, Request, File, UploadFile, Form
from pydantic import BaseModel, Field, HttpUrl, EmailStr, field_validator, model_validator
from starlette import status

from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, JSONResponse

app = FastAPI()

templates = Jinja2Templates(directory="templates")


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


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    tags: Set[str] = set()
    images: Union[List[Image], None] = None


class Offer(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    items: List[Item]


@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer


class User(BaseModel):
    email: EmailStr
    username: str
    password: str
    confirm_password: str

    @field_validator("email")
    def validate_email(cls, value: str):
        if 'admin' in value:
            raise ValueError("Admin is not allowed to Register")
        return value


@app.post("/create_user")
async def create_user(user: User):
    user = user.model_dump()
    return {'user': user}


def get_blog_or_404(id: str):
    blogs = {
        "1": "Blog1",
        "2": "Blog2",
        "3": "Blog3",
        "4": "Blog4",
        "5": "Blog5",
    }
    if blogs.get(id):
        return blogs.get(id)
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@app.get("/blog/{id}")
async def get_blog(blog_name: str = Depends(get_blog_or_404)):
    return {"blog": blog_name}


@app.get("/home")
async def get_index_page(request: Request, response_class=HTMLResponse):
    user = {
        "name": "Harish",
        "age": 25
    }
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@app.post("/submit_form")
async def form_handling(assignment: str = Form(...), assignment_file: UploadFile = File(...)):
    print(assignment)
    # print(assignment_file.filename)
    # print(assignment_file.read())
    # print(assignment_file.size)
    assignment_file = await assignment_file.read()
    # print(assignment_file)


class GenderChoices(str, Enum):
    male = "male"
    female = "female"
    others = "others"


class UserRegistrationPayload(BaseModel):
    firstname: str = Field(max_length=15)
    lastname: str = Field(max_length=15)
    username: str = Field(max_length=10)
    dob: datetime.date
    email: EmailStr
    gender: GenderChoices
    phone_number: str = Field(max_length=15)
    password: str
    confirm_password: str

    @model_validator(mode="after")
    def password_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Password and Confirm Password mismatch")
        return self


users = []


@app.post("/register_user", status_code=status.HTTP_201_CREATED)
async def user_creation(user: UserRegistrationPayload, response_class=JSONResponse):
    user = user.model_dump()
    try:
        if user.get('username') in users:
            raise ValueError("User Already Exists.")
        users.append(user)
        return {
            "users": users
        }
    except ValueError as ex:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(ex))
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex))
