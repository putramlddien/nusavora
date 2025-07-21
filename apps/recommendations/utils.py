import pandas as pd
from reviews.models import Review
from products.models import Product
from django.contrib.contenttypes.models import ContentType
from customer.models import ProductViewLog, AddToCartLog, PurchaseLog
from accounts.models import NusavoraUser  # untuk ambil favorites

def get_ratings_df():
    product_type = ContentType.objects.get_for_model(Product)

    # 1. Review (rating asli user, 1–5)
    review_qs = Review.objects.filter(content_type=product_type, is_approved=True)
    review_data = list(review_qs.values_list('user_id', 'object_id', 'rating'))
    review_df = pd.DataFrame(review_data, columns=['user_id', 'item_id', 'rating'])

    # 2. Purchase log → rating = 5
    purchase_qs = PurchaseLog.objects.all().values_list('user_id', 'product_id')
    purchase_df = pd.DataFrame(list(purchase_qs), columns=['user_id', 'item_id'])
    purchase_df['rating'] = 5

    # 3. Favorites → rating = 4
    favorite_data = []
    for user in NusavoraUser.objects.prefetch_related('favorites'):
        for prod in user.favorites.all():
            favorite_data.append((user.id, prod.id))
    favorite_df = pd.DataFrame(favorite_data, columns=['user_id', 'item_id'])
    favorite_df['rating'] = 4

    # 4. Add to cart log → rating = 3
    cart_qs = AddToCartLog.objects.all().values_list('user_id', 'product_id')
    cart_df = pd.DataFrame(list(cart_qs), columns=['user_id', 'item_id'])
    cart_df['rating'] = 3

    # 5. View log → rating = 1
    view_qs = ProductViewLog.objects.all().values_list('user_id', 'product_id')
    view_df = pd.DataFrame(list(view_qs), columns=['user_id', 'item_id'])
    view_df['rating'] = 1

    # Gabungkan semua
    all_df = pd.concat([review_df, purchase_df, favorite_df, cart_df, view_df], ignore_index=True)

    # Ambil rating tertinggi per user-item
    combined_df = all_df.groupby(['user_id', 'item_id'])['rating'].max().reset_index()

    return combined_df
