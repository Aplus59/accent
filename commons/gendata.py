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


def find_counterfactual_set_old_ver(sum_infl, a):
    # Step 1: Create a dictionary to group items by weight (length of list)
    all_items = {}
    for list_item, value in sum_infl:
        weight = len(list_item)
        if weight not in all_items:
            all_items[weight] = []
        if value > 0:
            all_items[weight].append({'item': list_item, 'value': value})

    # Sort each group by descending value
    for weight in all_items:
        all_items[weight].sort(key=lambda x: x['value'], reverse=True)

    list_item = [{'item': [],'value': 0,'taken_index': [0] * (len(sum_infl) + 1)}]  # Stores the highest odd-summed subset
    taken_index = [0] * (len(all_items) + 1)
    taken_index[1] = 1
    list_item.append({'item': all_items[1][0]['item'],'value': all_items[1][0]['value'],'taken_index': taken_index})  # Stores the highest odd-summed subset
    
    if all_items[1][0]['value'] > a:
        return  all_items[1][0]['item'], a - all_items[1][0]['value']
    
    for i in range(2, len(sum_infl) + 1):
        total = [{'value': 0, 'item': [],'taken_index':[0] * (len(sum_infl) + 1)} for _ in range(i *2)]
        for j in range(0,i):
            if j  < len(list_item) :
                taken_idx = list_item[j]['taken_index']
                if i - j in all_items and taken_idx[i - j] < len(all_items[i - j]):
                    keys = all_items[i - j][taken_idx[i - j]]['item']
                    overlap_items = set(keys) & set(list_item[j]['item'])
                    if not overlap_items:
                        total[j]['value'] = (
                            list_item[j]['value'] + all_items[i - j][taken_idx[i - j]]['value']
                        )
                        total[j]['item'] = (
                            list_item[j]['item'] + all_items[i - j][taken_idx[i - j]]['item']
                        )
                        total[j]['taken_index'] = taken_idx[:]
                        total[j]['taken_index'][i - j] += 1

                    else:
                        index = 0
                        while (
                            i - j in all_items and taken_idx[i - j] + index < len(all_items[i - j])
                            and set(all_items[i - j][taken_idx[i - j] + index]['item']) & set(list_item[j]['item'])
                        ):
                            index += 1
                        if i - j in all_items and taken_idx[i - j] + index < len(all_items[i - j]):
                            total[j]['value'] = (
                                list_item[j]['value'] + all_items[i - j][taken_idx[i - j] + index]['value']
                            )
                            total[j]['item'] = (
                                list_item[j]['item'] + all_items[i - j][taken_idx[i - j] + index]['item']
                            )
                            total[j]['taken_index'] = taken_idx[:]
                            total[j]['taken_index'][i - j] += index
                            
        filtered_totals = [(index, t) for index, t in enumerate(total) if t['value'] > a]
        if filtered_totals:
            min_index = min(filtered_totals, key=lambda x: x[1]['value'])[0]
            return total[min_index]['item'], a - total[min_index]['value']

        max_item = max(
            (x for x in total if x['value'] > 0),
            key=lambda x: x['value'],
            default=None 
        )

        if max_item is not None:
            list_item.append(max_item)

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
def write_data_to_excel(n=75, output_dir="op"):
    os.makedirs(output_dir, exist_ok=True)  # Tạo thư mục nếu chưa có
    for o in range(12,15):
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
                
                # So sánh kết quả
                equal_r1_r2 = are_lists_equal(r1, r2)

                # Thêm dữ liệu vào danh sách
                records.append({
                    "ord": k,  
                    "n": n_,
                    "m": m,
                    "all_data":all_data ,
                    "a": a,
                    "find_counterfactual_set": str(r1),
                    "select_optimal_pairs": str(r2),
                    "time": [
                        elapsed_time_r1,elapsed_time_r2
                    ],
                    "equal_r1_r2": "TRUE" if equal_r1_r2 else "FALSE",
                })
            print(f"Done k",k)
        
        # Ghi vào file Excel
        with open(f'all_data{o}.csv', "w", newline="", encoding="utf-8") as file:
            fieldnames = [
                "file", "n", "m", "a", 
                "find_counterfactual_set", "select_optimal_pairs",
                "time", "equal_r1_r2"
            ]
            writer = csv.DictWriter(file, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)
        
        print(f"Đã ghi dữ liệu vào")

write_data_to_excel()