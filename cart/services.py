from typing import Optional, Union
from store.models import Product
from .cart import Cart


class CartService:

    @staticmethod
    def add_product_to_cart(
            cart: Cart,
            product: Product,
            quantity: int,
            override_quantity: bool = False,
            dimensions: Optional[str] = None,
            frame_type: Optional[str] = None,
            frame_color: Optional[str] = None,
    ) -> None:
        cart.add(
            product=product,
            quantity=quantity,
            override_quantity=override_quantity,
            dimensions=dimensions,
            frame_type=frame_type,
            frame_color=frame_color
        )

    @staticmethod
    def update_cart_quantity(
            cart: Cart,
            product: Product,
            received_quantity: Union[str,int],
    ) -> None:
        try:
            quantity = int(received_quantity)
        except (TypeError, ValueError):
            quantity = 1

        if quantity <= 0:
            cart.remove(product)
        else:
            cart.add(
                product=product,
                quantity=quantity,
                override_quantity=True
            )