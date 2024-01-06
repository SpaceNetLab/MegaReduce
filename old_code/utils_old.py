import math
from itertools import combinations
from itertools import permutations
import numpy as np
import sys
import heapq
import time
import os


def calculate_distance(point1, point2):
    x1, y1, z1 = point1
    x2, y2, z2 = point2

    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)

    return distance


def calculate_cartesian_coordinates(altitude, inclination, raan, angle):
    earth_radius = 6371  # Radius of the Earth in kilometers
    radius = (earth_radius + altitude) * 1000  # Convert altitude to meters
    omega_plus_v = math.radians(angle)
    Omega = math.radians(raan)
    i = math.radians(inclination)

    a = math.cos(omega_plus_v) * math.cos(Omega) - math.sin(omega_plus_v) * math.cos(i) * math.sin(Omega)
    b = math.cos(omega_plus_v) * math.sin(Omega) + math.sin(omega_plus_v) * math.cos(i) * math.cos(Omega)
    c = math.sin(omega_plus_v) * math.sin(i)
    x = radius * a
    y = radius * b
    z = radius * c
    return x, y, z


def generate_pairs_combination(lst):
    # Use permutations function to generate all 2-element permutations
    pairs = combinations(lst, 2)
    # Convert combinations object to a list of tuples
    pairs_list = list(pairs)
    return pairs_list


def generate_pairs_permutation(lst):
    # Use permutations function to generate all 2-element permutations
    pairs = permutations(lst, 2)
    # Convert permutations object to a list of tuples
    pairs_list = list(pairs)

    return pairs_list


def get_coordinate_in_earth(ll, t=0):  # 获取任何一个坐标点（经纬度标识）在某一个时刻的笛卡尔坐标
    rotation_per_second = 360 / 86400  # 地球自转的速度，每一秒转过的角度
    longitude = ll[0]
    if longitude < 0:  # 将西经转到[0,360)的范围
        longitude += 360
    longitude = (longitude + t * rotation_per_second) % 360
    latitude = ll[1]
    lon_rad = math.radians(longitude)
    lat_rad = math.radians(latitude)
    radius = 6371000  # Radius of the Earth in meters
    x = radius * math.cos(lat_rad) * math.cos(lon_rad)
    y = radius * math.cos(lat_rad) * math.sin(lon_rad)
    z = radius * math.sin(lat_rad)
    return x, y, z


def calculate_angle(vector1, vector2):
    vector1 = list(vector1)
    vector2 = list(vector2)
    dot_product = np.dot(vector1, vector2)
    magnitude1 = np.linalg.norm(vector1)
    magnitude2 = np.linalg.norm(vector2)

    cosine_angle = dot_product / (magnitude1 * magnitude2)
    angle_rad = np.arccos(cosine_angle)
    angle_deg = np.degrees(angle_rad)
    return angle_deg


def find_connectable_satellite(ground, cpd):  # 最小仰角为35度，也就是说距离向量和地站向量的夹角应该小于55度
    sat_neighbour = []
    cpd_list = list(cpd.keys())
    for sat, pos in cpd.items():
        distance_vector = (pos[0] - ground[0], pos[1] - ground[1], pos[2] - ground[2])
        angle = calculate_angle(distance_vector, ground)
        if angle <= 55:
            sat_neighbour.append(cpd_list.index(sat))  # 记录可连接卫星的索引号，而不是名字

    return sat_neighbour


"""
A C1
B C2
original matrix ------ A
"""


def matrix_expand(origin_matrix, gs_dict, cpd, t):
    num_sat = origin_matrix.shape[0]
    num_gs = len(gs_dict)
    matrix_a = origin_matrix  # old * old
    gs_sat_dict = dict()

    for loc, ll in gs_dict.items():
        cart_coord = get_coordinate_in_earth(ll, t)
        gs_sat_dict[loc] = find_connectable_satellite(cart_coord, cpd)

    matrix_b = np.zeros((num_gs, num_sat), dtype=int)  # add * old

    index = 0
    for neighbour in gs_sat_dict.values():
        matrix_b[index][neighbour] = 1
        index += 1

    matrix_ab = np.row_stack((matrix_a, matrix_b))  # (old + add) * old

    matrix_c1 = np.transpose(matrix_b)  # sat * gs

    matrix_c2 = np.zeros((num_gs, num_gs), dtype=int)

    matrix_c = np.row_stack((matrix_c1, matrix_c2))

    expanded_matrix = np.column_stack((matrix_ab, matrix_c))

    if num_gs == 2:
        row_sum = np.sum(matrix_b, axis=1)
        return expanded_matrix, min(row_sum)

    else:
        return expanded_matrix


