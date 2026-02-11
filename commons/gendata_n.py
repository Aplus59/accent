import time
def are_lists_equal(list1, list2):
        return (sorted(list1) == sorted(list2) or len(list1) == len(list2))
def select_optimal_pairs(sum_infl, score_gap):
    dp = {0: (0, [])}  # Khởi tạo DP với giá trị 0
    
    for keys, value in sum_infl:
        current_dp = list(dp.items())
        for v, (count, combination) in current_dp:
            if set(keys) & set(combination):  # Tránh trùng lặp phần tử
                continue
            new_value = v + value
            new_count = count + len(keys)
            
            # Cập nhật nếu chưa có hoặc có tổ hợp ít phần tử hơn
            if new_value not in dp or new_count < dp[new_value][0]:
                dp[new_value] = (new_count, combination + keys)
            elif new_count == dp[new_value][0] and new_value > v:
                dp[new_value] = (new_count, combination + keys)
    
    # Tìm giá trị tốt nhất lớn hơn score_gap
    best_v, best_combination = None, None
    for v, (count, combination) in dp.items():
        if v > score_gap:
            if best_v is None or count < dp[best_v][0] or (count == dp[best_v][0] and v < best_v):
                best_v, best_combination = v, combination

    if best_v is None:
        return [], 0
    return best_combination, score_gap - best_v

def find_counterfactual_set(sum_infl, a):
    # Step 1: Create a dictionary to group items by weight (length of list)
    all_items = {}
    if not sum_infl:
        return [], 0
    for list_item, value in sum_infl:
        weight = len(list_item)
        if weight not in all_items:
            all_items[weight] = []
        if value > 0:
            all_items[weight].append({'item': list_item, 'value': value})

    # Sort each group by descending value
    for weight in all_items:
        all_items[weight].sort(key=lambda x: x['value'], reverse=True)


    
    list_item = [[{'item': [],'value': 0,'taken_index': [0] * (len(sum_infl) + 1)}]]  # Stores the highest odd-summed subset
    taken_index = [0] * (len(sum_infl) + 1)
    taken_index[1] = 1
    list_item.append([{'item': all_items[1][0]['item'],'value': all_items[1][0]['value'],'taken_index': taken_index}])  # Stores the highest odd-summed subset
    
    if all_items[1][0]['value'] > a:
        return  all_items[1][0]['item'], a - all_items[1][0]['value']
    
    for i in range(2, len(sum_infl) + 1):
        total = [{'value': 0, 'item': [],'taken_index':[0] * (len(sum_infl) + 1)} for _ in range(i *2)]
        for j in range(0,i):
            if j  < len(list_item) and len(list_item[j]) > 0:
                taken_idx = list_item[j][0]['taken_index']
                if i - j in all_items and taken_idx[i - j] < len(all_items[i - j]):
                    keys = all_items[i - j][taken_idx[i - j]]['item']
                    overlap_items = set(keys) & set(list_item[j][0]['item'])
                    if not overlap_items:
                        total[j]['value'] = (
                            list_item[j][0]['value'] + all_items[i - j][taken_idx[i - j]]['value']
                        )
                        total[j]['item'] = (
                            list_item[j][0]['item'] + all_items[i - j][taken_idx[i - j]]['item']
                        )
                        total[j]['taken_index'] = taken_idx[:]
                        total[j]['taken_index'][i - j] += 1

                    else:
                        index = 0
                        while (
                            i - j in all_items and taken_idx[i - j] + index < len(all_items[i - j]) and j < len(list_item)
                            and set(all_items[i - j][taken_idx[i - j] + index]['item']) & set(list_item[j][0]['item'])
                        ):
                            index += 1
                        if i - j in all_items and taken_idx[i - j] + index < len(all_items[i - j]) and j < len(list_item):
                            total[j]['value'] = (
                                list_item[j][0]['value'] + all_items[i - j][taken_idx[i - j] + index]['value']
                            )
                            total[j]['item'] = (
                                list_item[j][0]['item'] + all_items[i - j][taken_idx[i - j] + index]['item']
                            )
                            total[j]['taken_index'] = taken_idx[:]
                            total[j]['taken_index'][i - j] += index
                        m = 1
                        
                        while (
                            i - j in all_items and taken_idx[i - j] < len(all_items[i - j]) and j < len(list_item) and m < len(list_item[j])
                            and set(all_items[i - j][taken_idx[i - j]]['item']) & set(list_item[j][m]['item'])
                        ):
                            m+=1
                        if i - j in all_items and taken_idx[i - j] < len(all_items[i - j]) and j < len(list_item) and m < len(list_item[j]):
                            total[j + i]['value'] = (
                                list_item[j][m]['value'] + all_items[i - j][taken_idx[i - j]]['value']
                            )
                            total[j + i]['item'] = (
                                list_item[j][m]['item'] + all_items[i - j][taken_idx[i - j]]['item']
                            )
                            total[j + i]['taken_index'] = taken_idx[:]
                            total[j + i]['taken_index'][i - j] += 1
                            

        filtered_totals = [(index, t) for index, t in enumerate(total) if t['value'] > a]
        if filtered_totals:
            min_index = min(filtered_totals, key=lambda x: x[1]['value'])[0]
            return total[min_index]['item'], a - total[min_index]['value']

        sorted_total = sorted(
            [x for x in total if x['value'] > 0],  # Lọc phần tử có value > 0
            key=lambda x: x['value'], 
            reverse=True  # Sắp xếp giảm dần
        )
        list_item.append(sorted_total)
    return [], 0  


