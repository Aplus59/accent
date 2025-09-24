import sys
import re
from collections import defaultdict
import os
from anytree import Node, RenderTree, find
import pickle

# Thiết lập lại encoding mặc định
sys.stdout.reconfigure(encoding='utf-8')

# Đọc dữ liệu từ tệp
current_dir = os.path.dirname(os.path.abspath(__file__))  
file_path = os.path.join(current_dir, 'movies.tsv')

def find_causal():
    movies = []
    with open(file_path, encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split("\t")
            if len(parts) < 3:
                continue
            movie_id, title, genres = parts[:3]

            # Tách năm từ title (ví dụ: "Toy Story (1995)")
            year_match = re.search(r'\((\d{4})\)', title)
            year = year_match.group(1) if year_match else "1900"

            # Chuẩn hóa base_name
            base_name = re.sub(r'\s*\(\d{4}\)$', '', title).strip()
            base_name = re.sub(r', (The|A)$', '', base_name).strip()
            base_name = base_name.split(':')[0]
            base_name = re.sub(r' (\d+|[IVXLCDM]+|3-D)$', '', base_name).strip()

            # Thêm phim vào danh sách
            movies.append({
                'id': movie_id,
                'title': title,
                'base_name': base_name,
                'year': year,
                'genres': genres
            })

    # Nhóm phim theo base_name
    groups = defaultdict(list)
    for movie in movies:
        groups[movie['base_name']].append(movie)

    # Root chung
    main_root = Node("0")

    # Tạo cây
    for base_name, group in groups.items():
        group.sort(key=lambda x: int(x['year']))
        root = Node(f"{group[0]['id']}", parent=main_root)
        current_node = root
        for movie in group[1:]:
            current_node = Node(f"{movie['id']}", parent=current_node)

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
    
def print_causal_tree(root):
    """
    In toàn bộ causal tree ra màn hình với cấu trúc phân cấp.
    """
    for pre, fill, node in RenderTree(root):
        print(f"{pre}{node.name}")


causal_tree_path = 'causal_tree.pkl'
if os.path.exists(causal_tree_path):
    with open(causal_tree_path, 'rb') as f:
        causal_tree = pickle.load(f)
else:
    causal_tree = find_causal()
    with open(causal_tree_path, 'wb') as f:
        pickle.dump(causal_tree, f)

print_causal_tree(causal_tree)
