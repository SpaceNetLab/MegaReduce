import numpy as np
from itertools import permutations


def get_edges(adjacency_matrix):
    edges = []
    num_vertices = len(adjacency_matrix)

    for i in range(num_vertices):
        for j in range(i + 1, num_vertices):
            if adjacency_matrix[i][j] == 1:
                if i < 25:
                    src = 'S{}'.format(i + 1)
                elif i == 25:
                    src = 'GA'
                elif i == 26:
                    src = 'GB'
                else:
                    src = 'GC'

                if j < 25:
                    dst = 'S{}'.format(j + 1)
                elif j == 25:
                    dst = 'GA'
                elif j == 26:
                    dst = 'GB'
                else:
                    dst = 'GC'

                edges.append((src, dst))

    return edges


def generate_pairs(lst):
    # Use permutations function to generate all 2-element permutations
    pairs = permutations(lst, 2)

    # Convert permutations object to a list of tuples
    pairs_list = list(pairs)

    return pairs_list


if __name__ == "__main__":
    Graph = np.loadtxt("553_weighted.csv", delimiter=',', dtype=int)
    # 全都转化为1
    Graph_1 = np.where(Graph > 0, 1, 0)
    Edges = get_edges(Graph_1)  # 62条边

    # 构造卫星、地站、所有点的列表
    sat_list = ['S{}'.format(i + 1) for i in range(25)]
    gs_list = ['GA', 'GB', 'GC']
    node_list = sat_list + gs_list
    # print(len(Edges))
    K = 4  # 先把k设置为3

    '''
    以下代码为构造变量文件，根据选择的K，构造出variables.txt文件
    '''
    file = open("variables_{}.txt".format(K), "w")
    # 构造核心变量
    for i in range(len(Edges)):
        src = Edges[i][0]
        dst = Edges[i][1]
        variable_name = 'X_{}_{}'.format(src, dst)
        str = variable_name + ' = model.addVar(vtype=GRB.BINARY, name="{}")'.format(variable_name)
        # x1 = model.addVar(vtype=GRB.BINARY, name="x1") 构造成这个样子
        file.write(str + '\n')

    # 构造其余变量
    gs_pair_directed = generate_pairs(gs_list)  # 这一步构造五元组的第一个元素（流量的起点）和第二个元素（流量的终点）的pair
    for i in range(len(gs_pair_directed)):
        src = gs_pair_directed[i][0]
        dst = gs_pair_directed[i][1]
        for k in range(1, K + 1):  # 这里是为了构造五元组的第三个元素 k
            for t in range(len(Edges)):
                variable_name_1 = 'X_{}_{}_{}_{}_{}'.format(src, dst, k, Edges[t][0], Edges[t][1])
                str_1 = variable_name_1 + ' = model.addVar(vtype=GRB.BINARY, name="{}")'.format(variable_name_1)
                file.write(str_1 + '\n')
                variable_name_2 = 'X_{}_{}_{}_{}_{}'.format(src, dst, k, Edges[t][1], Edges[t][0])
                str_2 = variable_name_2 + ' = model.addVar(vtype=GRB.BINARY, name="{}")'.format(variable_name_2)
                file.write(str_2 + '\n')

    file.close()
    '''
    以下代码为构造目标函数
    '''
    file = open("objective_{}.txt".format(K), "w")
    # model.setObjective(x1 + 2 * x2 + 3 * x3, GRB.MAXIMIZE)
    obj_str = ''
    for i in range(len(Edges)):
        src = Edges[i][0]
        dst = Edges[i][1]
        variable_name = 'X_{}_{}'.format(src, dst)
        weight = 10
        if src in ('GA', 'GB', 'GC') or dst in ('GA', 'GB', 'GC'):
            weight = 1
        if weight == 1:
            obj_str += '{} + '.format(variable_name)
        else:
            obj_str += '{} * {} + '.format(weight, variable_name)

    obj_str = obj_str[:-2]
    obj_str = ' model.setObjective(' + obj_str + ', GRB.MINIMIZE)'
    file.write(obj_str + '\n')
    file.close()

    '''
    以下代码为构造约束
    model.addConstr(x1 + x2 + x3 <= 2, "c1")
    '''
    neighbour_dict = {}

    for item in Edges:
        src = item[0]
        dst = item[1]
        if src not in neighbour_dict:
            neighbour_dict[src] = []

        if dst not in neighbour_dict:
            neighbour_dict[dst] = []

        neighbour_dict[src].append(dst)
        neighbour_dict[dst].append(src)

    file = open("constraints_{}.txt".format(K), "w")

    '''
    流量约束
    '''
    # 先构造邻居关系，用字典的形式盛放，'S1':['S2','S5','S6','S21','GA']

    # 对任何一条流而言，每一个卫星节点，入流量等于出流量（450个约束 25*3*6）
    for i in range(len(gs_pair_directed)):
        src = gs_pair_directed[i][0]
        dst = gs_pair_directed[i][1]
        for k in range(1, K + 1):
            for s in range(len(sat_list)):
                neighbour_list = neighbour_dict[sat_list[s]]
                constraint_str = ''
                for neighbour_element in neighbour_list:
                    constraint_str += 'X_{}_{}_{}_{}_{} - '.format(src, dst, k, neighbour_element, sat_list[s])
                    constraint_str += 'X_{}_{}_{}_{}_{} + '.format(src, dst, k, sat_list[s], neighbour_element)

                constraint_str = constraint_str[:-2] + ' == 0'
                constraint_str = 'model.addConstr(' + constraint_str + ', \"' + '{} balance'.format(sat_list[s]) + '\")'
                file.write(constraint_str + '\n')

    # 对于每一个流量发出点，首先要满足这一个点到任何另外一点发出的总流量是K （6*2 = 12个约束）
    for i in range(len(gs_pair_directed)):
        src = gs_pair_directed[i][0]
        dst = gs_pair_directed[i][1]
        constraint_str_out = ''
        constraint_str_in = ''
        neighbour_list_out = neighbour_dict[src]
        neighbour_list_in = neighbour_dict[dst]

        for k in range(1, K + 1):
            for neigh in neighbour_list_out:
                constraint_str_out += 'X_{}_{}_{}_{}_{} + '.format(src, dst, k, src, neigh)

        constraint_str_out = constraint_str_out[:-2] + ' == {}'.format(K)
        constraint_str_out = 'model.addConstr(' + constraint_str_out + ', \"' + '{} out {} in'.format(src, dst) + '\")'
        file.write(constraint_str_out + '\n')

        for k in range(1, K + 1):
            for neigh in neighbour_list_in:
                constraint_str_in += 'X_{}_{}_{}_{}_{} + '.format(src, dst, k, neigh, dst)

        constraint_str_in = constraint_str_in[:-2] + ' == {}'.format(K)
        constraint_str_in = 'model.addConstr(' + constraint_str_in + ', \"' + '{} in {} out'.format(dst, src) + '\")'
        file.write(constraint_str_in + '\n')

    # 出射约束与入射约束 共计
    for i in range(len(gs_pair_directed)):
        src = gs_pair_directed[i][0]
        dst = gs_pair_directed[i][1]

        neighbour_list_out = neighbour_dict[src]
        neighbour_list_in = neighbour_dict[dst]
        for k in range(1, K + 1):
            constraint_str_out = ''
            for neigh in neighbour_list_out:
                constraint_str_out += 'X_{}_{}_{}_{}_{} + '.format(src, dst, k, src, neigh)
            constraint_str_out = constraint_str_out[:-2] + ' == 1'
            constraint_str_out = 'model.addConstr(' + constraint_str_out + ', \"' + '{} out {} in out_constraint{}'.format(
                src,
                dst, k) + '\")'
            file.write(constraint_str_out + '\n')

        for k in range(1, K + 1):
            constraint_str_in = ''
            for neigh in neighbour_list_in:
                constraint_str_in += 'X_{}_{}_{}_{}_{} + '.format(src, dst, k, neigh, dst)
            constraint_str_in = constraint_str_in[:-2] + ' == 1'
            constraint_str_in = 'model.addConstr(' + constraint_str_in + ', \"' + '{} out {} in in_constraint{}'.format(
                src,
                dst, k) + '\")'
            file.write(constraint_str_in + '\n')

    '''
    不相交约束
    '''
    for i in range(len(gs_pair_directed)):
        src = gs_pair_directed[i][0]
        dst = gs_pair_directed[i][1]

        for t in range(len(Edges)):
            node_1 = Edges[t][0]
            node_2 = Edges[t][1]
            constraint_disjoint_1 = ''
            for k in range(1, K + 1):
                constraint_disjoint_1 += 'X_{}_{}_{}_{}_{} + '.format(src, dst, k, node_1, node_2)
            constraint_disjoint_1 = constraint_disjoint_1[:-2] + ' <= 1'
            constraint_disjoint_1 = 'model.addConstr(' + constraint_disjoint_1 + ', \"' + 'k={} {} {} disjoint'.format(
                k,
                node_1,
                node_2) + '\")'
            file.write(constraint_disjoint_1 + '\n')

            constraint_disjoint_2 = ''
            for k in range(1, K + 1):
                constraint_disjoint_2 += 'X_{}_{}_{}_{}_{} + '.format(src, dst, k, node_2, node_1)
            constraint_disjoint_2 = constraint_disjoint_2[:-2] + ' <= 1'
            constraint_disjoint_2 = 'model.addConstr(' + constraint_disjoint_2 + ', \"' + 'k={} {} {} disjoint'.format(
                k,
                node_2,
                node_1) + '\")'
            file.write(constraint_disjoint_2 + '\n')

    '''
    目标函数非线性转化约束
    '''
    for t in range(len(Edges)):  # 构造核心变量
        node_1 = Edges[t][0]
        node_2 = Edges[t][1]
        core_variable_name = 'X_{}_{}'.format(node_1, node_2)

        for i in range(len(gs_pair_directed)):
            src = gs_pair_directed[i][0]
            dst = gs_pair_directed[i][1]
            for k in range(1, K + 1):
                constraint_non_linear_1 = ''
                peri_variable_name_1 = 'X_{}_{}_{}_{}_{}'.format(src, dst, k, node_1, node_2)
                constraint_non_linear_1 += core_variable_name + ' - ' + peri_variable_name_1 + ' >= 0 '
                constraint_non_linear_1 = 'model.addConstr(' + constraint_non_linear_1 + ', \"' + 'cv {} {} nl for {} {} {} '.format(
                    node_1, node_2, src, dst, k) + '\")'
                file.write(constraint_non_linear_1 + '\n')

                constraint_non_linear_2 = ''
                peri_variable_name_2 = 'X_{}_{}_{}_{}_{}'.format(src, dst, k, node_2, node_1)
                constraint_non_linear_2 += core_variable_name + ' - ' + peri_variable_name_2 + ' >= 0 '
                constraint_non_linear_2 = 'model.addConstr(' + constraint_non_linear_2 + ', \"' + 'cv {} {} nl for {} {} {} '.format(
                    node_2, node_1, src, dst, k) + '\")'
                file.write(constraint_non_linear_2 + '\n')

    '''
    防止流量回踢
    '''
    for i in range(len(gs_pair_directed)):
        src = gs_pair_directed[i][0]
        dst = gs_pair_directed[i][1]
        for k in range(1, K + 1):
            for t in range(len(Edges)):
                constraint_back_forbidden = ''
                node_1 = Edges[t][0]
                node_2 = Edges[t][1]
                variable_name_1 = 'X_{}_{}_{}_{}_{}'.format(src, dst, k, node_1, node_2)
                variable_name_2 = 'X_{}_{}_{}_{}_{}'.format(src, dst, k, node_2, node_1)
                constraint_back_forbidden += variable_name_1 + ' + ' + variable_name_2 + ' <= 1 '
                constraint_back_forbidden = 'model.addConstr(' + constraint_back_forbidden + ', \"' + 'noback {} {} {} {} {}'.format(
                    src, dst, k, node_1, node_2) + '\")'
                file.write(constraint_back_forbidden + '\n')

    '''
    防止自我回环
    '''
    for i in range(len(gs_pair_directed)):
        src = gs_pair_directed[i][0]
        dst = gs_pair_directed[i][1]
        neighbour_list_src = neighbour_dict[src]
        for neigh in neighbour_list_src:
            for k in range(1, K + 1):
                constraint_loop_forbidden = ''
                variable_name = 'X_{}_{}_{}_{}_{}'.format(src, dst, k, neigh, src)
                constraint_loop_forbidden += variable_name + ' == 0'
                constraint_loop_forbidden = 'model.addConstr(' + constraint_loop_forbidden + ', \"' + 'noloop {} {} {} {} {}'.format(
                    src, dst, k, neigh, src) + '\")'
                file.write(constraint_loop_forbidden + '\n')

    '''
    这是一个可加可不加的约束：
        如果一条流已经到达目标了，就不要再出走了（乱射）
    '''
    for i in range(len(gs_pair_directed)):
        src = gs_pair_directed[i][0]
        dst = gs_pair_directed[i][1]
        neighbour_list_dst = neighbour_dict[dst]
        for neigh in neighbour_list_dst:
            for k in range(1, K + 1):
                constraint_no_random_out = ''
                variable_name = 'X_{}_{}_{}_{}_{}'.format(src, dst, k, dst, neigh)
                constraint_no_random_out += variable_name + ' == 0'
                constraint_no_random_out = 'model.addConstr(' + constraint_no_random_out + ', \"' + 'norout {} {} {} {} {}'.format(
                    src, dst, k, dst, neigh) + '\")'
                file.write(constraint_no_random_out + '\n')

    file.close()

'''
X_GA_GB_1_S2_GA = 1.0
X_GA_GB_1_GA_S2 = 1.0
X_GA_GB_1_S15_GB = 1.0
X_GA_GB_1_GB_S15 = 1.0

这里是把流量踢回来了，这里加一个约束，防止流量第一步回笼

'''
