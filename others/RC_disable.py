import time

from utils import *
from Topo import *
import multiprocessing
from datetime import datetime
import os
from itertools import starmap

from RC_mod import *

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
    init_con_info = {
        "name": "init_con",
        "info": [(1, 600, 90, 40, 17)]
    }

    gw_file_path = "../gw_amazon.txt"  #
    lr = 10
    K_T = 1
    C_T = 2
    con_info = init_con_info

    ret = con_feasibility_check(con_info, gw_file_path, lr, gs, K_T, C_T)
    print("破损后的星座的状态：", ret[0], ret[1])
