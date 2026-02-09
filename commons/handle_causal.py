import sys
import re
from collections import defaultdict
import os
from anytree import Node, RenderTree, find
import pickle
import requests
import json

# Thiết lập lại encoding mặc định
sys.stdout.reconfigure(encoding='utf-8')

# Đường dẫn file
current_dir = os.path.dirname(os.path.abspath(__file__))
item_file_path = os.path.join(current_dir, '..', 'commons', 'u.item')
mapping_file_path = os.path.join(current_dir, 'item_mapping.csv')

# TMDB API key
TMDB_API_KEY = '047e2b1a953869fb647450e3b181628d'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

# Đọc mapping original_item → new_item
original_to_new = {}
if not os.path.exists(mapping_file_path):
    raise FileNotFoundError(f"Không tìm thấy file mapping: {mapping_file_path}.")

with open(mapping_file_path, 'r', encoding='utf-8') as f:
    next(f)  # Bỏ qua header
    for line in f:
        if line.strip():
            orig, new = line.strip().split(',')
            original_to_new[int(orig)] = int(new)

month_order = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12,
    '': 0  # cho trường hợp thiếu
}

# Hàm gọi TMDB API để lấy TMDB ID, collection_id và release_date từ title + year
def get_tmdb_info(title, year):
    search_url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        'api_key': TMDB_API_KEY,
        'query': title.split(' (')[0],
        'year': year,
        'language': 'en-US'
    }
    response = requests.get(search_url, params=params)
    if response.status_code != 200:
        print(f"Search Error for '{title} ({year})': {response.text}")
        return None, None, None
    
    results = response.json().get('results', [])
    if not results:
        return None, None, None
    
    tmdb_id = results[0]['id']
    release_date = results[0].get('release_date', '')
    
    details_url = f"{TMDB_BASE_URL}/movie/{tmdb_id}"
    params = {'api_key': TMDB_API_KEY, 'language': 'en-US'}
    response = requests.get(details_url, params=params)
    if response.status_code != 200:
        print(f"Details Error for ID {tmdb_id}: {response.text}")
        return None, None, None
    
    details = response.json()
    collection = details.get('belongs_to_collection')
    collection_id = collection.get('id') if collection else None
    
    return tmdb_id, collection_id, release_date

def build_base_tree(movies):
    # Nhóm theo base_name
    groups = defaultdict(list)
    for movie in movies:
        groups[movie['base_name']].append(movie)
    
    main_root_base = Node("-1_base")  # Root cho cây chính
    
    for base_name, group in groups.items():
        if len(group) < 2:
            continue  # Chỉ franchise (>=2)
        # Sort theo approximate release_date từ u.item
        group.sort(key=lambda x: (x['year'], month_order.get(x['month'], 0)))
        
        root = Node(str(group[0]['new_id']), parent=main_root_base)
        current_node = root
        for movie in group[1:]:
            current_node = Node(str(movie['new_id']), parent=current_node)
    
    return main_root_base

def build_tmdb_tree(movies):
    # Nhóm trực tiếp theo collection_id từ dataset
    groups = defaultdict(list)
    for movie in movies:
        if movie['collection_id']:
            groups[movie['collection_id']].append(movie)
    
    sub_root_tmdb = Node("-1_tmdb")
    
    for coll_id, group in groups.items():
        if len(group) < 2:
            continue
        # Sort theo release_date (từ movie detail, có thể approximate nếu TMDB miss)
        group.sort(key=lambda x: x['release_date'])
        
        root = Node(str(group[0]['new_id']), parent=sub_root_tmdb)
        current_node = root
        for movie in group[1:]:
            current_node = Node(str(movie['new_id']), parent=current_node)
    
    return sub_root_tmdb