# Integrated new code
import numpy as np
from collections import defaultdict

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

def improved_find_counterfactual_set(gap_infl, visited, parents, score_gap):
    """Improved O(n^2): Chains from tree, suffixes per chain as options, grouped DP for exact min set."""
    n = len(visited)
    if n == 0:
        return [], 0
    
    chains = get_chains(visited, parents)
    
    # Group options: per chain, list of suffix (mutual exclusive)
    group_options = []
    for chain in chains:
        options = []  # (suffix_list, v, size, indices)
        for start_idx in range(len(chain)):
            suffix = chain[start_idx:]  # [start older, ..., newer] like [id] + children
            indices = [visited.index(item) for item in suffix]
            v = sum(gap_infl[idx] for idx in indices)
            if v > 0:
                options.append((suffix, v, len(suffix), indices))
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
    
    # Reconstruct indices
    removed_indices = []
    current_k = min_cost
    while current_k > 0:
        grp_idx, opt_idx, prev_k = prev[current_k]
        opt_indices = group_options[grp_idx][opt_idx][3]  # the indices
        removed_indices.extend(opt_indices)
        current_k = prev_k
    
    # Use unique indices
    unique_removed_indices = list(set(removed_indices))
    final_gap = score_gap - sum(gap_infl[idx] for idx in unique_removed_indices)
    
    return sorted(unique_removed_indices), final_gap

def improved_counterfactual(all_data, score_gap):
    if not all_data:
        return [], 0

    # Build chain_to_v
    chain_to_v = {tuple(chain): value for chain, value in all_data}

    # Build parents
    parents = {}
    for chain, _ in all_data:
        for i in range(len(chain) - 1):
            child = chain[i]
            parent = chain[i + 1]
            parents[child] = parent

    # Build id_to_infl
    id_to_infl = {}
    for chain, value in all_data:
        curr_chain = chain
        curr_v = value
        if len(curr_chain) > 1:
            sub_chain = tuple(curr_chain[1:])
            sub_v = chain_to_v[sub_chain]
            infl = curr_v - sub_v
        else:
            infl = curr_v
        id_to_infl[curr_chain[0]] = infl

    # Visited: sorted unique items
    visited = sorted(set(item for chain, _ in all_data for item in chain))

    # gap_infl
    gap_infl = [id_to_infl.get(id_, 0) for id_ in visited]  # 0 if not found, but should be all

    # Call improved
    removed_indices, final_gap = improved_find_counterfactual_set(gap_infl, visited, parents, score_gap)

    if final_gap < 0:
        removed_items = [visited[idx] for idx in removed_indices]
        return sorted(removed_items), final_gap
    else:
        return [], 0

