import numpy as np
import math

from commons.explanation_algorithm_template import ExplanationAlgorithmTemplate
from commons.handle_causal import find_causal,find_child
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
    # Check nếu weight 1 không có item nào
    if 1 not in all_items or not all_items[1]:
        return [], 0  # hoặc continue nếu trong vòng lặp

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
        causal_tree = find_causal()
        print(f'try replace', repl, score_gap)
        print("visited",visited)
        causal_list = []
        for id in visited:
            if id == 0:
                causal_list.append(id)
            else:
                children = find_child(causal_tree,f'{id}')
                if len(children) != 0:
                    causal_list.append([id] + [int(child) for child in children if int(child) in visited])
                else:
                    causal_list.append(id)
                
        index_causal_list = []
        for item in causal_list:
            if isinstance(item, list):  # Nếu item là một danh sách con
                sub_index = [visited.index(sub_item) for sub_item in item]  # Tìm chỉ số của các phần tử con
                index_causal_list.append(sub_index)
            else:  # Nếu item là một phần tử đơn
                index_causal_list.append(visited.index(item))

        # Tính toán ảnh hưởng với cấu trúc nhân quả
        sum_infl = []
        for idx_group in index_causal_list:
            if isinstance(idx_group, list):
                # Tổng ảnh hưởng trong nhóm nhân quả
                group_infl = sum(gap_infl[idx] for idx in idx_group)
                sum_infl.append((idx_group, group_infl))
            else:
                sum_infl.append(([idx_group], gap_infl[idx_group]))

        print("list", sum_infl,"sg", score_gap)
        # Sắp xếp ưu tiên số lượng phần tử trong tuple nhỏ nhất, nếu số lượng phần tử bằng nhau, xét đến infl
        removed_items, score_gap = find_counterfactual_set(sum_infl, score_gap)
        print("Score gap",score_gap)
        if score_gap < 0:
            print(f'replace {repl}: {removed_items}')
            return removed_items, score_gap
        else:
            print(f'cannot replace {repl}')
            return None, 1e9