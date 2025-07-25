from time import time

import numpy as np

from NCF.src.helper import get_scores
from commons.accent_template import AccentTemplate

class Accent(AccentTemplate):
    @staticmethod
    def find_counterfactual_multiple_k(user, ks, model, data, args):
        """
            given a user, find an explanation for that user using ACCENT
            Args:
                user: ID of user
                ks: a list of values of k to consider (k = 5 hay 10 hay 20)
                model: the recommender model, a Tensorflow Model object

            Returns: a list explanations, each correspond to one value of k. Each explanation is a tuple consisting of:
                        - a set of items in the counterfactual explanation
                        - the originally recommended item
                        - a list of items in the original top k
                        - a list of predicted scores after the removal of the counterfactual explanation
                        - the predicted replacement item
        """
        begin = time() # đếm h
        u_indices = np.where(model.data_sets.train.x[:, 0] == user)[0] # tìm hàng các item người dùng đã tương tác ở tập train . 
        # [0] vì hàm np.where trả về tuple index thoải mãn (thay vì [1,2,3] thì nó trả về array[1,2,3]) nên phải [0]
        visited = [int(model.data_sets.train.x[i, 1]) for i in u_indices] # có hàng rồi thì tìm id ở hàng i cột 1
        assert set(visited) == model.data_sets.train.visited[user] # đảm bảo dữ liệu lấy ra đúng
        influences = np.zeros((ks[-1], len(u_indices))) # khởi tạo mảng với ks[-1] dòng và u_indice cột
        scores, topk = get_scores(user, ks[-1], model) # tính điểm score và lấy danh sách top k của user
        for i in range(ks[-1]): # chạy danh sách top k
            test_idx = user * ks[-1] + i # lấy index item thứ i của thằng user u
            assert int(model.data_sets.test.x[test_idx, 0]) == user
            assert int(model.data_sets.test.x[test_idx, 1]) == topk[i]
            # kiểm tra hợp lệ chỉ số test xem index này có thật sự là của user u và item thứ i đó có phải id của thằng top k i kh
            train_idx = model.get_train_indices_of_test_case([test_idx])
            # trả về mảng index user = user và index item = item của dòng test_idx trong tập train
            tmp, u_idx, _ = np.intersect1d(train_idx, u_indices, return_indices=True) 
            # tìm điểm giao nhau, có nghĩa là userID là u_indeces, kiếm các dòng liên quan test case mà người dùng u đã tương tác
            # tmp là chỉ số chung (là số giống nhau của 2 thằng vd 5,6), u_ind là chỉ số của mấy thằng giống nhau trong danh sách u_index vd 1, 2 ( vị tị trong ,mảng)
            #A = B giao C
            # assert A = C 
            assert np.all(tmp == u_indices)
            # kiểm tra xem temp có == u_indices không
            tmp = -model.get_influence_on_test_loss([test_idx], train_idx)
            #Tính toán ảnh hưởng của item đối với mất mát kiểm tra:
            influences[i] = tmp[u_idx]
            #tmp này chứa ảnh hưởng của cả tập(liên quan i và u), sau đó lấy thằng ảnh hưởng mà user có tương tác th, u_indx
            #túm lại là tính ảnh hưởng các item mà người dùng đã tt
            #Lưu ảnh hưởng vào ma trận ảnh hưởng (influences):

        res = None # kết quả của phản chứng
        best_repl = -1 # lưu chỉ số item thay thế tốt 1
        best_i = -1 # index của item tốt nhất
        best_gap = 1e9 # lưu chỉ số gap nhỏ nhất.

        ret = []  # lưu kết quả lần thay thế.
        for i in range(1, ks[-1]):
            print("user",user)
            tmp_res, tmp_gap = Accent.try_replace(topk[i], scores[topk[0]] - scores[topk[i]], influences[0] - influences[i],visited)
            # thử thay thế một phần tử , trả về các item cần remove và gap
            if tmp_res is not None and (
                    res is None or len(tmp_res) < len(res) or (len(tmp_res) == len(res) and tmp_gap < best_gap)):
                res, best_repl, best_i, best_gap = tmp_res, topk[i], i, tmp_gap
            # nếu có item nào để thay thế 
            # res is None: chưa có giải pháp thay thế tốt nhất -> giải pháp hiện tại oke nhất.
            #hoặc:số lượng item thay thế hiện tại bé hơn thằng tốt nhất
            # hoặc số lượng bằng nhau nhưng gap < gap tốt nhất. Thì cập nhật kết quả.
            if i + 1 == ks[len(ret)]: # sau khi kiếm hết k thằng thì kiếm thằng tốt nhất.
                if res is not None: # nếu kiếm đc thay thế hợp lệ
                    predicted_scores = np.array([scores[item] for item in topk[:(i + 1)]])# lưu điểm số các item trong top k hiện tại
                    for item in res:
                        print("res", item)
                        print("inf",influences[:(i + 1), item])
                        predicted_scores -= influences[:(i + 1), item] # chọn list các phần từ thứ 2 với độ dại từ 0 -> i + 1 vì có list k, mỗi lần chọn thằng tốt nhất trong k đó, nên chỉ cần predict score khoảng đó th.
                        #vd:predicted_scores = np.array([10, 20, 30, 40, 50, 60, 70])
                        #influences = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]]):
                        # giả sử item = 2 thì trả về np.array([2, 5, 8,11,14])
                        #predicted_scores = np.array([10-2, 20-5, 30-8, 40, 50])

                    # điểm số của các thằng top k sau khi bỏ z. 
                    print("pedicted_score",predicted_scores[0],predicted_scores[best_i],topk[i],best_i)
                    assert predicted_scores[0] < predicted_scores[best_i]
                    # sau khi trừ hết thì thằng best_i phải có ảnh hưởng , scores cao hơn thằng 0
                    assert abs(predicted_scores[0] - predicted_scores[best_i] - best_gap) < 1e-3
                    # kiểm tra sự khác biệt giữa sự thay thế (gap) có khớp với best_gap (với độ sai lệch cho phép là
                    ret.append((set(visited[idx] for idx in res), topk[0], topk[:(i + 1)], list(predicted_scores), best_repl))
                    # Nếu tất cả các kiểm tra trên đều hợp lệ, thêm kết quả vào ret (danh sách kết quả). Kết quả này là một tuple gồm:
                    # Một tập hợp các phần tử đã được thay thế trong giải thích phản chứng.
                    # Phần tử ban đầu (theo topk[0]).
                    # Danh sách các phần tử trong top-k (từ topk[:(i + 1)]).
                    # Danh sách điểm số đã được dự đoán sau khi thay thế.
                    # Phần tử thay thế tốt nhất (theo best_repl).                    

                else:
                    ret.append((None, topk[0], topk[:(i + 1)], None, -1))
                    # không có thì thêm none.

        print('counterfactual time', time() - begin)
        return ret