import random
def generate_set(n):
    """Generate a random set of positive integers that sum up to n."""
    nums = []
    total = 0
    while total < n:
        # Randomly choose a number between 1 and the remaining sum
        num = random.randint(1, n - total)
        nums.append(num)
        total += num
    return list(nums)


import random

def generate_data(n):
    result_set = generate_set(n)

    all_items = []
    list_data = {0: []}
    used = []

    # Generate list[4] up to o items
    for i in range(len(result_set)):  # Ensure i doesn't exceed result_set length
        for _ in range(result_set[i]):
            second_item = None
            if list_data.get(i):  # Check if list_data[i] exists and is not empty
                second_item = random.choice(list_data[i])
                count = 0
                while second_item in used:
                    if count == len(list_data[i]):
                        if len(result_set) == i + 1:
                            result_set.append(1)
                        else:
                            result_set[i+1] += 1
                        break
                    second_item = random.choice(list_data[i])
                    count += 1
                if count == len(list_data[i]):
                    continue

            used.append(second_item)
            new_item = [random.randint(1,100)]
            while new_item in all_items:
                new_item = [random.randint(1,100)]

            all_items.append(new_item.copy())
            value = 0
            if second_item:
                new_item.extend(second_item[0])
                value = round(random.uniform(0, 0.005), 19) + second_item[1]
            else:
                value = round(random.uniform(0, 0.005), 19)
            if i + 1 not in list_data:
                list_data[i + 1] = []
            list_data[i + 1].append((new_item, value))  # Store as a tuple
    return list_data

import time
import random
import json
import os
import pandas as pd
import json
import csv
def write_data_to_excel(n=100, output_dir="op"):
    os.makedirs(output_dir, exist_ok=True)  # Tạo thư mục nếu chưa có
    
    records = []  # Danh sách để lưu tất cả dữ liệu trước khi ghi vào file Excel
    
    for k in range(0,n):
        
        for m in range(40):
            total = 0
            all_data = []
            n_ = random.randint(5, 10) if k < 25 else random.randint(10, 20) if 25 <= k < 50 else random.randint(20, 25)
            
            # Sinh dữ liệu
            generated_data = generate_data(n_)
            for i in range (len(generated_data)):
                for j in range(len(generated_data[i])):
                    total += generated_data[i][j][1]
                    all_data.append(generated_data[i][j])
            
            a = random.uniform(0, total * 2 / 3)
            
            # Tính toán với các phương pháp
            start_time = time.time()
            r1, r11 = find_counterfactual_set(all_data, a)
            elapsed_time_r1 = time.time() - start_time

            start_time = time.time()
            r2, r22 = select_optimal_pairs(all_data, a)
            elapsed_time_r2 = time.time() - start_time
            
            start_time = time.time()
            r3, r33 = improved_counterfactual(all_data, a)
            elapsed_time_r3 = time.time() - start_time
            
            # So sánh kết quả
            equal_r1_r2 = are_lists_equal(r1, r2)
            equal_r1_r3 = are_lists_equal(r1, r3)
            equal_r2_r3 = are_lists_equal(r2, r3)

            # Thêm dữ liệu vào danh sách
            records.append({
                "ord": k,  
                "n": n_,
                "m": m,
                "all_data":all_data ,
                "a": a,
                "find_counterfactual_set": str(r1),
                "select_optimal_pairs": str(r2),
                "improved_counterfactual": str(r3),
                "time": [
                    elapsed_time_r1, elapsed_time_r2, elapsed_time_r3
                ],
                "equal_r1_r2": "TRUE" if equal_r1_r2 else "FALSE",
                "equal_r1_r3": "TRUE" if equal_r1_r3 else "FALSE",
                "equal_r2_r3": "TRUE" if equal_r2_r3 else "FALSE",
            })
        print(f"Done k",k)
    
    # Ghi vào file Excel
    with open("all_data5.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
    
    print(f"Đã ghi dữ liệu vào")

write_data_to_excel()