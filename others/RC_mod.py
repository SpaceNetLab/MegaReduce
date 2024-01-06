import time

from utils import *
from Topo import *
import multiprocessing
from datetime import datetime
import os
from itertools import starmap


# 增加了一个输入哦！
def run_for_one_time_slot(para_tuple):
    constellation = para_tuple[0]
    g_path = para_tuple[1]
    lambda_ratio = para_tuple[2]
    t = para_tuple[3]
    cp_dict = para_tuple[4]
    k_threshold = para_tuple[5]
    capa_threshold = para_tuple[6]
    con_name = constellation["name"]
    in_t = IntegratedNetwork(constellation["info"], g_path, t)
    cp_list = list(cp_dict.keys())
    pairs_list = generate_pairs_combination(cp_list)  # 12*11/2 = 66 对
    if t != 0:
        time.sleep(1)
    directory = "./Research_{}/PathValue{}".format(con_name, lambda_ratio)  #
    if not os.path.exists(directory):
        os.makedirs(directory)
    path_file = open(directory + "/" + "path_value_{}.txt".format(t), "a")

    score = [0, 0]  # score会作为返回值，作为对于一个时间片的评价,第一个元素表示有几条不相交的路径，第二个元素表示一个通信对头上的卫星数量
    unreach_num = 0
    for pair in pairs_list:
        src = pair[0]
        dst = pair[1]
        final_topo, k_max = in_t.fin_topo(src, dst, cp_dict)
        k_max = int(k_max)
        if k_max == 0:
            unreach_num += 1
            continue
        score[1] += k_max
        best_value = 0
        edges = get_edges(final_topo, in_t)
        final_lst = np.zeros(len(edges), dtype=int)

        for k in range(1, k_max + 1):  #
            value, time_solve, ret_list = find_k_disjoint_ways_dj(final_topo, edges, in_t)
            if k == 1:
                best_value = value

            if value > best_value * lambda_ratio:
                ret_tuple = (src, dst, k, value, time_solve)
                path_file.write(str(ret_tuple) + "\n")
                score[0] += (k - 1)
                find_used_link(edges, final_lst, src, dst, t, lambda_ratio, con_name)
                break
            else:
                ret_tuple = (src, dst, k, value, time_solve)
                path_file.write(str(ret_tuple) + "\n")
                final_lst = final_lst + ret_list
                if k == k_threshold:  # 为了节约时间，如果已经找到了k_threshold 条路径 ，那么就也不要算当前通讯对了
                    if best_value < 1:
                        unreach_num += 1
                    else:
                        score[0] += k
                    find_used_link(edges, final_lst, src, dst, t, lambda_ratio, con_name)
                    break

    path_file.close()
    # 计算当前时间片的满足率
    print(t,unreach_num)
    score[0] = 1 - (unreach_num / 66)  # 这个绝对是不能超过1
    score[1] = score[1] / (len(pairs_list) * capa_threshold)  # 这个在容量要求不是很大的时候是可以大于1的
    return score


def con_feasibility_check(con, gw_path, lr, cp_dict, k_threshold, c_threshold):
    time_list = [600 * i for i in range(0, 10)]  # 这里是多少自己定
    para_list = []  # 长度为100
    for slot in time_list:
        para_list.append((con, gw_path, lr, slot, cp_dict, k_threshold, c_threshold))

    pool = multiprocessing.Pool()

    return_values = pool.map(run_for_one_time_slot, para_list)  # 这里产生了100个时间片的结果

    pool.close()
    pool.join()

    aver_k_satisfied = 0
    aver_c_satisfied = 0
    for item in return_values:
        aver_k_satisfied += item[0]
        aver_c_satisfied += item[1]

    aver_k_satisfied /= len(return_values)
    aver_c_satisfied /= len(return_values)

    return aver_k_satisfied, aver_c_satisfied


