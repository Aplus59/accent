from itertools import combinations
import math

def min_items_greater_than_a(sum_infl, a):
    # Step 1: Create a dictionary to group items by weight (length of list)
    all_items = {}
    for list_item, value in sum_infl:
        weight = len(list_item)
        if weight not in all_items:
            all_items[weight] = []
        all_items[weight].append({'item': list_item, 'value': value})

    # Sort each group by descending value
    for weight in all_items:
        all_items[weight].sort(key=lambda x: x['value'], reverse=True)

    print("w", all_items)

    taken_index = [0] * len(sum_infl)
    taken_index[1] = 1

    list_item = [{'item': all_items[1][0]['item'],'value': all_items[1][0]['value'],'taken_index': taken_index}]  # Stores the highest odd-summed subset
    
    if all_items[1][0]['value'] >= a:
        return  all_items[1][0]['item'], a - all_items[1][0]['value']
    print("list_item", list_item[0])


    for i in range(2, len(sum_infl) + 1):
        total = [{'value': 0, 'item': [],'taken_index':[0] * (len(sum_infl) + 2)} for _ in range(i + 2)]
        if i in all_items and 1 in all_items:
            total[0]['value'] = all_items[i][0]['value']
            total[0]['item'] = all_items[i][0]['item']
            total[0]['taken_index'][i] += 1
        print("half j",math.floor((i) / 2),"index",i)

        range_j = max(1, math.floor((i) / 2)) + 1


        for j in range(1,range_j):
            print("go go", i - j, j)
            print("list_item", list_item)
            for offset, index_offset in [(i - j, j - 1), (j, i - j - 1)]:
                if index_offset < len(list_item):
                    taken_idx = list_item[index_offset]['taken_index']
                    if offset in all_items and taken_idx[offset] < len(all_items[offset]) :
                        keys = all_items[offset][taken_idx[offset]]['item']
                        overlap_items = set(keys) & set(list_item[index_offset]['item'])

                        if not overlap_items:
                            total[j + (0 if offset == i - j else range_j)]['value'] = (
                                list_item[index_offset]['value'] + all_items[offset][taken_idx[offset]]['value']
                            )
                            total[j + (0 if offset == i - j else range_j)]['item'] = (
                                list_item[index_offset]['item'] + all_items[offset][taken_idx[offset]]['item']
                            )
                            total[j + (0 if offset == i - j else range_j)]['taken_index'] = taken_idx[:]
                            total[j + (0 if offset == i - j else range_j)]['taken_index'][offset] += 1
                            print("not_overlap_list_item", list_item[index_offset]['item'], "all", all_items[offset][taken_idx[offset]]['item'])

                        else:
                            index = 0
                            while (
                                offset in all_items and taken_idx[offset] + index < len(all_items[offset])
                                and set(all_items[offset][taken_idx[offset] + index]['item']) & set(list_item[index_offset]['item'])
                            ):
                                index += 1

                            if offset in all_items and taken_idx[offset] + index < len(all_items[offset]):
                                total[j + (0 if offset == i - j else range_j)]['value'] = (
                                    list_item[index_offset]['value'] + all_items[offset][taken_idx[offset] + index]['value']
                                )
                                total[j + (0 if offset == i - j else range_j)]['item'] = (
                                    list_item[index_offset]['item'] + all_items[offset][taken_idx[offset] + index]['item']
                                )
                                total[j + (0 if offset == i - j else range_j)]['taken_index'] = taken_idx[:]
                                total[j + (0 if offset == i - j else range_j)]['taken_index'][offset] += index
                                print("overlap_list_item", list_item[index_offset]['item'], "all", all_items[offset][taken_idx[offset] + index]['item'])

        filtered_totals = [(index, t) for index, t in enumerate(total) if t['value'] >= a]
        if filtered_totals:
            min_index = min(filtered_totals, key=lambda x: x[1]['value'])[0]
            return total[min_index]['item'], a - total[min_index]['value']

        max_index = max(enumerate(total), key=lambda x: x[1]['value'])[0]
        print("total",total[max_index] )
        list_item.append(total[max_index])

    return [], 0  


# Sample data
# items = [([0], 0.2), ([1], 0.01), ([2], 0.02), ([3], 0.02), ([4], 0.02), ([5], 0.0012), ([6], 0.00312), ([7], 0.0126), ([8], 0.09), 
#          ([9, 31, 34], 0.01), ([10], 0.015), ([11], 0.012), ([12, 1], 0.6), ([14,50], 0.4), ([15], 0.05), ([16,17,1,0],1.6),([20,21,22,23],0.5),([24,25,26,27,28,29,30,31],1)]
# items = [([0], 0.05), ([2,3], 0.5), ([3], 0.6), ([4], 0.1), ([5], 0.0012), ([6], 0.00312), ([7], 0.0126), ([8], 0.09), 
#          ([9, 31, 34], 0.01), ([10], 0.015), ([50,60], 0.3), ([77,2,3], 0.1), ([14,50,52], 0.04), ([15], 0.05), ([16,17,1,0],0.06),([20,21,22,23],0.05),([24,25,26,27,28,29,30,31],1)]

# best i = 4
# best i = 5
#[4,2,3] causal [2,3] causal [3]
# ([4,2,3], 2.6)
# ([50,60], 2) ([3], 0.5)

# items = [([0], 0.02), ([2,3], 0.5), ([3], 0.5), ([11], 0.5), ([5], 0.0012), ([6], 0.00312), ([7], 0.0126), ([8], 0.09), 
#          ([9, 31, 34], 0.01), ([10], 0.015), ([50,60], 2), ([4,2,3], 2.6), ([14,50,52], 0.04), ([15], 0.05), ([16,17,1,0],0.06),([20,21,22,23],0.05),([24,25,26,27,28,29,30,31],1)]


items = [([0], 0.02), ([2], 0.4), ([3], 0.2), ([4], 0.1), ([5], 0.0012), ([6], 0.00312), ([7], 0.0126), ([8], 0.09), 
         ([9, 31, 34], 0.01), ([11], 0.015), ([10,11], 0.1), ([4,2,3], 0.1), ([14,50,52], 0.04), ([15], 0.05)]

# Test the function
a = min_items_greater_than_a(items, 1)
print(a)
