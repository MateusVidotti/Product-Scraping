from contextlib import asynccontextmanager
from configs.settings import Settings
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi_pagination import add_pagination, Page
from fastapi_pagination.ext.motor import paginate
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import Any
import uvicorn


class UserIn(BaseModel):
    name: str
    email: str


class UserOut(UserIn):
    _id: int

    class Config:
        orm_mode = True


class ProductIn(BaseModel):
    """
    Modelo para um produto da Open Food Facts.
    """
    code: int
    barcode: str
    status: str
    imported_t: datetime
    url: str
    product_name: str
    quantity: str
    categories: str
    brands: str
    image_url: str


class ProductOut(ProductIn):
    _id: int
    class Config:
        orm_mode = True


@asynccontextmanager
async def lifespan(_: Any) -> None:
    global client
    settings = Settings()
    client = AsyncIOMotorClient(settings.mongo_url)
    yield


app = FastAPI(lifespan=lifespan)
client: AsyncIOMotorClient


@app.get("/", response_model=str)
def root():
    return "Fullstack Challenge 20220626"


@app.get("/products/", response_model=Page[ProductOut])
async def get_products() -> Any:
    return await paginate(client.products_db.produto)


@app.get("/product/:{code}", response_model=ProductOut)
async def get_product_by_code(code):
    produto = await client.products_db.produto.find_one({'code': int(code)})
    if produto is None:
        raise HTTPException(404)
    return produto


add_pagination(app)

if __name__ == "__main__":
    uvicorn.run("pagination_motor:app")
