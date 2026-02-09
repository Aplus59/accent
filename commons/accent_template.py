import numpy as np
import math
import os
import pickle
from commons.explanation_algorithm_template import ExplanationAlgorithmTemplate
from commons.handle_causal import find_causal,find_child
from collections import defaultdict

def extract_parents(causal_tree):
    """Extract parents dict: child -> parent from anytree causal_tree."""
    parents = {}
    for node in causal_tree.descendants:
        if node.parent and node.parent.name.isdigit():  # Skip non-digit parents like '-1_hybrid'
            try:
                child_id = int(node.name)
                parent_id = int(node.parent.name)
                parents[child_id] = parent_id
            except ValueError:
                continue  # Skip if name not int
    return parents

def get_chains(visited, parents):
    """Get list of chains ([older root, child, ..., leaf newer]) from visited."""
    visited_set = set(visited)
    children_dict = defaultdict(list)
    for child in visited_set:
        parent = parents.get(child)
        if parent in visited_set:
            children_dict[parent].append(child)
    
    roots = [item for item in visited if item not in parents or parents[item] not in visited_set]
    
    chains = []
    for root in roots:
        chain = [root]
        current = root
        while children_dict[current]:
            # Assume linear chain, take first (or only) child
            next_child = children_dict[current][0]
            chain.append(next_child)
            current = next_child
        chains.append(chain)
    
    # Isolated items
    covered = set(sum(chains, []))
    for item in set(visited) - covered:
        chains.append([item])
    
    return chains

def improved_find_counterfactual_set(gap_infl, visited, causal_tree, score_gap):
    """Improved O(n^2): Chains from tree, suffixes per chain as options, grouped DP for exact min set."""
    n = len(visited)
    if n == 0:
        return [], 0
    
    parents = extract_parents(causal_tree)
    chains = get_chains(visited, parents)
    
    # Group options: per chain, list of suffix (mutual exclusive)
    group_options = []
    for chain in chains:
        options = []  # (suffix_list, v, size)
        for start_idx in range(len(chain)):
            suffix = chain[start_idx:]  # [start older, ..., newer] like [id] + children
            indices = [visited.index(item) for item in suffix]
            v = sum(gap_infl[idx] for idx in indices)
            if v > 0:
                options.append((suffix, v, len(suffix), indices))  # add indices if need
        group_options.append(options)
    
    # DP: max v for cost <=k
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
    
    # Min cost >= score_gap
    min_cost = np.inf
    for k in range(max_cost + 1):
        if dp[k] >= score_gap and k < min_cost:
            min_cost = k
    if min_cost == np.inf:
        return [], 0
    
    # Reconstruct items
    removed_items = []
    current_k = min_cost
    while current_k > 0:
        grp_idx, opt_idx, prev_k = prev[current_k]
        suffix = group_options[grp_idx][opt_idx][0]
        removed_items.extend(suffix)
        current_k = prev_k
    
    final_gap = score_gap - sum(gap_infl[visited.index(z)] for z in removed_items)
    
    return sorted(removed_items), final_gap

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
        removed_items, score_gap = improved_find_counterfactual_set(gap_infl, visited, causal_tree, score_gap)
        
        print("Score gap",score_gap)
        if score_gap < 0:
            print(f'replace {repl}: {removed_items}')
            return removed_items, score_gap
        else:
            print(f'cannot replace {repl}')
            return None, 1e9