def check_and_modify(constellation, k_satis, c_satis):
    if k_satis >= 0.95 and c_satis >= 0.95:  # 认为是一个合格的星座
        if k_satis > c_satis:  # k（可靠性）更加满足要求 则进行对k影响较大的缩减方式
            new_con = shrink_k(constellation)
        else:  # c（容量）更加满足要求 则进行对c影响较大的缩减方式
            new_con = shrink_c(constellation)
        return True, new_con
    else:  # 认为是一个不合格的星座
        if k_satis < c_satis:  # k（可靠性）更加不符合要求 则进行对k影响较大的扩容方式
            new_con = expand_k(constellation)
        else:  # c（容量）更加不符合要求 则进行对c影响较大的扩容方式
            new_con = expand_c(constellation)
        return False, new_con


# def shrink_k(con):
#     shrink_con = dict()
#     shrink_con["name"] = "shrink_k"
#     old_list = con["info"]
#     new_list = []
#     for shell_index in range(len(old_list)):
#         if shell_index == 0 or shell_index == 1:
#             new_tuple = (
#                 old_list[shell_index][0], old_list[shell_index][1], old_list[shell_index][2],
#                 old_list[shell_index][3] - 2,
#                 old_list[shell_index][4] - 4)
#             new_list.append(new_tuple)
#         else:
#             new_tuple = (
#                 old_list[shell_index][0], old_list[shell_index][1], old_list[shell_index][2],
#                 old_list[shell_index][3],
#                 old_list[shell_index][4] - 4)
#             new_list.append(new_tuple)
#     shrink_con["info"] = new_list
#     return shrink_con
#
#
# def expand_k(con):
#     expand_con = dict()
#     expand_con["name"] = "expand_k"
#     old_list = con["info"]
#     new_list = []
#     for shell_index in range(len(old_list)):
#         if shell_index == 0 or shell_index == 1:
#             new_tuple = (
#                 old_list[shell_index][0], old_list[shell_index][1], old_list[shell_index][2],
#                 old_list[shell_index][3] + 1,
#                 old_list[shell_index][4] + 2)
#             new_list.append(new_tuple)
#         else:
#             new_tuple = (
#                 old_list[shell_index][0], old_list[shell_index][1], old_list[shell_index][2],
#                 old_list[shell_index][3],
#                 old_list[shell_index][4] + 2)
#             new_list.append(new_tuple)
#     expand_con["info"] = new_list
#     return expand_con
#
#
# def shrink_c(con):
#     shrink_con = dict()
#     shrink_con["name"] = "shrink_c"
#     old_list = con["info"]
#     new_list = []
#     for shell_index in range(len(old_list)):
#         if shell_index == 0 or shell_index == 1:
#             new_tuple = (
#                 old_list[shell_index][0], old_list[shell_index][1], old_list[shell_index][2],
#                 old_list[shell_index][3] - 4,
#                 old_list[shell_index][4] - 2)
#             new_list.append(new_tuple)
#         else:
#             new_tuple = (
#                 old_list[shell_index][0], old_list[shell_index][1], old_list[shell_index][2],
#                 old_list[shell_index][3] - 1,
#                 old_list[shell_index][4] - 4)
#             new_list.append(new_tuple)
#     shrink_con["info"] = new_list
#     return shrink_con
#
#
# def expand_c(con):
#     expand_con = dict()
#     expand_con["name"] = "expand_c"
#     old_list = con["info"]
#     new_list = []
#     for shell_index in range(len(old_list)):
#         if shell_index == 0 or shell_index == 1:
#             new_tuple = (
#                 old_list[shell_index][0], old_list[shell_index][1], old_list[shell_index][2],
#                 old_list[shell_index][3] + 2,
#                 old_list[shell_index][4] + 1)
#             new_list.append(new_tuple)
#         else:
#             new_tuple = (
#                 old_list[shell_index][0], old_list[shell_index][1], old_list[shell_index][2],
#                 old_list[shell_index][3],
#                 old_list[shell_index][4] + 2)
#             new_list.append(new_tuple)
#
#     expand_con["info"] = new_list
#     return expand_con


def shrink_k(con):
    shrink_con = dict()
    shrink_con["name"] = "shrink_k"
    old_list = con["info"]
    new_list = []
    for shell_index in range(len(old_list)):
        new_tuple = (
            old_list[shell_index][0], old_list[shell_index][1], old_list[shell_index][2],
            old_list[shell_index][3] - 2,
            old_list[shell_index][4] - 4)
        new_list.append(new_tuple)
    shrink_con["info"] = new_list
    return shrink_con


