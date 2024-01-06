import ast
from Constellation_model import *
from utils import *
import numpy as np
import multiprocessing


# 读取rand_point文件，返回列表
def rand_point_reader(rp_file_path, t):
    rp_list = []
    rp_file = open(rp_file_path, "r")
    line = rp_file.readline()
    while line:
        line_stripe = line.strip()
        tuple_obj = ast.literal_eval(line_stripe)
        tuple_obj_t = get_coordinate_in_earth(tuple_obj, t)
        rp_list.append(tuple_obj_t)
    rp_file.close()
    return rp_list


# 只需要构建星座就行了，因为只要看看每时每刻地面上的一点头上能有颗卫星
def con_position_dict(con, t):  # 这里的输入不能有name 就一个纯纯info
    con_info = con["info"]
    con = Constellation(con_info, t)
    cpd, c_matrix, sat_lst = con.constellation_topo()
    return cpd


def one_slot_statistics(con, t):
    rp_list = rand_point_reader("rand_point.txt", t)
    con_pos_dict = con_position_dict(con, t)
    stat_array = np.zeros(len(rp_list), dtype=int)
    for index in range(len(rp_list)):
        rand_point = rp_list[index]
        neigh_lst = find_connectable_satellite(rand_point, con_pos_dict)
        stat_array[index] = len(neigh_lst)

    directory = "./coverage_stat/{}".format(con["name"])
    if not os.path.exists(directory):
        os.makedirs(directory)
    np.savetxt(directory + "./" + t)

    aver = np.mean(stat_array)
    coverage_rate = np.count_nonzero(stat_array) / len(stat_array)
    return con["name"], t, aver, coverage_rate


if __name__ == "__main__":
    time_list = [600 * i for i in range(0, 10)]
    Kuiper_origin = {
        "name": "Kuiper_origin",
        "info": [(1, 630, 51.9, 34, 34),
                 (2, 610, 42, 36, 36),
                 (3, 590, 33, 28, 28)]
    }
    Kuiper_reduced = {
        "name": "Kuiper_reduced",
        "info": [(1, 630, 51.9, 23, 23),
                 (2, 610, 42, 25, 25),
                 (3, 590, 33, 17, 17)]
    }
    Starlink_origin = {
        "name": "Starlink_origin",
        "info": [(1, 550, 53, 72, 22),
                 (2, 1100, 53.8, 32, 50),
                 (3, 1130, 74, 8, 50),
                 (4, 1275, 81, 5, 75),
                 (5, 1325, 70, 6, 75)]
    }
    Starlink_reduced = {
        "name": "Starlink_reduced",
        "info": [(1, 550, 53, 12, 22),
                 (2, 1100, 53.8, 32, 10),
                 (3, 1130, 74, 8, 10),
                 (4, 1275, 81, 5, 35),
                 (5, 1325, 70, 6, 35)]

    }

    con_list = [Kuiper_origin, Kuiper_origin, Starlink_origin, Starlink_reduced]
    para_list = []
    for Con in con_list:
        for T in time_list:
            para_list.append((Con, T))

    pool = multiprocessing.Pool()
    return_values = pool.starmap(one_slot_statistics, para_list)

    pool.join()
    pool.close()

    stat_file = open("./stat.txt", "w")
    for item in return_values:
        stat_file.write(str(item) + "\n")

    stat_file.close()

