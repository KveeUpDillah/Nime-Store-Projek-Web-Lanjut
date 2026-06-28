from .general import (
    index,
    home,
    support,
    contact,
    gallery,
    about,
    login,
)

from .auth_views import (
    become_seller,
)

from .seller_views import (
    seller_dashboard,
    confirm_payment,
    product_create,
    product_update,
    product_delete,
    my_seller_profile,
    edit_seller_profile,
    seller_profile,
    review_dashboard,
)

from .product_views import (
    catalog,
    product_detail,
    add_product_review,
    reply_review,
)

from .cart_views import (
    cart_view,
    add_to_cart,
    update_cart_item,
    remove_from_cart,
)

from .order_views import (
    checkout,
    place_order,
    cancel_order,
    cust_orders,
    receipt_data,
    receipt_pdf,
)

from .profile_views import (
    buyer_profile,
    edit_buyer_profile,
)

from .chatbot_views import (
    widget_chat,
    chatbot_page,
    anime_search_api,
    anime_save,
)