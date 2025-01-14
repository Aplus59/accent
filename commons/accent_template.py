from commons.explanation_algorithm_template import ExplanationAlgorithmTemplate


class AccentTemplate(ExplanationAlgorithmTemplate):
    @staticmethod
    def try_replace(repl, score_gap, gap_infl):
        """
        given a replacement item, try to swap the replacement and the recommendation
        Args:
            repl: the replacement item
            score_gap: the current score gap between repl and the recommendation
            gap_infl: a list of items and their influence on the score gap

        Returns: if possible, return the set of items that must be removed to swap and the new score gap
                else, None, 1e9
        """
        print(f'try replace', repl, score_gap)
        sorted_infl = np.argsort(-gap_infl) # sắp xếp pt theo độ ảnh hưởng giảm dần.

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
