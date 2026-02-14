import hashlib
import os
from ast import literal_eval
from pathlib import Path
import pickle
import numpy as np
import pandas as pd
from commons.handle_causal import find_child  # Chỉ cần find_child, không cần find_causal nữa
from NCF.src.helper import get_model
from NCF.src.scripts.load_movielens import load_movielens


def init_all_results(ks):
    """
    init a list of results to store explanations produced by explanation algorithms
    :param ks: list of k values to considered
    :return: a list of dictionaries where each one stores the result of one k value
    """
    all_results = []
    for _ in ks:
        all_results.append(
            {
                'user': [],
                'item': [],
                'topk': [],
                'counterfactual': [],
                'predicted_scores': [],
                'replacement': []
            }
        )
    return all_results


def append_result(ks, all_results, user_id, res):
    """
    append res to all_results where res is the result of an explanation algorithm
    :param ks: list of k values considered
    :param all_results: a dataset of results
    :param user_id: id of user explained
    :param res: the result produced by the explanation algorithms
    """
    for j in range(len(ks)):
        all_results[j]['user'].append(user_id)
        counterfactual, rec, topk, predicted_scores, repl = res[j]
        all_results[j]['item'].append(rec)
        all_results[j]['topk'].append(topk)
        all_results[j]['counterfactual'].append(counterfactual)
        all_results[j]['predicted_scores'].append(predicted_scores)
        all_results[j]['replacement'].append(repl)

        print('k =', ks[j])
        if not counterfactual:
            print(f"Can't find counterfactual set for user {user_id}")
        else:
            print(f"Found a set of size {len(counterfactual)}: {counterfactual}")
            print("Old top k: ", topk)
            print("Replacement: ", repl, predicted_scores)


def counterfactual2path(user, counterfactual_set):
    """
    find a directory name to store the retrained model for a user-explanation pair
    :param user: id of the user
    :param counterfactual_set: the counterfactual explanation
    :return: a directory name
    """
    res = f'{user}-{"-".join(str(x) for x in sorted(counterfactual_set))}'
    if len(res) < 255:
        return res
    return hashlib.sha224(res.encode()).hexdigest()


def read_row_from_result_file(row):
    """
    read a row from the result file
    :param row: the row to be parsed
    :return: if the counterfactual set is None then return None, else:
        idx: the id of the instance
        user_id: id of user
        topk: top k recommendations
        counterfactual: counterfactual set
        predicted_scores: predicted scores of the original top k items
        replacement: the predicted replacement item
    """
    idx, user_id, item_id, topk, counterfactual, predicted_scores, replacement = row[:7]
    if not isinstance(counterfactual, str):
        print('skip', idx, user_id, item_id, topk, counterfactual, predicted_scores, replacement)
        return None, None, None, None, None, None, None
    topk = literal_eval(topk)
    counterfactual = literal_eval(counterfactual)
    if isinstance(predicted_scores, str):
        predicted_scores = literal_eval(predicted_scores)
    else:
        predicted_scores = None
    print('begin idx', idx, user_id, item_id, topk, counterfactual, predicted_scores, replacement)
    return idx, user_id, item_id, topk, counterfactual, predicted_scores, replacement


def prepare_path(home_dir, user_id, counterfactual, seed):
    """
    create a path to store retrained model
    :param home_dir: home directory to store the retrained model
    :param user_id: id of user
    :param counterfactual: counterfactual set
    :param seed: a unique number of differentiate multiple retrains
    :return: the path of the created directory or None if this retrain has already been done
    """
    path = f'{home_dir}/{counterfactual2path(user_id, counterfactual)}/{seed}/'
    if Path(path).exists():
        return None
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def prepare_new_scores(user_id, key, home_dir):
    """
    prepare to get new scores for a pretrained model
    :param user_id: id of user to be scored
    :param key: directory name where the pretrained models are stored
    :param home_dir: home directory where all pretrained models are stored
    :return: None if the pretrained model doesn't exist or the subfolders where the pretrained models are stored
    """
    # load model from disk
    if not Path(f'{home_dir}/{key}/').exists():
        print('missing', user_id, key)
        return None
    subfolders = sorted([f.path for f in os.scandir(f'{home_dir}/{key}/') if f.is_dir()])
    if len(subfolders) != 5:
        print('missing', user_id, key, len(subfolders))
        return None
    return subfolders


def get_topk_scores(idx, user_id, item_id, topk, counterfactual, predicted_scores, replacement, item2scores, home_dir,
                    get_scores):
    """
    get the new scores of top-k items
    Args:
        idx: test number
        user_id: ID of user
        item_id: ID of item
        topk: the top-k items
        counterfactual: the counterfactual set
        predicted_scores: the predicted scores
        replacement: the replacement item
        item2scores: a dict for caching
        home_dir: the home directory, where trained models are stored

    Returns: a 2d array where each row is the scores of top-k items in one retrain.
    """
    scores = get_scores(idx, user_id, item_id, topk, counterfactual, predicted_scores, replacement, item2scores,
                        home_dir)
    if scores is None:
        return None

    res = np.zeros((5, len(topk)))
    for i in range(5):
        res[i] = [scores[i][item] for item in topk]
    return res


