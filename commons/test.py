# Dữ liệu giả cho các biến visited và gap_infl
visited = [1, 2, 3, 4, 5, 6, 7, 364, 9, 60, 11, 12, 67, 14, 15, 16, 17, 18, 19, 20, 
           21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 59, 33, 34, 61, 36, 37, 
           38, 39, 40, 41, 42, 78, 44, 45, 46, 47]

# Giả sử gap_infl là một danh sách con của visited, ví dụ là những bộ phim có chỉ số lẻ
gap_infl = [idx for idx in visited if idx % 2 != 0]

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
