from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.cart.schemas import (
    CartItemCreate,
    CartItemUpdate,
    CartResponse,
)
from app.cart.service import cart_service
from app.db.sessions import get_db
from app.users.models import User

router = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)

@router.get(
    "",
    response_model=CartResponse
)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return cart_service.get_cart(
        db,
        current_user.id,
    )



@router.post(
    "/items",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
)
def add_item(
    item_data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return cart_service.add_item(
        db=db,
        user_id=current_user.id,
        product_id=item_data.product_id,
        quantity=item_data.quantity,
    )

@router.put(
    "/items/{item_id}",
    response_model=CartResponse,
)
def update_item(
    item_id: int,
    item_data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return cart_service.update_item(
        db=db,
        user_id=current_user.id,
        item_id=item_id,
        quantity=item_data.quantity,
    )


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart_service.remove_item(
        db,
        current_user.id,
        item_id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)



@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
)
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart_service.clear_cart(
        db,
        current_user.id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)