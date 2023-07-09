from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class StatusProduto(str, Enum):
    DRAFT = 'draft'
    IMPORTED = 'imported'


class ProductModel(BaseModel):
    """
    Modelo para um produto da Open Food Facts.
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    code: Optional[int]
    barcode: Optional[str]
    status: StatusProduto
    imported_t: Optional[datetime or None]
    url: str
    product_name: Optional[str]
    quantity: Optional[str]
    categories: Optional[str]
    brands: Optional[str]
    image_url: Optional[str]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "code": 8000500310427,
                "barcode": "8000500310427(EAN / EAN-13)",
                "status": "imported",
                "url": "https://world.openfoodfacts.org//product/8000500310427/nutella-biscuits",
                "product_name": "Nutella biscuits - 304g",
                "quantity": "304 g",
                "categories": "Snacks, Sweet snacks, Biscuits and cakes, Biscuits, Chocolate biscuits, Filled biscuits",
                "packaging": "Plastic, O 7 - Other plastics",
                "brands": "Nutella, Ferrero",
                "image_url": "https://images.openfoodfacts.org/images/products/800/050/031/0427/front_en.224.full.jpg",

            }
        }


# class ProductModel(BaseModel):
#     """
#     Modelo para um produto da Open Food Facts.
#     """
#     id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
#     code: int = Field(...)
#     barcode: str = Field(...)
#     status: StatusProduto = Field(...)
#     imported_t: datetime = Field(default_factory=datetime.now)
#     url: str = Field(...)
#     product_name: str = Field(...)
#     quantity: str = Field(...)
#     categories: str = Field(...)
#     brands: str = Field(...)
#     image_url: str = Field(...)
#
#     class Config:
#         allow_population_by_field_name = True
#         arbitrary_types_allowed = True
#         json_encoders = {ObjectId: str}
#         schema_extra = {
#             "example": {
#                 "code": 8000500310427,
#                 "barcode": "8000500310427(EAN / EAN-13)",
#                 "status": "imported",
#                 "url": "https://world.openfoodfacts.org//product/8000500310427/nutella-biscuits",
#                 "product_name": "Nutella biscuits - 304g",
#                 "quantity": "304 g",
#                 "categories": "Snacks, Sweet snacks, Biscuits and cakes, Biscuits, Chocolate biscuits, Filled biscuits",
#                 "packaging": "Plastic, O 7 - Other plastics",
#                 "brands": "Nutella, Ferrero",
#                 "image_url": "https://images.openfoodfacts.org/images/products/800/050/031/0427/front_en.224.full.jpg",
#
#             }
#         }


class UpdateProductModel(BaseModel):
    """
    Modelo para um produto da Open Food Facts.
    """
    # code: Optional[int]
    # barcode: Optional[str]
    status: Optional[StatusProduto]
    imported_t: datetime = Field(default_factory=datetime.now)
    product_name: Optional[str]
    quantity: Optional[str]
    categories: Optional[str]
    packaging: Optional[str]
    brands: Optional[str]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "code": 8000500310427,
                "barcode": "8000500310427(EAN / EAN-13)",
                "status": "imported",
                "product_name": "Nutella biscuits - 304g",
                "quantity": "304 g",
                "categories": "Snacks, Sweet snacks, Biscuits and cakes, Biscuits, Chocolate biscuits, Filled biscuits",
                "packaging": "Plastic, O 7 - Other plastics",
                "brands": "Nutella, Ferrero",

            }
        }