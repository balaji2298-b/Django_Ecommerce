from .models import Cart, Orderrs  

def get_user_counts(user_id):
    return {
        'cart_count': Cart.objects.filter(user_id=user_id).count(),
        'order_count': Orderrs.objects.filter(user_id=user_id).count(),
        'wishlist_count': Wishlist.objects.filter(user_id=user_id).count(),  # optional
    }
