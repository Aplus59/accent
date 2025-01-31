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
    
    if all_items[1][0]['value'] > a:
        return  all_items[1][0]['item'], a - all_items[1][0]['value']
    print("list_item", list_item[0])


    temp_taken_index = [[0] * (len(sum_infl) + 2) for _ in range(len(sum_infl) + 2)]

    for i in range(2, len(sum_infl) + 1):
        total = [{'value': 0, 'item': []} for _ in range(i + 2)]
        if i in all_items and 1 in all_items:
            total[0] = all_items[i][0]

        # i = 3
        # j = 1
        # 2 1
        # 1 2 
        #
        temp_taken_index[0] = [0] * (len(sum_infl) + 2)
        temp_taken_index[0][i] += 1  
        print("mex",math.floor((i) / 2),"index",i)

        range_j = max(1, math.floor((i) / 2)) + 1


        for j in range(1,range_j):
            print("go go", i - j, j)
            print("list1", list_item)
            # j =1
            if j - 1 < len(list_item):
                taken_idx = list_item[j - 1]['taken_index']
                if i - j  in all_items and taken_idx[i - j] < len(all_items[i-j]):

                    keys = all_items[i - j][taken_idx[i - j]]['item']
                    overlap_items = set(keys) & set(list_item[j - 1]['item'])

                    if not overlap_items:
                       

                        total[j]['value'] = list_item[j - 1]['value'] + all_items[i - j][taken_idx[i - j]]['value']
                        total[j]['item'] = list_item[j - 1]['item'] + all_items[i - j ][taken_idx[i - j]]['item']
                        print('not li1',list_item[j - 1]['item'],"all",all_items[i - j ][taken_idx[i - j]]['item'])

                        temp_taken_index[j] = taken_idx[:]
                        temp_taken_index[j] = temp_taken_index[j ][:]  # Sửa lỗi cập nhật danh sách tránh tham chiếu ngoài phạm vi
                        temp_taken_index[j][i - j] += 1
                    else:
                        # 4 số
                        # 1 + 3 (thu [0])
                        # 1 + 3 ( thu [6])
                        index = 0
                        while((i - j in all_items and taken_idx[i - j] + index  < len(all_items[i - j]))  and set(all_items[i - j][taken_idx[i - j] + index]['item']) & set(list_item[j - 1]['item'])):
                            index += 1
                        if(i - j in all_items and taken_idx[i - j] + index  < len(all_items[i - j])):
                            total[j]['value'] = list_item[j - 1]['value'] + all_items[i - j][taken_idx[i - j]+ index]['value']
                            total[j]['item'] = list_item[j - 1]['item'] + all_items[i - j ][taken_idx[i - j] + index]['item']
                            print('nli1',list_item[j - 1]['item'],"all",all_items[i - j ][taken_idx[i - j] + index]['item'])

                            temp_taken_index[j] = taken_idx[:]
                            temp_taken_index[j] = temp_taken_index[j ][:]  # Sửa lỗi cập nhật danh sách tránh tham chiếu ngoài phạm vi
                            temp_taken_index[j][i - j] += index

                        
            if i - j - 1 < len(list_item):       
                taken_idx = list_item[i - j - 1]['taken_index']
                if j in all_items and taken_idx[j] < len(all_items[j]) and i - j != j:
                    # j = 1 i - j =2
                    # j = 1 i - j = 2
                    # j nua i
                    # i = 3
                    # j = 1
                    # j + rang_j = 2

                    keys = all_items[j][taken_idx[j]]['item']
                    overlap_items = set(keys) & set(list_item[i - j - 1]['item'])
                    if not overlap_items:
                        total[j + range_j]['value'] = list_item[i - j - 1]['value'] + all_items[j][taken_idx[j]]['value']
                        total[j + range_j]['item'] = list_item[i - j - 1]['item'] + all_items[j][taken_idx[j]]['item']
                        print("not li2",list_item[i - j - 1]['item']," all ", all_items[j][taken_idx[j]]['item'])

                        temp_taken_index[j + range_j] = taken_idx[:]
                        temp_taken_index[j + range_j] = temp_taken_index[j * 2][:]
                        temp_taken_index[j + range_j][j] += 1
                    else:
                        index = 0
                        while((j in all_items and taken_idx[j] + index  < len(all_items[j]))  and set(all_items[j][taken_idx[j] + index]['item']) & set(list_item[i - j - 1]['item'])):
                            index += 1
                        if (j in all_items and taken_idx[j] + index  < len(all_items[j])):
                            total[j + range_j]['value'] = list_item[i - j - 1]['value'] + all_items[j][taken_idx[j]+ index]['value']
                            total[j + range_j]['item'] = list_item[i - j - 1]['item'] + all_items[j ][taken_idx[j] + index]['item']
                            print("nli2",list_item[i - j - 1]['item']," all ", all_items[j][taken_idx[j] + index]['item'])

                            temp_taken_index[j + range_j] = taken_idx[:]
                            temp_taken_index[j + range_j] = temp_taken_index[j * 2][:]  # Sửa lỗi cập nhật danh sách tránh tham chiếu ngoài phạm vi
                            temp_taken_index[j + range_j][i - j] += index
                        
                        

        filtered_totals = [(index, t) for index, t in enumerate(total) if t['value'] >= a]
        if filtered_totals:
            min_index = min(filtered_totals, key=lambda x: x[1]['value'])[0]
            print("\n dsa",a - total[min_index]['value'])
            return total[min_index]['item'], a - total[min_index]['value']

        max_index = max(enumerate(total), key=lambda x: x[1]['value'])[0]
        print("total",total[max_index] )
        print("t",total )
        total[max_index]['taken_index'] = temp_taken_index[max_index]
        list_item.append(total[max_index])

    return [], 0  # If no valid combination is found