def expand_k(con):
    expand_con = dict()
    expand_con["name"] = "expand_k"
    old_list = con["info"]
    new_list = []
    for shell_index in range(len(old_list)):
        new_tuple = (
            old_list[shell_index][0], old_list[shell_index][1], old_list[shell_index][2],
            old_list[shell_index][3] + 1,
            old_list[shell_index][4] + 2)
        new_list.append(new_tuple)
    expand_con["info"] = new_list
    return expand_con


def shrink_c(con):
    shrink_con = dict()
    shrink_con["name"] = "shrink_c"
    old_list = con["info"]
    new_list = []
    for shell_index in range(len(old_list)):
        new_tuple = (
            old_list[shell_index][0], old_list[shell_index][1], old_list[shell_index][2],
            old_list[shell_index][3] - 4,
            old_list[shell_index][4] - 2)
        new_list.append(new_tuple)
    shrink_con["info"] = new_list
    return shrink_con


def expand_c(con):
    expand_con = dict()
    expand_con["name"] = "expand_c"
    old_list = con["info"]
    new_list = []
    for shell_index in range(len(old_list)):
        new_tuple = (
            old_list[shell_index][0], old_list[shell_index][1], old_list[shell_index][2],
            old_list[shell_index][3] + 2,
            old_list[shell_index][4] + 1)
        new_list.append(new_tuple)
    expand_con["info"] = new_list
    return expand_con


if __name__ == "__main__":
    gs = {"NYC": (-74.0059731, 40.7143528),  # 纽约
          "LA": (-122.4194, 37.7749),  # 洛杉矶
          "BJ": (116.4, 39.9),  # 北京
          "SY": (150.88, -33.91),  # 悉尼
          "LD": (0.11, 51.5),  # 伦敦
          "JNB": (27.9, -26.13),  # 约翰内斯堡
          "RIO": (-43.2, -22.95),  # 里约热内卢
          "SP": (103.85, 1.3),  # 新加坡
          "DB": (55.3, 25.3),  # 迪拜
          "TK": (139.73, 35.7),  # 东京
          "XDL": (77.2, 38.6),  # 新德里
          "CL": (31, 30)  # 开罗
          }

    init_kuiper_con = {
        "name": "init_con",
        "info": [(1, 630, 51.9, 34, 34),
                 (2, 610, 42, 36, 36),
                 (3, 590, 33, 28, 28)]
    }
    # init_kuiper_con_1 = {
    #     "name": "shrink_c3",
    #     "info": [(1, 630, 51.9, 22, 28),
    #              (2, 610, 42, 24, 30),
    #              (3, 590, 33, 16, 22)]
    # }

    # starlink_info = {
    #     "name": "star_init",
    #     "info": [(1, 550, 53, 72, 22),
    #              (2, 540, 53.2, 72, 22),
    #              (3, 570, 70, 36, 20),
    #              (4, 560, 97.6, 6, 58),
    #              (4, 560, 97.6, 4, 43)]
    # }

    # starlink_info_half = {
    #     "name": "star_half",
    #     "info": [(1, 550, 53, 36, 22),
    #              (2, 540, 53.2, 36, 22),
    #              (3, 570, 70, 18, 20),
    #              (4, 560, 97.6, 6, 30),
    #              (4, 560, 97.6, 4, 20)]
    # }

    gw_file_path = "../gw_amazon.txt"  #
    lr = 10
    K_T = 1
    C_T = 2

    con_info = init_kuiper_con  #
    count = 0
    file = open("./research_log.txt", "a")

    while True:
        ret = con_feasibility_check(con_info, gw_file_path, lr, gs, K_T, C_T)  # 接收到一个tuple （星座的K满足率，星座的C满足率）
        file.write(con_info["name"] + ":")
        file.write(str(con_info["info"]))
        print('finish !', ret, con_info["name"], con_info["info"])
        flag, con_info = check_and_modify(con_info, ret[0], ret[1])
        file.write("Feasible \n" if flag else "Infeasible \n")

        count += 1
        con_info["name"] = con_info["name"] + str(count)
        if count > 8 and flag:
            break

    file.close()
