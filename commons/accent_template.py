import numpy as np
from commons.explanation_algorithm_template import ExplanationAlgorithmTemplate
from commons.handle_causal import find_causal,find_child


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

        causal_list = []
        for id in visited:
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
        sorted_infl = []
        for idx_group in index_causal_list:
            if isinstance(idx_group, list):
                # Tổng ảnh hưởng trong nhóm nhân quả
                group_infl = sum(gap_infl[idx] for idx in idx_group)
                sorted_infl.append((idx_group, group_infl))
            else:
                sorted_infl.append(([idx_group], gap_infl[idx_group]))
        # Sắp xếp ưu tiên số lượng phần tử trong tuple nhỏ nhất, nếu số lượng phần tử bằng nhau, xét đến infl
        sorted_infl.sort(key=lambda x: (len(x[0]), -x[1]))
        removed_items = set()

        # Xử lý từng nhóm ảnh hưởng đã sắp xếp
        for group, group_infl in sorted_infl:
            if group_infl < 0:  # Không thể giảm chênh lệch thêm nữa
                break

            # Kiểm tra các phần tử đã tồn tại trong removed_items
            group_set = set(group)
            overlap_items = group_set & removed_items  # Các phần tử trùng lặp
            overlap_infl = sum(gap_infl[item] for item in overlap_items)  # Ảnh hưởng của các phần tử trùng lặp
            
            score_gap -= group_infl
            # Cộng lại ảnh hưởng của các phần tử trùng lặp vào score_gap
            score_gap += overlap_infl

            removed_items.update(group)  # Thêm toàn bộ nhóm vào tập loại bỏ
            # score_gap -= group_infl
            if score_gap < 0:  # Nếu thay thế đạt yêu cầu
                break
        if score_gap < 0:
            print(f'replace {repl}: {removed_items}')
            return removed_items, score_gap
        else:
            print(f'cannot replace {repl}')
            return None, 1e9
