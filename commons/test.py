# Dữ liệu giả cho các biến visited và gap_infl
visited = [1, 2, 3, 4, 5, 6, 7, 364, 9, 60, 11, 12, 67, 14, 15, 16, 17, 18, 19, 20, 
           21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 59, 33, 34, 61, 36, 37, 
           38, 39, 40, 41, 42, 78, 44, 45, 46, 47]

# Giả sử gap_infl là một danh sách con của visited, ví dụ là những bộ phim có chỉ số lẻ
gap_infl = [12, 2, 35, 4, 52, 16, 27, 4, 9, 6, 15, 12, 7, 14, 15, 6, 27, 8, 19, 20, 
           2, 1, 7, 60, 45, 26, 27, 2, 29, 33, 13, 59, 13, 3, 61, 36, 37, 
           18, 39, 40, 5, 42, 78, 44, 48, 46, 47]

score_gap = 100  # Giả sử chênh lệch điểm số ban đầu

# Đoạn mã tiếp theo bạn có thể chạy sau khi đã tạo dữ liệu giả
from handle_causal import find_causal, find_child
from anytree import Node, RenderTree, find

causal_tree = find_causal()

# for pre, fill, node in RenderTree(causal_tree):
#         print(f"{pre}{node.name}")

print("list",visited)
causal_list = []
for id in visited:
    children = find_child(causal_tree,f'{id}')
    if len(children) != 0:
        print(children)
        causal_list.append([id] + [int(child) for child in children if int(child) in visited])
        print('causal _in',causal_list)
    else:
        causal_list.append(id)
print('causal',causal_list)

index_causal_list = []
for item in causal_list:
    if isinstance(item, list):  # Nếu item là một danh sách con
        sub_index = [visited.index(sub_item) for sub_item in item]  # Tìm chỉ số của các phần tử con
        index_causal_list.append(sub_index)
    else:  # Nếu item là một phần tử đơn
        index_causal_list.append(visited.index(item))
print('index',index_causal_list)

# Kết quả sẽ có index_causal_list chứa các chỉ số của causal_list trong visited

# Tính toán ảnh hưởng với cấu trúc nhân quả
sorted_infl = []
for idx_group in index_causal_list:
    if isinstance(idx_group, list):
        # Tổng ảnh hưởng trong nhóm nhân quả
        group_infl = sum(gap_infl[idx] for idx in idx_group)
        sorted_infl.append((idx_group, group_infl))
    else:
        sorted_infl.append(([idx_group], gap_infl[idx_group]))

print('sorted_infl',sorted_infl)

# Sắp xếp ưu tiên số lượng phần tử trong tuple nhỏ nhất, nếu số lượng phần tử bằng nhau, xét đến infl
sorted_infl.sort(key=lambda x: (len(x[0]), -x[1]))


print('sorted_infl',sorted_infl)
removed_items = set()

# Xử lý từng nhóm ảnh hưởng đã sắp xếp
for group, group_infl in sorted_infl:
    if group_infl < 0:  # Không thể giảm chênh lệch thêm nữa
        break
    removed_items.update(group)  # Thêm toàn bộ nhóm vào tập loại bỏ
    score_gap -= group_infl
    if score_gap < 0:  # Nếu thay thế đạt yêu cầu
        break

if score_gap < 0:
    print(f'Replace: {removed_items}')
else:
    print(f'Cannot replace')