def compare_trees_stats_only(main_root_base, sub_root_tmdb, movies_by_new_id):
    print("\nComparison statistics between the main tree (base_name) and the secondary tree (TMDB):")

    
    base_groups = {}
    num_base_groups = 0
    for child in main_root_base.children:
        group_ids = [child.name] + [d.name for d in child.descendants]
        base_name = movies_by_new_id[int(child.name)]['base_name']
        base_groups[base_name] = set(group_ids)
        num_base_groups += 1
    
    tmdb_groups = {}
    num_tmdb_groups = 0
    for child in sub_root_tmdb.children:
        group_ids = [child.name] + [d.name for d in child.descendants]
        coll_id = movies_by_new_id[int(child.name)]['collection_id']
        tmdb_groups[coll_id] = set(group_ids)
        num_tmdb_groups += 1
    
    # Thống kê
    num_matching = 0
    num_diff = 0
    num_base_only = 0
    num_tmdb_only = 0
    
    matched_base_names = set()
    for base_name, base_set in base_groups.items():
        coll_id = movies_by_new_id[int(next(iter(base_set)))]['collection_id']
        if coll_id in tmdb_groups:
            tmdb_set = tmdb_groups[coll_id]
            if base_set == tmdb_set:
                num_matching += 1
            else:
                num_diff += 1
            matched_base_names.add(base_name)
        else:
            num_base_only += 1
    
    for coll_id in tmdb_groups:
        # Tìm nếu có base_name tương ứng
        found = False
        for base_name in base_groups:
            if movies_by_new_id[int(next(iter(base_groups[base_name])))]['collection_id'] == coll_id:
                found = True
                break
        if not found:
            num_tmdb_only += 1
    
    print(f"Total number of groups in the main tree: {num_base_groups}")
    print(f"Total number of groups in the secondary tree: {num_tmdb_groups}")
    print(f"Number of fully matching groups: {num_matching}")
    print(f"Number of groups with differences (same coll_id but different movies): {num_diff}")
    print(f"Number of groups only in the main tree: {num_base_only}")
    print(f"Number of groups only in the secondary tree: {num_tmdb_only}")


    # Lưu các nhánh không match vào file txt (bằng tiếng Anh)
    with open('unmatched_branches.txt', 'w', encoding='utf-8') as f:
        f.write("Unmatched branches between base tree and TMDB tree:\n\n")
        
        # Groups with differences
        f.write("1. Groups with differences (same coll_id but different movies):\n")
        for base_name, base_set in base_groups.items():
            coll_id = movies_by_new_id[int(next(iter(base_set)))]['collection_id']
            if coll_id in tmdb_groups:
                tmdb_set = tmdb_groups[coll_id]
                if base_set != tmdb_set:
                    f.write(f"\nGroup '{base_name}' (coll_id: {coll_id}):\n")
                    f.write("Movies only in base tree:\n")
                    for id_str in base_set - tmdb_set:
                        mid = int(id_str)
                        movie = movies_by_new_id[mid]
                        f.write(f"  - New ID: {mid}, Old ID: {movie['original_id']}, Title: {movie['title']}, Year: {movie['year']}, Release Date: {movie['release_date']}, Collection ID: {movie['collection_id']}\n")
                    f.write("Movies only in TMDB tree:\n")
                    for id_str in tmdb_set - base_set:
                        mid = int(id_str)
                        movie = movies_by_new_id[mid]
                        f.write(f"  - New ID: {mid}, Old ID: {movie['original_id']}, Title: {movie['title']}, Year: {movie['year']}, Release Date: {movie['release_date']}, Collection ID: {movie['collection_id']}\n")
        
        # Groups only in base tree
        f.write("\n2. Groups only in base tree:\n")
        for base_name, base_set in base_groups.items():
            coll_id = movies_by_new_id[int(next(iter(base_set)))]['collection_id']
            if coll_id not in tmdb_groups:
                f.write(f"\nGroup '{base_name}' (coll_id: {coll_id if coll_id else 'None'}):\n")
                for id_str in base_set:
                    mid = int(id_str)
                    movie = movies_by_new_id[mid]
                    f.write(f"  - New ID: {mid}, Old ID: {movie['original_id']}, Title: {movie['title']}, Year: {movie['year']}, Release Date: {movie['release_date']}, Collection ID: {movie['collection_id']}\n")
        
        # Groups only in TMDB tree
        f.write("\n3. Groups only in TMDB tree:\n")
        for coll_id, tmdb_set in tmdb_groups.items():
            found = False
            for base_name in base_groups:
                if movies_by_new_id[int(next(iter(base_groups[base_name])))]['collection_id'] == coll_id:
                    found = True
                    break
            if not found:
                f.write(f"\nGroup coll_id: {coll_id}:\n")
                for id_str in tmdb_set:
                    mid = int(id_str)
                    movie = movies_by_new_id[mid]
                    f.write(f"  - New ID: {mid}, Old ID: {movie['original_id']}, Title: {movie['title']}, Year: {movie['year']}, Release Date: {movie['release_date']}, Collection ID: {movie['collection_id']}\n")

