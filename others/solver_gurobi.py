import time
from utils import *
import gurobipy as gp
from gurobipy import GRB

def neigh_dict_generator(edges):
    neighbour_dict = {}
    for item in edges:
        src = item[0]
        dst = item[1]
        if src not in neighbour_dict:
            neighbour_dict[src] = []

        if dst not in neighbour_dict:
            neighbour_dict[dst] = []

        neighbour_dict[src].append(dst)
        neighbour_dict[dst].append(src)
    return neighbour_dict


def find_neigh_index_and_direction(node, neighbour_dict, edges):
    neighbour_list = neighbour_dict[node]  # 找到某一个卫星的所有邻居节点了，接着就是构造该边，然后在edge_list中去寻找该边的index
    artificial_edge_list = []
    for neigh in neighbour_list:
        artificial_edge_list.append((node, neigh))
        artificial_edge_list.append((neigh, node))

    neigh_edge_index_list = []
    directions = []
    for item in artificial_edge_list:
        if item in edges:
            index_to_add = edges.index(item)
            neigh_edge_index_list.append(index_to_add)
            if item[0] == node:  # 此时说明是源 1 表示流出
                directions.append(1)
            else:  # 此时说明是目的 0 表示流入
                directions.append(0)

    return neigh_edge_index_list, directions


