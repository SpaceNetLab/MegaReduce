import os
import ast

import numpy as np

from utils import *
import pandas as pd


def read_one_txt_for_sat(filepath):
    file = open(filepath, "r")
    output_str = ""
    line = file.readline()
    while line:
        line_stripe = line.strip()
        output_str += line_stripe
        line = file.readline()
    file.close()

    list_of_tuples = eval("[" + output_str.replace(")(", "), (") + "]")

    node_set = set()
    for item in list_of_tuples:
        node_set.add(item[0])
        node_set.add(item[1])

    prefix = "G"
    num_gw = 30
    gw_lst = [prefix + str(i) for i in range(1, num_gw + 1)]  # ['G1','G2',…………]
    ground_node = ["LA", "NYC", "BJ", "SY", "LD", "JNB", "RIO"]
    sat_set = node_set.difference(ground_node + gw_lst)

    return sat_set


def read_one_txt_for_path(filepath):
    file = open(filepath, "r")
    line = file.readline()
    count_lst = []
    while line:
        line_stripe = line.strip()
        tuple_value = ast.literal_eval(line_stripe)
        count_lst.append(int(tuple_value[2]))
        line = file.readline()
    file.close()

    k_lst = []
    for i in range(len(count_lst) - 1):
        if count_lst[i] >= count_lst[i + 1]:
            k_lst.append(count_lst[i])

    k_lst.append(count_lst[-1])  # 至此，在一个时间片内，190个城市对的K值均得以统计

    return k_lst


if __name__ == "__main__":
    directory = "./kuiper_con1/UsedLink1.5"
    sat_nodes_set_all_slots = set()
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            Sat_set = read_one_txt_for_sat(directory + "/" + filename)
            sat_nodes_set_all_slots = sat_nodes_set_all_slots.union(Sat_set)

    # print(sat_nodes_set_all_slots)
    print(len(sat_nodes_set_all_slots))

    # 以上代码负责统计用了多少颗卫星

    # 以下代码负责统计最小k
    K_min_lst = []
    directory = "./Kuiper_con1/PathValue1.5"

    gs = {"NYC": (-74.0059731, 40.7143528),  # 纽约
          "LA": (-122.4194, 37.7749),  # 洛杉矶
          "BJ": (116.4, 39.9),  # 北京
          "SY": (150.88, -33.91),  # 悉尼
          "LD": (0.11, 51.5),  # 伦敦
          "JNB": (27.9, -26.13),  # 约翰内斯堡
          "RIO": (-43.2, -22.95),  # 里约热内卢
          "HK": (114.25, 22.25),  # 香港
          "SH": (121.7, 30.8),  # 上海
          "SP": (103.85, 1.3),  # 新加坡
          "DB": (55.3, 25.3),  # 迪拜
          "TK": (139.73, 35.7),  # 东京
          "XDL": (77.2, 38.6),  # 新德里
          "MOS": (37.5, 55.5),  # 莫斯科
          "BY": (-58.4, -34.6),  # 布宜诺斯艾利斯
          "BL": (13.04, 52.5),  # 柏林
          "PA": (2.3, 48.85),  # 巴黎
          "WT": (174.8, -41.3),  # 惠灵顿
          "TO": (-79.4, 43.7),  # 多伦多
          "CL": (31, 30)  # 开罗
          }

    cp_lst = [item for item in gs.keys()]

    header_lst = generate_pairs_combination(cp_lst)
    header_lst = ['time'] + header_lst

    df = pd.DataFrame(columns=header_lst)


    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            K_lst = read_one_txt_for_path(directory + "/" + filename)  # 一个时间片内，所有城市对之间的k值
            K_min = min(K_lst)  # 一个时间片内，所有城市对之间的k值的最小值
            str_no_subfix = filename.replace(".txt", "")
            str_lst = str_no_subfix.split("_")
            name = str_lst[-1]
            name = int(name)
            # if len(K_lst) != 190:
            #     print(filename)
            #     print(len(K_lst))

            lst_to_add = [name] + K_lst[0:190]
            #
            new_row_df = pd.DataFrame([lst_to_add], columns=df.columns)
            df = pd.concat([df, new_row_df], axis=0, ignore_index=True)
            K_min_lst.append(K_min)  # 多少个时间片，就有多少个元素

    global_k_min = min(K_min_lst)
    print(global_k_min)

    df_sorted_by_time = df.sort_values("time")
    excel_file = "./Kuiper_con1/K_sata_con1_1.5.xlsx"
    df_sorted_by_time.to_excel(excel_file, index=False)

