from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.products.models import Product
from app.products.repository import product_repository, category_repository
from app.products.schemas import ProductCreate, ProductUpdate, CategoryCreate


class ProductService:

    def create_product(
        self,
        db: Session,
        product_data: ProductCreate
    ):

        return product_repository.create(
            db,
            product_data
        )

    def get_product(
        self,
        db: Session,
        product_id: int
    ):

        product = product_repository.get_by_id(
            db,
            product_id
        )

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        return product

    def list_products(
        self,
        db: Session,
        page: int = 1,
        limit: int = 20,
        search: str | None = None,
        category_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
    ):

        statement = select(Product)

        if search:
            search_pattern = f"%{search}%"

            statement = statement.where(
                or_(
                    Product.name.ilike(search_pattern),
                    Product.description.ilike(search_pattern)
                )
            )

        if category_id is not None:
            statement = statement.where(
                Product.category_id == category_id
            )

        if min_price is not None:
            statement = statement.where(
                Product.price >= min_price
            )

        if max_price is not None:
            statement = statement.where(
                Product.price <= max_price
            )

        offset = (page - 1) * limit

        statement = (
            statement
            .offset(offset)
            .limit(limit)
        )

        return list(db.scalars(statement).all())

    def update_product(
        self,
        db: Session,
        product_id: int,
        product_data: ProductUpdate
    ):

        product = self.get_product(
            db,
            product_id
        )

        update_data = product_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(product, field, value)

        db.commit()
        db.refresh(product)

        return product

    def delete_product(
        self,
        db: Session,
        product_id: int
    ):

        product = self.get_product(
            db,
            product_id
        )

        product_repository.delete(
            db,
            product
        )

product_service = ProductService()


class CategoryService:

    def create_category(
        self,
        db: Session,
        category_data: CategoryCreate
    ):

        return category_repository.create(
            db,
            category_data
        )

category_service = CategoryService()
    