def build_hybrid_tree(main_root_base, sub_root_tmdb, movies_by_new_id):
    hybrid_root = Node("-1_hybrid")
    
    # Thêm tất cả groups từ TMDB (ưu tiên nếu có collection_id)
    for child in sub_root_tmdb.children:
        # Copy chain
        new_root = Node(child.name, parent=hybrid_root)
        current = new_root
        for desc in child.descendants:
            current = Node(desc.name, parent=current)
    
    # Thêm groups từ base_name chỉ nếu tất cả phim trong group có collection_id = None
    for child in main_root_base.children:
        group_ids = [child.name] + [d.name for d in child.descendants]
        all_none_coll = all(movies_by_new_id[int(id_str)]['collection_id'] is None for id_str in group_ids)
        if all_none_coll:
            # Copy chain
            new_root = Node(child.name, parent=hybrid_root)
            current = new_root
            for desc in child.descendants:
                current = Node(desc.name, parent=current)
    
    return hybrid_root

def find_causal():
    movies = []
    tmdb_cache = {}
    no_collection_titles = []
    movies_by_tmdb_id = {}
    movies_by_new_id = {}
    unique_collections = set()
    
    with open(item_file_path, encoding="ISO-8859-1") as file:
        for line in file:
            if not line.strip():
                continue
            parts = line.strip().split('|')
            if len(parts) < 5:
                continue
            movie_id_str = parts[0]
            title = parts[1]
            date = parts[2] if len(parts) > 2 else ""
            url = parts[4] if len(parts) > 4 else ""

            movie_id = int(movie_id_str)
            if movie_id not in original_to_new:
                continue
            new_id = original_to_new[movie_id]

            # Xử lý date
            if date:
                date_parts = date.split('-')
                if len(date_parts) == 3:
                    day, month, year = date_parts
                else:
                    day, month, year = "01", "Jan", "1900"
            else:
                day, month, year = "01", "Jan", "1900"

            # Chuẩn hóa base_name
            base_name = re.sub(r'\s*(\(\d{4}\)|\d{4})$', '', title).strip()
            base_name = re.sub(r', (The|A)$', '', base_name).strip()
            base_name = re.sub(r':.*$', '', base_name).strip()
            base_name = re.sub(r' (\d+|[IVXLCDM]+|3-D)$', '', base_name).strip()

            # Lấy TMDB info
            cache_key = f"{title}_{year}"
            if cache_key in tmdb_cache:
                tmdb_id, collection_id, release_date = tmdb_cache[cache_key]
            else:
                tmdb_id, collection_id, release_date = get_tmdb_info(title, year)
                tmdb_cache[cache_key] = (tmdb_id, collection_id, release_date)

            if not release_date:
                release_date = f"{year}-{month_order.get(month, 1):02d}-{day.zfill(2)}"

            movie_dict = {
                'original_id': movie_id,
                'new_id': new_id,
                'title': title,
                'base_name': base_name,
                'year': year,
                'month': month,
                'url': url,
                'collection_id': collection_id,
                'release_date': release_date,
                'tmdb_id': tmdb_id
            }
            movies.append(movie_dict)
            movies_by_new_id[new_id] = movie_dict
            if tmdb_id:
                movies_by_tmdb_id[tmdb_id] = movie_dict
            if collection_id:
                unique_collections.add(collection_id)
            else:
                no_collection_titles.append(title)

    # Xây cây chính từ base_name
    main_root_base = build_base_tree(movies)
    
    # Xây cây phụ từ TMDB collections (chỉ franchise)
    sub_root_tmdb = build_tmdb_tree(movies)
    
    # Thống kê so sánh và lưu unmatched vào txt
    compare_trees_stats_only(main_root_base, sub_root_tmdb, movies_by_new_id)
    
    # Build hybrid tree
    hybrid_root = build_hybrid_tree(main_root_base, sub_root_tmdb, movies_by_new_id)
    
    # Ghi thông tin franchise trong hybrid tree vào file txt (bằng tiếng Anh)
    with open('franchise_info.txt', 'w', encoding='utf-8') as f:
        f.write("Franchise information in hybrid tree:\n\n")
        group_index = 1
        for child in hybrid_root.children:
            group_ids = [child.name] + [d.name for d in child.descendants]
            coll_id = movies_by_new_id[int(child.name)]['collection_id']
            base_name = movies_by_new_id[int(child.name)]['base_name']
            f.write(f"Franchise {group_index}: Base Name = '{base_name}', Collection ID = {coll_id if coll_id else 'None'}\n")
            for id_str in group_ids:
                mid = int(id_str)
                movie = movies_by_new_id[mid]
                f.write(f"  - New ID: {mid}, Old ID: {movie['original_id']}, Title: {movie['title']}, Year: {movie['year']}, Release Date: {movie['release_date']}, Collection ID: {movie['collection_id']}\n")
            f.write("\n")
            group_index += 1
    
    # In stat hybrid
    num_hybrid_groups = len(list(hybrid_root.children))
    print(f"\nHybrid tree created with {num_hybrid_groups} groups.")
    
    # In phim không có collection_id (bằng tiếng Anh)
    print("\nMovies without collection_id:")
    if len(no_collection_titles) < 10:
        for title in no_collection_titles:
            print(f"- {title}")
    else:
        print(f"Total number: {len(no_collection_titles)}")

    return main_root_base, sub_root_tmdb, hybrid_root