# best 3 + [1][0]( nhan qua cua 3) -> best 3 + [1][1]
# [4,2,3]+ [2] -> [4,2,3] + [4] = 2.7 < a
# second_best3 + [1][0] > a
# [50,60],2] + [3] >= a 
# [[2,3],4]


# Sample data
# items = [([0], 0.2), ([1], 0.01), ([2], 0.02), ([3], 0.02), ([4], 0.02), ([5], 0.0012), ([6], 0.00312), ([7], 0.0126), ([8], 0.09), 
#          ([9, 31, 34], 0.01), ([10], 0.015), ([11], 0.012), ([12, 1], 0.6), ([14,50], 0.4), ([15], 0.05), ([16,17,1,0],1.6),([20,21,22,23],0.5),([24,25,26,27,28,29,30,31],1)]
# items = [([0], 0.02), ([2], 0.5), ([3], 0.5), ([4], 0.1), ([5], 0.0012), ([6], 0.00312), ([7], 0.0126), ([8], 0.09), 
#          ([9, 31, 34], 0.01), ([10], 0.015), ([50,60], 2), ([4,2,3], 2.6), ([14,50,52], 0.04), ([15], 0.05), ([16,17,1,0],0.06),([20,21,22,23],0.05),([24,25,26,27,28,29,30,31],1)]
items = [([0], 0.02), ([2], 0.5), ([3], 0.5), ([4], 0.1), ([5], 0.0012), ([6], 0.00312), ([7], 0.0126), ([8], 0.09), 
         ([9, 31, 34], 0.01), ([10], 0.015), ([50,60], 2), ([4,2,3], 2.6), ([14,50,52], 0.04), ([15], 0.05), ([16,17,1,0],0.06),([20,21,22,23],0.05),([24,25,26,27,28,29,30,31],1)]


# items = [([0], 0.02), ([2], 0.4), ([3], 0.2), ([4], 0.1), ([5], 0.0012), ([6], 0.00312), ([7], 0.0126), ([8], 0.09), 
#          ([9, 31, 34], 0.01), ([11], 0.015), ([10,11], 2.6), ([4,2,3], 2.6), ([14,50,52], 0.04), ([15], 0.05)]

# Test the function
a = min_items_greater_than_a(items, 3)
print(a)
