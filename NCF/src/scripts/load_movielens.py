import numpy as np
import pandas as pd
from NCF.src.influence.dataset import DataSet
from NCF.src.influence.datasets import Datasets


def load_movielens(train_dir, batch, use_recs=False):
    """
    Load MovieLens dataset and create train, validation, and test DataSet objects.
    
    Args:
        train_dir: Directory containing the data files.
        batch: Batch size (not used for padding in this version).
        use_recs: If True, use recs.csv for test set; otherwise, split from train data.
    
    Returns:
        Datasets object containing train, validation, and test datasets.
    """
    # Đọc dữ liệu chính
    data = np.loadtxt(f"{train_dir}/movielens_train.tsv", delimiter='\t')
    assert data.shape[1] == 4, "Expected 4 columns (user_id, item_id, rating, tt) in movielens_train.tsv"
    assert np.all(data[:, :2] >= 0), "Negative user_id or item_id found in data"

    # Xáo trộn và chia dữ liệu thành train/validation/test (80/10/10)
    np.random.shuffle(data)
    n = len(data)
    train_size = int(0.8 * n)
    valid_size = int(0.1 * n)
    train = data[:train_size]
    valid = data[train_size:train_size + valid_size]
    test = data[train_size + valid_size:]

    # Xử lý tập test nếu use_recs=True
    if use_recs:
        test_df = pd.read_csv('recs.csv')
        assert all(col in test_df.columns for col in ['user', 'rec', 'score']), "recs.csv must have columns: user, rec, score"
        test = test_df[['user', 'rec', 'score']].to_numpy()
        assert np.all(test[:, :2] >= 0), "Negative user_id or item_id found in recs.csv"

    # Tách input (user_id, item_id) và output (rating)
    train_input = train[:, :2].astype(np.int32)
    train_output = train[:, 2].astype(np.float32)
    valid_input = valid[:, :2].astype(np.int32)
    valid_output = valid[:, 2].astype(np.float32)
    test_input = test[:, :2].astype(np.int32)
    test_output = test[:, 2].astype(np.float32)

    # In thông tin để debug
    print(f"Train: {train.shape[0]} samples, max user_id: {int(np.max(train[:, 0]))}, max item_id: {int(np.max(train[:, 1]))}")
    print(f"Valid: {valid.shape[0]} samples, max user_id: {int(np.max(valid[:, 0]))}, max item_id: {int(np.max(valid[:, 1]))}")
    print(f"Test: {test.shape[0]} samples, max user_id: {int(np.max(test[:, 0]))}, max item_id: {int(np.max(test[:, 1]))}")

    # Tạo đối tượng DataSet
    train = DataSet(train_input, train_output)
    validation = DataSet(valid_input, valid_output)
    test = DataSet(test_input, test_output)

    return Datasets(train=train, validation=validation, test=test)