def find_child(root, name):
    target_node = find(root, lambda node: node.name == name)
    if target_node:
        return [descendant.name for descendant in target_node.descendants]
    else:
        return None
    
# Load hoặc tạo mới (lưu cả ba cây)
base_tree_path = 'causal_tree_base.pkl'
tmdb_tree_path = 'causal_tree_tmdb.pkl'
hybrid_tree_path = 'causal_tree_hybrid.pkl'

if os.path.exists(base_tree_path) and os.path.exists(tmdb_tree_path) and os.path.exists(hybrid_tree_path):
    with open(base_tree_path, 'rb') as f:
        main_root_base = pickle.load(f)
    with open(tmdb_tree_path, 'rb') as f:
        sub_root_tmdb = pickle.load(f)
    with open(hybrid_tree_path, 'rb') as f:
        hybrid_root = pickle.load(f)
    print("Loaded existing trees.")
else:
    main_root_base, sub_root_tmdb, hybrid_root = find_causal()
    with open(base_tree_path, 'wb') as f:
        pickle.dump(main_root_base, f)  # Lưu cây chính (base)
    with open(tmdb_tree_path, 'wb') as f:
        pickle.dump(sub_root_tmdb, f)  # Lưu cây phụ (TMDB)
    with open(hybrid_tree_path, 'wb') as f:
        pickle.dump(hybrid_root, f)  # Lưu cây hybrid
    print("Created and saved new trees.")