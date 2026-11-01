from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app.cart.models import Cart, CartItem
from app.products.models import Product


class CartRepository:

    def get_cart_by_user_id(
        self,
        db: Session,
        user_id: int,
    ) -> Cart | None:

        statement = (
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(
                selectinload(Cart.items).selectinload(
                    CartItem.product
                )
            )
            .execution_options(populate_existing=True)
        )

        return db.scalar(statement)


    def create_cart(
        self,
        db: Session,
        user_id: int,
    ) -> Cart:
        cart = Cart(user_id=user_id)

        db.add(cart)
        db.commit()
        db.refresh(cart)

        return cart

    
    def get_product(
        self,
        db: Session,
        product_id: int,
    ) -> Product | None:
        statement = select(Product).where(
            Product.id == product_id
        )

        return db.scalar(statement)


    def get_item_by_product_id(
        self,
        db: Session,
        cart_id: int,
        product_id: int,
    ) -> CartItem | None:
        statement = select(CartItem).where(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id
        )

        return db.scalar(statement)

    def get_item_by_id(
        self,
        db: Session,
        cart_id: int,
        item_id: int,
    ) -> CartItem | None:
        statement = select(CartItem).where(
            CartItem.id == item_id,
            CartItem.cart_id == cart_id
        )

        return db.scalar(statement)


    def create_item(
        self,
        db: Session,
        cart_id: int,
        product_id: int,
        quantity: int,
    ) -> CartItem:
        item = CartItem(
            cart_id=cart_id,
            product_id=product_id,
            quantity=quantity
        )

        db.add(item)
        db.commit()
        db.refresh(item)

        return item

    def update_item_quantity(
        self,
        db: Session,
        item: CartItem,
        quantity: int,
    ) -> CartItem:
        item.quantity = quantity

        db.commit()
        db.refresh(item)

        return item

    def delete_item(
        self,
        db: Session,
        item: CartItem
    ) -> None:
        db.delete(item)
        db.commit()

    def clear_items(
        self,
        db: Session,
        cart_id: int
    ) -> None:
        statement = delete(CartItem).where(
            CartItem.cart_id == cart_id
        )

        db.execute(statement)
        db.commit()


cart_repository = CartRepository()



        