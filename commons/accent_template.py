import numpy as np
import math
import os
import pickle
from commons.explanation_algorithm_template import ExplanationAlgorithmTemplate
from commons.handle_causal import find_causal,find_child
from collections import defaultdict
from anytree import find

def get_global_chains(root):
    """Trả về tất cả các chain đầy đủ trong toàn bộ cây (mỗi franchise là 1 chain tuyến tính)."""
    chains = []
    for franchise_root in root.children:          # mỗi child của -1_hybrid là root của 1 franchise
        chain = []
        current = franchise_root
        while current and current.name.isdigit():
            chain.append(int(current.name))
            if current.children:
                current = current.children[0]     # chỉ có 1 con
            else:
                break
        if chain:
            chains.append(chain)
    return chains


def improved_find_counterfactual_set(gap_infl, visited, causal_tree, score_gap):
    """
    Sửa hoàn toàn: dùng full global chain + project lên visited items.
    Đảm bảo: nếu remove item cũ → phải remove hết tất cả descendant đã xem (không còn gap).
    """
    n = len(visited)
    if n == 0:
        return [], 0

    visited_set = set(visited)
    visited_idx = {item: i for i, item in enumerate(visited)}   # item -> index trong visited

    # 1. Lấy tất cả chain toàn cục
    global_chains = get_global_chains(causal_tree)

    # 2. Với mỗi global chain, lấy phần đã xem (theo thứ tự cũ → mới)
    group_options = []          # mỗi group = 1 franchise có phim đã xem
    for gchain in global_chains:
        watched = [item for item in gchain if item in visited_set]
        if len(watched) < 1:
            continue

        options = []
        for start in range(len(watched)):
            suffix = watched[start:]                     # suffix của các phim đã xem
            indices = [visited_idx[item] for item in suffix]
            v = sum(gap_infl[i] for i in indices)
            if v > 0:
                options.append((suffix, v, len(suffix), indices))

        if options:
            group_options.append(options)

    # 3. DP giống cũ: chọn đúng 1 option mỗi group (mutually exclusive suffixes)
    max_cost = n
    dp = [-np.inf] * (max_cost + 1)
    dp[0] = 0.0
    prev = [None] * (max_cost + 1)

    for grp_idx, options in enumerate(group_options):
        temp_dp = dp[:]
        temp_prev = prev[:]
        for opt_idx, (suffix, v, c, _) in enumerate(options):
            for k in range(max_cost, c - 1, -1):
                new_v = dp[k - c] + v
                if new_v > temp_dp[k]:
                    temp_dp[k] = new_v
                    temp_prev[k] = (grp_idx, opt_idx, k - c)
        dp = temp_dp
        prev = temp_prev

    # Tìm min cost đủ score_gap
    min_cost = np.inf
    for k in range(max_cost + 1):
        if dp[k] >= score_gap and k < min_cost:
            min_cost = k
    if min_cost == np.inf:
        return [], 0

    # Reconstruct
    removed_indices = []
    current_k = min_cost
    while current_k > 0:
        grp_idx, opt_idx, prev_k = prev[current_k]
        indices = group_options[grp_idx][opt_idx][3]
        removed_indices.extend(indices)
        current_k = prev_k

    unique_removed_indices = sorted(set(removed_indices))
    final_gap = score_gap - sum(gap_infl[idx] for idx in unique_removed_indices)

    return unique_removed_indices, final_gap

class AccentTemplate(ExplanationAlgorithmTemplate):
    @staticmethod
    
    def try_replace(repl, score_gap, gap_infl,visited):
        """
        given a replacement item, try to swap the replacement and the recommendation
        Args:
            repl: the replacement item
            score_gap: the current score gap between repl and the recommendation
            gap_infl: a list of items and their influence on the score gap

        Returns: if possible, return the set of items that must be removed to swap and the new score gap
                else, None, 1e9
        """
        print(f'handle causal_tree')
        current_dir = os.path.dirname(os.path.abspath(__file__))
        causal_tree_path = os.path.join(current_dir, 'causal_tree.pkl')
        if os.path.exists(causal_tree_path):
            with open(causal_tree_path, 'rb') as f:
                causal_tree = pickle.load(f)
        else:
            raise FileNotFoundError(f"Causal tree file not found: {causal_tree_path}. Please run handle_causal.py first.")

        print(f'try replace', repl, score_gap)
        
        # Thay bằng improved (no need causal_list, sum_infl)
        removed_indices, score_gap = improved_find_counterfactual_set(gap_infl, visited, causal_tree, score_gap)
        
        print("Score gap",score_gap)
        if score_gap < 0:
            removed_items = [visited[idx] for idx in removed_indices]
            print(f'replace {repl}: {removed_items}')
            return removed_indices, score_gap
        else:
            print(f'cannot replace {repl}')
            return None, 1e9