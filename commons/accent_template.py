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

        
        sorted_infl = np.argsort(-gap_infl) # sắp xếp pt theo độ ảnh hưởng giảm dần.

        #[10,3,4]
        #[0,2,1]
        removed_items = set() # Khởi tạo một tập hợp các phần tử sẽ bị loại bỏ để thực hiện việc thay thế.

        # score_1: 100
        # score_i = 90
        # score_gap = 100 - 90 = 10 g < 0 khi đó 
        # -10
        # - 1 
        # score_i > score 1

        for idx in sorted_infl:
            if gap_infl[idx] < 0:  # cannot reduce the gap any more Vì đã xếp theo thứ tự nên nó âm là đằng sau cũng âm, nên cần dừng lại.
                break
            removed_items.add(idx)
            score_gap -= gap_infl[idx]
            if score_gap < 0:  # the replacement passed the predicted score của thằng rep đã cao hơn thằng gốc
                break
        if score_gap < 0:
            print(f'replace {repl}: {removed_items}')
            return removed_items, score_gap
        else:
            print(f'cannot replace {repl}')
            return None, 1e9
