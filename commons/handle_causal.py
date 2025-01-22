import sys
import re
from collections import defaultdict
from anytree import Node, RenderTree, find
# Thiết lập lại encoding mặc định
sys.stdout.reconfigure(encoding='utf-8')

# Đọc dữ liệu từ tệp
file_path = 'commons/u.item'
movies = []

def find_causal():
    with open(file_path, encoding="ISO-8859-1") as file:
        for line in file:
            parts = line.strip().split('|')  # Tách dòng theo ký tự |
            movie_id, title, date, _, url = parts[:5]  # Lấy các trường cần thiết
            if date:  # Kiểm tra nếu có ngày hợp lệ
                day, month, year = date.split('-')
            else:
                day, month, year = "01", "Jan", "1900"  # Gán giá trị mặc định nếu thiếu ngày
            
            # Chuẩn hóa tên cơ sở
            base_name = re.sub(r'\s*(\(\d{4}\)|\d{4})$', '', title).strip()
            base_name = re.sub(r', (The|A)$', '', base_name).strip()
            base_name = base_name.split(':')[0]
            base_name = re.sub(r' (\d+|[IVXLCDM]+|3-D)$', '', base_name).strip()
            
            # Thêm phim vào danh sách
            movies.append({'id': movie_id, 'title': title, 'base_name': base_name, 'year': year, 'month': month, 'url': url})

    # Nhóm phim theo base_name
    groups = defaultdict(list)
    for movie in movies:
        groups[movie['base_name']].append(movie)

    # Tạo root chung
    main_root = Node("0")  # Root chung có số là 0

    # Sắp xếp và tạo cây
    for base_name, group in groups.items():
        # Sắp xếp theo năm, nếu bằng thì theo tháng
        group.sort(key=lambda x: (x['year'], x['month']))
        root = Node(f"{group[0]['id']}", parent=main_root)  # Gán root của cây con là con của main_root
        current_node = root
        for movie in group[1:]:
            current_node = Node(f"{movie['id']}", parent=current_node)
        
        # print(f"Tree for {base_name}:")
        # for pre, fill, node in RenderTree(root):
        #     print(f"{pre}{node.name}")
        # print("\n")
    

    #Hiển thị toàn bộ cây với root chung
    # print("Main Tree:")
    # for pre, fill, node in RenderTree(main_root):
    #     print(f"{pre}{node.name}")
    # print("\n")

    # # Tìm kiếm node trong cây
    # target_node = find(main_root, lambda node: node.name == "234")

    # # Kiểm tra và lấy các nút con của nó
    # if target_node:
    #     print(f"Found node: {target_node.name}")
    #     print("Children and Descendants:")
    #     for descendant in target_node.descendants:  # Trả về tất cả các node con, kể cả các cấp sâu hơn
    #         print(descendant.name)
    # else:
    #     print("Node not found.")

    return main_root
def find_child(main_root,name):
    target_node = find(main_root, lambda node: node.name == name)

# Kiểm tra và lưu các nút con của nó
    if target_node:
        descendants_list = [descendant.name for descendant in target_node.descendants]  # Lưu tên các node con vào danh sách
        return descendants_list
    else:
        print("Node not found.")
        return None
    
# causal_tree = find_causal()