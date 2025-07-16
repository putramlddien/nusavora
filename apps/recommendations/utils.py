import pandas as pd
from reviews.models import Review
from products.models import Product
from django.contrib.contenttypes.models import ContentType
from customer.models import ProductViewLog, AddToCartLog, PurchaseLog

def get_ratings_df():
    # 1. Review log (bisa rating 1-5)
    product_type = ContentType.objects.get_for_model(Product)
    review_qs = Review.objects.filter(content_type=product_type, is_approved=True)
    review_data = list(review_qs.values_list('user_id', 'object_id', 'rating'))
    review_df = pd.DataFrame(review_data, columns=['user_id', 'item_id', 'rating'])
    review_df['weight'] = 5  # tertinggi

    # 2. Purchase log (anggap rating default 5)
    purchase_qs = PurchaseLog.objects.all().values_list('user_id', 'product_id')
    purchase_df = pd.DataFrame(list(purchase_qs), columns=['user_id', 'item_id'])
    purchase_df['rating'] = 5
    purchase_df['weight'] = 4

    # 3. Add to Cart log (anggap rating 3)
    cart_qs = AddToCartLog.objects.all().values_list('user_id', 'product_id')
    cart_df = pd.DataFrame(list(cart_qs), columns=['user_id', 'item_id'])
    cart_df['rating'] = 3
    cart_df['weight'] = 2

    # 4. View log (anggap rating 1)
    view_qs = ProductViewLog.objects.all().values_list('user_id', 'product_id')
    view_df = pd.DataFrame(list(view_qs), columns=['user_id', 'item_id'])
    view_df['rating'] = 1
    view_df['weight'] = 1

    # Gabungkan semua
    all_df = pd.concat([review_df, purchase_df, cart_df, view_df], ignore_index=True)

    # **Custom: total score = rating * weight, supaya review/purchase lebih kuat**
    all_df['score'] = all_df['rating'] * all_df['weight']

    # **Ambil skor tertinggi untuk setiap user-item**
    combined_df = all_df.groupby(['user_id', 'item_id'])['score'].max().reset_index()
    combined_df.rename(columns={'score': 'rating'}, inplace=True)

    return combined_df