def gurobi_solver(graph, edges, k_path):  # 原来的大K就是这里的k
    start_time = time.time()
    # edges = get_edges(graph)  # 3236*2 + 16 + 17 = 6472 + 33 =6505
    num_sat = graph.shape[0] - 2  # 3236
    gs_num = 2
    sat_list = ['S{}'.format(s + 1) for s in range(num_sat)]  # 3236是卫星数量
    gs_list = ['GA', 'GB']  # 有2个地站，用字母顺序命名
    node_list = sat_list + gs_list
    gs_pair_directed = generate_pairs_permutation(gs_list)
    neighbour_dict = neigh_dict_generator(edges)
    # 以下代码为模型构造过程，有三个步骤，分别是构造变量，目标，约束
    src_dst_pair_num = len(gs_pair_directed)  # 2对
    edge_num = len(edges)  # 6503
    model = gp.Model("Binary Programming")
    core_edge_set = model.addVars(edge_num, vtype=GRB.BINARY, name="core_variables")
    peripheral_edge_set = model.addVars(edge_num, src_dst_pair_num, k_path, 2, vtype=GRB.BINARY,
                                        name="peripheral_variables")
    model.update()

    weight = [1] * edge_num
    product_expr = gp.LinExpr()
    for i in range(len(weight)):
        product_expr.add(core_edge_set[i], weight[i])

    model.setObjective(product_expr, GRB.MINIMIZE)

    #
    # # 接下来就是添加约束了
    #
    # 1.流量守恒约束之——卫星流量守恒
    """
    找到对应的一条流（src,dst,k）
    找到一颗卫星
    找到与之邻接的所有边对应的角标（在edge_list中）
    构造流量守恒关系
    """
    for j in range(src_dst_pair_num):
        for k in range(k_path):

            for sat in sat_list:
                neil, dirs = find_neigh_index_and_direction(sat, neighbour_dict, edges)

                # 流入  =  流出
                input_sum = gp.quicksum(peripheral_edge_set[neil[i], j, k, dirs[i]] for i in
                                        range(len(neil)))
                output_sum = gp.quicksum(peripheral_edge_set[neil[i], j, k, 1 - dirs[i]] for i in
                                         range(len(neil)))
                model.addConstr(input_sum == output_sum)
    # 2.流量守恒之——对于每一条流（src,dst,k）起点点必须在一个邻居中选择一个出发，终点必须在一个邻居中选择进入

    for j in range(src_dst_pair_num):
        src = gs_pair_directed[j][0]
        neil_src, dirs_src = find_neigh_index_and_direction(src, neighbour_dict, edges)
        dst = gs_pair_directed[j][1]
        neil_dst, dirs_dst = find_neigh_index_and_direction(dst, neighbour_dict, edges)
        for k in range(k_path):
            output_sum = gp.quicksum(
                peripheral_edge_set[neil_src[i], j, k, 1 - dirs_src[i]] for i in range(len(neil_src)))
            model.addConstr(output_sum == 1)

            input_sum = gp.quicksum(
                peripheral_edge_set[neil_dst[i], j, k, dirs_dst[i]] for i in range(len(neil_dst)))
            model.addConstr(input_sum == 1)
    # 3.作为中转节点的卫星的流量守恒

    for j in range(src_dst_pair_num):
        src = gs_pair_directed[j][0]
        dst = gs_pair_directed[j][1]
        for k in range(k_path):
            for g in range(len(gs_list)):
                if dst != gs_list[g] and src != gs_list[g]:  # 这里的意思是说 对于一条流而言，某个地站，该地站既不是源头，也不是目的地，只是作为中间转发的一个节点
                    neil, dirs = find_neigh_index_and_direction(gs_list[g], neighbour_dict, edges)
                    input_sum = gp.quicksum(peripheral_edge_set[neil[i], j, k, dirs[i]] for i in
                                            range(len(neil)))
                    output_sum = gp.quicksum(peripheral_edge_set[neil[i], j, k, 1 - dirs[i]] for i in
                                             range(len(neil)))
                    model.addConstr(input_sum == output_sum)

    # 4.不相交约束
    for i in range(edge_num):
        for j in range(src_dst_pair_num):
            sum1 = gp.quicksum(peripheral_edge_set[i, j, k, 0] for k in range(k_path))
            sum2 = gp.quicksum(peripheral_edge_set[i, j, k, 1] for k in range(k_path))
            model.addConstr(sum1 + sum2 <= 1)
    # 5.非线性约束
    for i in range(edge_num):
        for j in range(src_dst_pair_num):
            for k in range(k_path):
                for t in range(2):
                    model.addConstr(core_edge_set[i] >= peripheral_edge_set[i, j, k, t])

    # 6.防止流量回踢约束——是第4个约束的子集
    for i in range(edge_num):
        for j in range(src_dst_pair_num):
            for k in range(k_path):
                model.addConstr(gp.quicksum(peripheral_edge_set[i, j, k, t] for t in range(2)) <= 1)

    # 7.防止环路约束——这属于非必要约束，起到优化作用，起点出去的流量就别再回来了
    for j in range(src_dst_pair_num):
        src = gs_pair_directed[j][0]
        neil_src, dirs_src = find_neigh_index_and_direction(src, neighbour_dict, edges)
        for k in range(k_path):
            for i in range(len(neil_src)):
                model.addConstr(peripheral_edge_set[neil_src[i], j, k, dirs_src[i]] == 0)
    # 8.防止流量到达终点之后依然乱跑的约束
    for j in range(src_dst_pair_num):
        dst = gs_pair_directed[j][1]
        neil_dst, dirs_dst = find_neigh_index_and_direction(dst, neighbour_dict, edges)
        for k in range(k_path):
            for i in range(len(neil_dst)):
                wis = peripheral_edge_set[neil_dst[i], j, k, 1 - dirs_dst[i]] == 0
                model.addConstr(peripheral_edge_set[neil_dst[i], j, k, 1 - dirs_dst[i]] == 0)

    model.optimize()

    ret_edge_lst = []

    if model.status == GRB.OPTIMAL:
        print("Optimal solution found!")
        print("Objective value: ", model.objVal)
        bin_values = model.getAttr("x", core_edge_set)
        for var in core_edge_set:
            ret_edge_lst.append(bin_values[var])

        finish_time = time.time()
        total_time = finish_time - start_time
        print('total_time:', total_time)
        return model.objVal, total_time, ret_edge_lst
    else:
        print("No solution found.")
        finish_time = time.time()
        total_time = finish_time - start_time
        print('total_time:', total_time)
        return 10000, total_time, None