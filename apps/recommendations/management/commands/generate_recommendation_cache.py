from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recommendations.models import RecommendationCache
from products.models import Product
from recommendations.algorithms import model_based

class Command(BaseCommand):
    help = "Generate and store recommendation cache for all users"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        users = User.objects.filter(role='customer', is_active=True)

        self.stdout.write(f"🧠 Generating recommendations for {users.count()} users...")

        count_created = 0
        for user in users:
            try:
                recommendations = model_based.get_recommendations(user.id, top_k=20)

                # Hapus rekomendasi lama (jika ada)
                RecommendationCache.objects.filter(user=user).delete()

                # Simpan rekomendasi baru
                objects = []
                for product_id, score in recommendations:
                    try:
                        product = Product.objects.get(id=product_id)
                        obj = RecommendationCache(user=user, product=product, score=score)
                        objects.append(obj)
                    except Product.DoesNotExist:
                        continue

                RecommendationCache.objects.bulk_create(objects)
                count_created += len(objects)
                self.stdout.write(self.style.SUCCESS(f"✅ {user.username}: {len(objects)} rekomendasi disimpan"))
            except Exception as e:
                self.stderr.write(f"⚠️ Error for {user.username}: {str(e)}")

        self.stdout.write(self.style.SUCCESS(f"🚀 Done! Total rekomendasi disimpan: {count_created}"))