def dijkstra(adj_matrix, start_vertex, end_vertex):
    num_vertices = len(adj_matrix)

    # Initialize distance and visited arrays
    distance = [sys.maxsize] * num_vertices
    distance[start_vertex] = 0
    visited = [False] * num_vertices

    # Initialize parent array to store the path
    parent = [-1] * num_vertices

    # Create a priority queue (min heap) of vertices based on their distance
    priority_queue = [(0, start_vertex)]

    while priority_queue:
        # Get the vertex with the minimum distance from the priority queue
        dist, current_vertex = heapq.heappop(priority_queue)

        if visited[current_vertex]:
            continue

        visited[current_vertex] = True

        # Update distances of adjacent vertices
        for v in range(num_vertices):
            if not visited[v] and adj_matrix[current_vertex][v] > 0:
                new_distance = distance[current_vertex] + adj_matrix[current_vertex][v]
                if new_distance < distance[v]:
                    distance[v] = new_distance
                    parent[v] = current_vertex
                    heapq.heappush(priority_queue, (new_distance, v))

    # Build the shortest path
    shortest_path = []
    current_vertex = end_vertex
    while current_vertex != -1:
        shortest_path.append(current_vertex)
        current_vertex = parent[current_vertex]

    shortest_path.reverse()

    return distance[end_vertex], shortest_path


def modify_adjacency_matrix(adj_matrix, shortest_path):
    for i in range(len(shortest_path) - 1):
        u = shortest_path[i]  # Current vertex
        v = shortest_path[i + 1]  # Next vertex
        adj_matrix[u][v] = 0  # Set the weight of the edge to zero
        adj_matrix[v][u] = 0  # Set the weight of the edge to zero


def find_k_disjoint_ways_dj(adj_matrix, edges, in_t):
    start_time = time.time()
    src = adj_matrix.shape[0] - 2
    dst = adj_matrix.shape[1] - 1

    value, path = dijkstra(adj_matrix, src, dst)
    modify_adjacency_matrix(adj_matrix, path)

    ret_list = np.zeros(len(edges), dtype=int)

    for i in range(len(path) - 1):
        u = path[i]  # Current vertex
        v = path[i + 1]  # Next vertex
        index = find_index_in_edges(adj_matrix, edges, u, v, in_t)
        ret_list[index] = 1

    time_solve = time.time() - start_time

    return value, time_solve, ret_list


def find_index_in_edges(adj_matrix, edges, src_index, dst_index, in_t):
    num_sat = in_t.num_sat  # 不妨认为地站也是卫星，只关心两个通信对之间的通信
    num_gw = in_t.num_gw
    if src_index < num_sat:  # 是卫星
        src = "S{}".format(src_index + 1)
    elif src_index < (num_sat + num_gw):  # 是gw
        src = "G{}".format(src_index + 1 - num_sat)
    elif src_index == (num_sat + num_gw):
        src = "GA"
    else:
        src = "GB"

    if dst_index < num_sat:  # 是卫星
        dst = "S{}".format(dst_index + 1)
    elif dst_index < (num_sat + num_gw):
        dst = "G{}".format(dst_index + 1 - num_sat)
    elif dst_index == (num_sat + num_gw):
        dst = "GA"
    else:
        dst = "GB"

    if src_index < dst_index:
        pair_tuple = (src, dst)
    else:
        pair_tuple = (dst, src)

    return edges.index(pair_tuple)


def get_edges(adjacency_matrix, in_t):
    edges = []
    num_vertices = len(adjacency_matrix)
    num_sat = in_t.num_sat
    num_gw = in_t.num_gw
    num_gs = 2

    for i in range(num_vertices):
        for j in range(i + 1, num_vertices):
            if adjacency_matrix[i][j] == 1:
                if i < num_sat:
                    src = 'S{}'.format(i + 1)
                elif i < (num_sat + num_gw):
                    src = 'G{}'.format(i + 1 - num_sat)
                elif i == (num_sat + num_gw):
                    src = 'GA'
                else:
                    src = 'GB'

                if j < num_sat:
                    dst = 'S{}'.format(j + 1)
                elif j < (num_sat + num_gw):
                    dst = 'G{}'.format(j + 1 - num_sat)
                elif j == (num_sat + num_gw):
                    dst = 'GA'
                else:
                    dst = 'GB'

                edges.append((src, dst))

    return edges


def find_used_link(edges, lst, src, dst, t, lr, con_name):
    directory = "./Kuiper_{}/UsedLink{}".format(con_name, lr)
    if not os.path.exists(directory):
        os.makedirs(directory)
    ul_file = open(directory + "/" + "used_link_{}.txt".format(t), "a")
    for i in range(len(lst)):
        if lst[i] == 1:
            if edges[i][0] == "GA" or edges[i][0] == "GB" or edges[i][1] == "GA" or edges[i][1] == "GB":
                tuple_str_to_add = str(edges[i])
                tuple_str_to_add = tuple_str_to_add.replace("GA", src)
                tuple_str_to_add = tuple_str_to_add.replace("GB", dst)
            else:
                tuple_str_to_add = str(edges[i])

            ul_file.write(tuple_str_to_add)
    ul_file.write("\n")
    ul_file.close()


def split_list(lst, chunk_size):
    return [lst[i:i+chunk_size] for i in range(0, len(lst), chunk_size)]