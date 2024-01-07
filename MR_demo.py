from utils import *
from Topo import *
import multiprocessing
from datetime import datetime
import os
from itertools import starmap
import json
"""
# After modification, the function can exit in time, which means that if in the time slice, 
the number of paths between a communication pair is found to not meet the minimum requirements, then exit immediately, 
do not continue to count other communication pairs
"""


def run_for_one_time_slot(para_tuple):
    constellation = para_tuple[0]
    gw_file_path = para_tuple[1]
    lr = para_tuple[2]
    t = para_tuple[3]
    cp_dict = para_tuple[4]
    k_threshold = para_tuple[5]
    capa_threshold = 4  # you can specify how many satellites can connect at least
    con_name = constellation["name"]
    lambda_ratio = lr
    in_t = IntegratedNetwork(constellation["info"], gw_file_path,
                             t)
    gs = cp_dict
    gs_list = list(gs.keys())
    pairs_list = generate_pairs_combination(gs_list)

    directory = "./Kuiper_{}/PathValue{}".format(con_name, lambda_ratio)
    if not os.path.exists(directory):
        os.makedirs(directory)
    path_file = open(directory + "/" + "path_value_{}.txt".format(t), "a")

    for pair in pairs_list:
        src = pair[0]
        dst = pair[1]
        final_topo, k_max = in_t.fin_topo(src, dst, gs)
        k_max = int(k_max)
        if k_max < k_threshold:  # At least ensure that each communication nod can be connected, there is no less than the required number of satellites
            print(con_name, "too less sat over head!", src, dst)
            path_file.close()
            return False
        if k_max < capa_threshold:
            print(con_name, "not enough capacity!", src, dst)
            path_file.close()
            return False
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
                find_used_link(edges, final_lst, src, dst, t, lambda_ratio, con_name)
                if k <= k_threshold:  # If not passing the test, you don't have to move on
                    path_file.close()
                    print(con_name, "at", t, False, src, "to", dst)
                    return False
                break
            else:
                ret_tuple = (src, dst, k, value, time_solve)
                path_file.write(str(ret_tuple) + "\n")
                final_lst = final_lst + ret_list
                if k == k_threshold:  # In order to save time, if the k_threshold path has already been found, then do not count the current communication
                    find_used_link(edges, final_lst, src, dst, t, lambda_ratio, con_name)
                    break

    path_file.close()

    # This indicates that all communication pairs in this time slice meet the requirements of K_threshold and can exit normally
    return True


"""
This function checks the feasibility of a certain constellation. If it passes, it returns True;
 if it fails, it immediately terminates the check on the constellation, exits the function, and returns False
 
Only check if the provided constellation meets the conditions under one lambda rate（hops limit）
"""


def con_feasibility_check(con, gw_path, lr, cp_dict, k_threshold):
    fea_flag = True
    time_list = [60 * i for i in range(0, 100)]  # you can set the time slices!!
    para_list = []  # the length is 100
    for slot in time_list:
        para_list.append((con, gw_path, lr, slot, cp_dict, k_threshold))

    supervisor = multiprocessing.Value('i', True)
    pool = multiprocessing.Pool()

    return_values = pool.imap(run_for_one_time_slot, para_list)

    # Monitor the return values in real-time
    for value in return_values:
        with supervisor.get_lock():
            if not value:
                supervisor.value = False
                break
        if not supervisor.value:
            break

    # Terminate all processes if False is found
    if not supervisor.value:
        pool.terminate()
        fea_flag = False
        print("Terminated all child processes.")
    else:
        print("All child processes completed successfully.")

    # Close the Pool
    pool.close()
    pool.join()

    return fea_flag


"""
The function of this function is to reduce the size of the constellation, 
you can specify the way to reduce the number of orbits (tuple[3]) or reduce the number of satellites per orbit (tuple[4])

Given the original constellation, output the new constellation
"""


def con_shrink(con, count):
    shrink_con = dict()
    shrink_con["name"] = "shrink{}".format(count)
    old_list = con["info"]
    new_list = []
    for shell_index in range(len(old_list)):
        if shell_index == 0:
            new_tuple = (
                old_list[shell_index][0], old_list[shell_index][1], old_list[shell_index][2],
                old_list[shell_index][3] - 4,
                old_list[shell_index][4])
        else:
            new_tuple = (
                old_list[shell_index][0], old_list[shell_index][1], old_list[shell_index][2],
                old_list[shell_index][3],
                old_list[shell_index][4] - 4)

        new_list.append(new_tuple)
    shrink_con["info"] = new_list

    return shrink_con


"""
The function of this function is to expand the size of the constellation, 
you can specify the way to expand the number of orbits (tuple[3]) or expand the number of satellites per orbit (tuple[4])

Given the original constellation, output the new constellation
"""


def con_expand(con, count):
    expand_con = dict()
    expand_con["name"] = "expand{}".format(count)
    old_list = con["info"]
    new_list = []
    for shell_index in range(len(old_list)):
        if shell_index == 0:
            new_tuple = (
                old_list[shell_index][0], old_list[shell_index][1], old_list[shell_index][2],
                old_list[shell_index][3] + 1,
                old_list[shell_index][4])
        else:
            new_tuple = (
                old_list[shell_index][0], old_list[shell_index][1], old_list[shell_index][2],
                old_list[shell_index][3],
                old_list[shell_index][4] + 1)

        new_list.append(new_tuple)
    expand_con["info"] = new_list

    return expand_con


if __name__ == "__main__":
    # Run 100 time slices, spaced 60 seconds apart

    # given the constellation info in dict
    # each item in info list is one shell in constellation
    # (shell number, altitude, orbital inclination, number of orbits, number of satellites per orbit)
    with open('configuration.json', 'r') as file:
        data = json.load(file)


    init_con = data['init_con']
    gw_file_path = data['gw_file_path']
    lr = data['delay_constraint']  # delay constraints,The hop count of the optional path should be less than the value multiplied by the shortest hop count

    # Select the geographical location of the communication point, which you can specify. Make them evenly distributed across the globe
    gs = data['commu_locations']
    # Survivability requires that the disjoint path between any two communication pairs should not be less than this value
    K_T = data['survivability']
    shrink_count = 0
    expand_count = 0

    con_info = init_con

    iterations = data['iterations']

    file = open("./con_log.log", "a")

    while True:
        ret = con_feasibility_check(con_info, gw_file_path, lr, gs, K_T)
        file.write("Feasible " if ret else "Infeasible ")
        file.write(con_info["name"] + ":")
        file.write(str(con_info["info"]) + "\n")
        print('finish !', ret, con_info["name"], con_info["info"])
        if (shrink_count + expand_count) > iterations and ret:
            break

        if ret:  # The current constellation passed the inspection, indicating that the current constellation is still large enough to support minimum k and needs to be further reduced
            shrink_count += 1
            con_info = con_shrink(con_info, shrink_count)
        else:  # The current constellation cannot pass the inspection, indicating that the scale of the current constellation is insufficient to support the minimum k and needs to be further expanded
            expand_count += 1
            con_info = con_expand(con_info, expand_count)

    file.close()

