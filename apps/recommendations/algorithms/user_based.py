from surprise import Dataset, Reader, KNNBasic
from ..utils import get_ratings_df

def get_recommendations(user_id, top_k=5):
    df = get_ratings_df()
    if df.empty or user_id not in df['user_id'].values:
        return []
    reader = Reader(rating_scale=(1,5))
    data = Dataset.load_from_df(df, reader)
    trainset = data.build_full_trainset()
    algo = KNNBasic(sim_options={'name': 'cosine', 'user_based': True})
    algo.fit(trainset)

    user_inner_id = trainset.to_inner_uid(user_id)
    rated_items = set(j for (j, _) in trainset.ur[user_inner_id])
    all_items = trainset.all_items()
    candidates = [iid for iid in all_items if iid not in rated_items]

    predictions = []
    for item_inner_id in candidates:
        item_raw_id = trainset.to_raw_iid(item_inner_id)
        est_rating = algo.predict(user_id, item_raw_id).est
        predictions.append((item_raw_id, est_rating))
    predictions.sort(key=lambda x: x[1], reverse=True)
    return predictions[:top_k]