def get_new_scores_main(home_dir, input_files, get_scores):
    """
    get new scores after retrained for the given input_files
    :param home_dir: home directory where pretrained models are stored
    :param input_files: files containing the counterfactual sets
    :param get_scores: a method to get new scores
    """

    item2scores = dict()

    for file in input_files:
        print('begin file', file)
        inputs = pd.read_csv(file)
        for row in inputs.itertuples():
            idx, user_id, item_id, topk, counterfactual, predicted_scores, replacement = row[:7]
            topk = literal_eval(topk)
            if not isinstance(counterfactual, str):
                print('skip', idx, user_id, item_id, topk, counterfactual, predicted_scores, replacement)
                continue
            counterfactual = literal_eval(counterfactual)
            if isinstance(predicted_scores, str):
                predicted_scores = literal_eval(predicted_scores)
            else:
                predicted_scores = None
            assert item_id == topk[0]
            print('begin idx', idx, user_id, item_id, topk, counterfactual, predicted_scores, replacement)

            scores = get_topk_scores(idx, user_id, item_id, topk, counterfactual, predicted_scores, replacement,
                                     item2scores, home_dir, get_scores)
            if scores is None:
                print('bad scores', idx, user_id, item_id, topk, counterfactual, predicted_scores, replacement)
                continue
            assert len(scores) == 5

            for i in range(5):
                inputs.at[idx, f'actual_scores_{i}'] = str(list(scores[i]))
            s = np.mean(scores, axis=0)
            inputs.at[idx, f'actual_scores_avg'] = str(list(s))

            print('avg new scores', idx, user_id, item_id, topk, counterfactual, predicted_scores, replacement, s)

        inputs.to_csv(file, index=False)


def evaluate_files(parse_args, ks):
    args = parse_args()
    input_files = [f"{args.algo}_{k}.csv" for k in ks]

    # === SỬA: Load đúng hybrid tree ===
    current_dir = os.path.dirname(os.path.abspath(__file__))
    causal_tree_path = os.path.join(current_dir, 'causal_tree.pkl')

    if os.path.exists(causal_tree_path):
        with open(causal_tree_path, 'rb') as f:
            causal_tree = pickle.load(f)
        print(f"Loaded HYBRID causal tree: {causal_tree_path}")
    else:
        raise FileNotFoundError(f"Không tìm thấy hybrid tree: {causal_tree_path}\n"
                                "Chạy file build cây trước và đảm bảo file tên là causal_tree_hybrid.pkl")

    for file in input_files:
        print(f"\n=== Processing: {file} ===")
        data = pd.read_csv(file)

        swap = 0
        set_size = 0
        ns = 0
        total = 0
        violation_count = 0

        visited_cache = {}

        for idx, row in data.iterrows():
            try:
                user_id = int(row['user'])
                item_id = int(row['item'])
                counterfactual_str = row['counterfactual']
                actual_scores_str = row.get('actual_scores_avg')

                # Nếu file chưa có actual_scores_avg → bỏ qua (chưa retrain)
                if not isinstance(counterfactual_str, str) or not isinstance(actual_scores_str, str):
                    continue

                total += 1

                # === Parse chỉ 1 lần ===
                topk = literal_eval(row['topk'])
                counterfactual = literal_eval(counterfactual_str)
                actual_scores = literal_eval(actual_scores_str)

                assert item_id == topk[0]

                # Tính swap
                replacement = int(row['replacement'])
                replacement_rank = topk.index(replacement)
                if actual_scores[replacement_rank] > actual_scores[0]:
                    swap += 1
                    set_size += len(counterfactual)

                # Load visited (cache)
                if user_id not in visited_cache:
                    batch_size = 2048
                    path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../NCF/data'))
                    data_sets = load_movielens(path, batch=batch_size, use_recs=True)
                    u_indices = np.where(data_sets.train.x[:, 0] == user_id)[0]
                    visited_cache[user_id] = [int(data_sets.train.x[i, 1]) for i in u_indices]
                visited = visited_cache[user_id]

                # Kiểm tra causal + in chi tiết lỗi
                is_valid, violations = satisfies_causal_conditions_with_details(
                    counterfactual, causal_tree, visited, user_id, idx
                )

                if is_valid:
                    ns += 1
                else:
                    violation_count += 1
                    print(f"→ VIOLATION at row {idx} | user {user_id} | target {item_id}")
                    for item, desc in violations:
                        print(f"    Item {item} → descendant {desc} (đã xem nhưng không remove)")

            except Exception as e:
                print(f"Error at row {idx}: {e}")
                continue

        # Kết quả
        ccv = ns / total * 100 if total > 0 else 0
        print(f"\nFile: {file}")
        print(f"  Total explanations     : {total}")
        print(f"  Valid causal           : {ns} ({ccv:.2f}%)")
        print(f"  Violations             : {violation_count}")
        print(f"  Swap rate              : {swap}/{total} = {swap/total:.4f}")
        print(f"  Avg set size           : {set_size / swap if swap > 0 else 0:.2f}")
        print("=" * 70)

def satisfies_causal_conditions_with_details(counterfactual, causal_tree, visited, user_id, row_idx):
    """
    Trả về (is_valid, list_of_violations)
    violations = [(item, descendant), ...]
    """
    violations = []
    for item in counterfactual:
        if item == 0:
            continue
        descendants = find_child(causal_tree, str(item))
        if not descendants:
            continue

        for desc_str in descendants:
            desc_id = int(desc_str)
            if desc_id in visited and desc_id not in counterfactual:
                violations.append((item, desc_id))

    is_valid = len(violations) == 0
    return is_valid, violations