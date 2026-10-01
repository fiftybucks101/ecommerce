from sqlalchemy import select
from sqlalchemy.orm import Session

from app.products.models import Product
from app.products.schemas import ProductCreate

class ProductRepository:

    def create(
        self,
        db: Session,
        product_data: ProductCreate
    ) -> Product:

        product = Product(
            **product_data.model_dump()
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        return product

    def get_by_id(
        self,
        db:Session,
        product_id: int
    ) -> Product | None:

        statement = select(Product).where(
            Product.id == product_id
        )

        return db.scalar(statement)

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20
    ) -> list[Product]:

        statement = (
            select(Product)
            .offset(skip)
            .limit(limit)
        )

        return list(db.scalars(statement).all())

    def delete(
        self,
        db: Session,
        product: Product
    ) -> None:

        db.delete(product)
        db.commit()

product_repository = ProductRepository()

    


