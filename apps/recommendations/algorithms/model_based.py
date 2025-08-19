from surprise import Dataset, Reader, SVD
from ..utils import get_ratings_df

def get_recommendations(user_id, top_k=10, threshold=4.0):
    df = get_ratings_df()
    if df.empty:
        return []

    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df[['user_id', 'item_id', 'rating']], reader)
    trainset = data.build_full_trainset()

    algo = SVD()
    algo.fit(trainset)

    # Cek apakah user ada di training set
    try:
        inner_uid = trainset.to_inner_uid(user_id)
    except ValueError:
        return []  # Cold-start: user belum punya interaksi apa pun

    # Buat anti-testset hanya untuk user ini
    anti_testset = trainset.build_anti_testset()
    anti_user_testset = [entry for entry in anti_testset if entry[0] == user_id]

    predictions = algo.test(anti_user_testset)
    filtered = [(int(pred.iid), pred.est) for pred in predictions if pred.est >= threshold]
    return sorted(filtered, key=lambda x: x[1], reverse=True)[:top_k]
