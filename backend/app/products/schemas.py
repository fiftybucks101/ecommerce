from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100
    )

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )

class ProductBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=200
    )

    description: str | None = None

    price: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2
    )

    stock: int = Field(
        ge=0
    )

    category_id: int

    image_url: str | None = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=200
    )

    description: str | None = None

    price: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=10,
        decimal_places=2
    )

    stock: int | None = Field(
        default=None,
        ge=0
    )

    category_id: int | None = None

    image_url: str | None = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
