from surprise import Dataset, Reader, KNNBasic
from ..utils import get_ratings_df

def get_recommendations(user_id, top_k=5):
    df = get_ratings_df()
    if df.empty or user_id not in df['user_id'].values:
        return []
    reader = Reader(rating_scale=(1,5))
    data = Dataset.load_from_df(df, reader)
    trainset = data.build_full_trainset()
    algo = KNNBasic(sim_options={'name': 'cosine', 'user_based': False})
    algo.fit(trainset)

    user_inner_id = trainset.to_inner_uid(user_id)
    rated_items = [j for (j, _) in trainset.ur[user_inner_id]]
    scores = {}
    for item_inner_id, rating in trainset.ur[user_inner_id]:
        neighbors = algo.get_neighbors(item_inner_id, k=10)
        for neighbor_inner_id in neighbors:
            if neighbor_inner_id not in rated_items:
                scores[neighbor_inner_id] = scores.get(neighbor_inner_id, 0) + 1
    top_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    recommended_items = [(trainset.to_raw_iid(item_inner_id), score) for item_inner_id, score in top_items]
    return recommended_items