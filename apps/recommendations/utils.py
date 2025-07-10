import pandas as pd
from reviews.models import Review
from products.models import Product
from django.contrib.contenttypes.models import ContentType

def get_ratings_df():
    product_type = ContentType.objects.get_for_model(Product)
    qs = Review.objects.filter(content_type=product_type, is_approved=True)
    data = qs.values_list('user_id', 'object_id', 'rating')
    df = pd.DataFrame(list(data), columns=['user_id', 'item_id', 'rating'])
    return df