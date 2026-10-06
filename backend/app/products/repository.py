from sqlalchemy import select
from sqlalchemy.orm import Session

from app.products.models import Product, Category
from app.products.schemas import ProductCreate, CategoryCreate

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

    
class CategoryRepository:

    def create(
        self,
        db: Session,
        category_data: CategoryCreate
    ) -> Category:

        category = Category(
            **category_data.model_dump()
        )

        db.add(category)
        db.commit()
        db.refresh(category)

        return category

    def get_by_id(
        self,
        db:Session,
        category_id: int
    ) -> Category | None:

        statement = select(Category).where(
            Category.id == category_id
        )

        return db.scalar(statement)

    def delete(
        self,
        db: Session,
        category: Category
    ) -> None:
    
        db.delete(category)
        db.commit()

category_repository = CategoryRepository()

