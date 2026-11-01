from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.cart.models import Cart
from app.cart.repository import cart_repository
from app.cart.schemas import (
    CartItemResponse,
    CartResponse,
)


class CartService:

    def _get_or_create_cart(
        self,
        db: Session,
        user_id: int,
    ) -> Cart:
        cart = cart_repository.get_cart_by_user_id(
            db,
            user_id
        )

        if cart is None:
            cart_repository.create_cart(db, user_id)

            cart = cart_repository.get_cart_by_user_id(
                db,
                user_id,
            )

        if cart is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to retrieve cart.",
            )

        return cart

    def _build_cart_response(
        self,
        cart: Cart,
    ) -> CartResponse:
        response_items = []
        total = Decimal("0.00")

        for item in cart.items:
            unit_price = item.product.price
            subtotal = unit_price * item.quantity

            response_items.append(
                CartItemResponse(
                    id=item.id,
                    product_id=item.product_id,
                    product_name=item.product.name,
                    unit_price=unit_price,
                    quantity=item.quantity,
                    subtotal=subtotal,
                )
            )

            total += subtotal

        return CartResponse(
            id=cart.id,
            items=response_items,
            total=total,
        )

    def get_cart(
        self,
        db: Session,
        user_id: int,
    ) -> CartResponse:
        cart = self._get_or_create_cart(db, user_id)

        return self._build_cart_response(cart)

    def add_item(
        self,
        db: Session,
        user_id: int,
        product_id: int,
        quantity: int,
    ) -> CartResponse:
        cart = self._get_or_create_cart(db, user_id)

        product = cart_repository.get_product(
            db,
            product_id
        )

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )

        if product.stock <= 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Product is out of stock.",
            )

        item = cart_repository.get_item_by_product_id(
            db,
            cart.id,
            product_id
        )

        new_quantity = quantity

        if item is not None:
           new_quantity = item.quantity + quantity

        if new_quantity > product.stock:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Requested quantity exceeds available stock.",
            )

        if item is None:
            cart_repository.create_item(
                db,
                cart.id,
                product_id,
                new_quantity
            )
        else:
            cart_repository.update_item_quantity(
                db,
                item,
                new_quantity
            )

        updated_cart = self._get_or_create_cart(
            db,
            user_id
        )

        return self._build_cart_response(updated_cart)

    def update_item(
        self,
        db: Session,
        user_id: int,
        item_id: int,
        quantity: int
    ) -> CartResponse:
        cart = self._get_or_create_cart(db, user_id)

        item = cart_repository.get_item_by_id(
            db,
            cart.id,
            item_id,
        )

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found.",
            )

        product = cart_repository.get_product(
            db,
            item.product_id,
        )

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )

        if quantity > product.stock:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Requested quantity exceeds available stock.",
            )

        cart_repository.update_item_quantity(
            db,
            item,
            quantity,
        )

        updated_cart = self._get_or_create_cart(
            db,
            user_id,
        )

        return self._build_cart_response(updated_cart)

    def remove_item(
        self,
        db: Session,
        user_id: int,
        item_id: int,
    ) -> None:
        cart = self._get_or_create_cart(db, user_id)

        item = cart_repository.get_item_by_id(
            db,
            cart.id,
            item_id,
        )

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found.",
            )

        cart_repository.delete_item(db, item)

    def clear_cart(
        self,
        db: Session,
        user_id: int,
    ) -> None:
        cart = self._get_or_create_cart(db, user_id)

        cart_repository.clear_items(db, cart.id)

cart_service = CartService()


