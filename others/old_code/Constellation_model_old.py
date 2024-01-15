from utils import *


class Satellite:
    def __init__(self, name, angle_asc_node):
        self.name = name
        self.angle_asc_node = angle_asc_node
        self.cartesian_coordination = None  # 笛卡尔坐标系下的卫星位置
        self.front_neighbour = None  # front/behind 邻居在轨道构造完毕之后就可以构建，并且在之后的过程中不会发生改变
        self.behind_neighbour = None
        self.left_neighbour = None  # 并不严格表示左右邻居，左邻居的意思是轨道号小的那个轨道上最近的卫星，右邻居的意思是轨道号大的那个轨道上最近的卫星
        self.right_neighbour = None


class EarthOrbit:
    EARTH_MASS = 5.972e24  # Earth's mass in kilograms

    def __init__(self, orbit_name, altitude, inclination, raan, init_offset,
                 num_of_sat, t):  # init_offset指的是相对于升交点的偏移，也就是phase diff
        self.orbit_name = orbit_name
        self.altitude = altitude  # 单位是km
        self.inclination = inclination
        self.raan = raan
        self.init_offset = init_offset
        self.num_of_sat = num_of_sat
        self.a_speed = self.calculate_angular_speed()  # 角速度单位是 rad/s 按照度数算，需要换算，此值大小需要再乘以 180/pi
        self.t = t
        self.satellites = []
        self.add_satellite()
        self.coordinate()  # 计算每个卫星的笛卡尔坐标
        self.front_behind_neighbour_link()  # 一个轨道上所有的卫星建立完之后，就可以在这条轨道上寻找上下邻居,这个步骤是一次性且永久的

    def add_satellite(self):  # 初始化 构造一个轨道上的所有卫星
        sat_degree_interval = 360 / self.num_of_sat
        for i in range(self.num_of_sat):
            degree = (self.init_offset + i * sat_degree_interval + self.t * self.a_speed * 180 / math.pi) % 360
            sat = Satellite("{}_{}".format(self.orbit_name, i), degree)
            self.satellites.append(sat)

    def calculate_angular_speed(self):
        earth_radius = 6371  # Radius of the Earth in kilometers
        orbit_radius = (earth_radius + self.altitude) * 1000  # 以米为单位的轨道半径
        gravitational_constant = 6.67430e-11  # Gravitational constant in m^3/(kg*s^2)
        satellite_speed = math.sqrt(gravitational_constant * EarthOrbit.EARTH_MASS / orbit_radius)
        angular_speed = satellite_speed / orbit_radius
        return angular_speed

    def front_behind_neighbour_link(self):
        for i in range(self.num_of_sat):
            front_index = (i + 1) % self.num_of_sat
            behind_index = (i - 1) % self.num_of_sat
            self.satellites[i].front_neighbour = self.satellites[front_index].name
            self.satellites[i].behind_neighbour = self.satellites[behind_index].name

    def coordinate(self):  # 根据轨道信息和卫星的位置，计算出每个卫星的笛卡尔坐标系中的坐标
        for i in self.satellites:
            cart_coord = calculate_cartesian_coordinates(self.altitude, self.inclination, self.raan, i.angle_asc_node)
            i.cartesian_coordination = cart_coord

    def find_nearest(self, coordinate):  # 给定一个坐标，找到该轨道上，离该坐标最近的卫星索引
        min_dist = 5e10
        nearest_sat_index = -1
        for i in range(self.num_of_sat):
            dist = calculate_distance(self.satellites[i].cartesian_coordination, coordinate)
            if dist < min_dist:
                min_dist = dist
                nearest_sat_index = i
        return nearest_sat_index  # 返回该轨道最近卫星的索引


class Shell:
    def __init__(self, shell_id, altitude, inclination, num_of_orbit, num_of_sat_per_orbit, t):
        self.shell_id = shell_id
        self.altitude = altitude
        self.inclination = inclination
        self.num_of_orbit = num_of_orbit
        self.num_of_sat_per_orbit = num_of_sat_per_orbit
        self.t = t
        self.orbits = []
        self.add_orbit()
        self.left_right_neighbour_link()  # 这一步需要找到每个卫星的左右邻居,到此为止，整个星座的初始化就完成了

    def add_orbit(self):  # 这一步构建了星座的各条轨道，下层函数构造了各个轨道内的卫星分布，计算出每个卫星的笛卡尔坐标，找到每个卫星的上下邻居
        raan_degree_interval = 360 / self.num_of_orbit
        for i in range(self.num_of_orbit):
            orbit = EarthOrbit("{}_{}".format(self.shell_id, i), self.altitude, self.inclination,
                               i * raan_degree_interval, 0,
                               self.num_of_sat_per_orbit, self.t)
            self.orbits.append(orbit)

    def left_right_neighbour_link(self):
        for i in range(self.num_of_orbit):
            left_orbit_index = (i - 1) % self.num_of_orbit
            neighbour_selected = set()
            for j in range(self.num_of_sat_per_orbit):  # 定位到每一颗卫星
                src_sat = self.orbits[i].satellites[j]
                # 为了防止 违背互为邻居这一原则，只找左邻居,一个方向地去找
                # 在左轨道寻找邻居
                left_neighbour_index = self.orbits[left_orbit_index].find_nearest(src_sat.cartesian_coordination)

                if left_neighbour_index not in neighbour_selected:  # 如果自己最近的邻居被占用了，那只能先到先得了，这里或许存在一些问题，等以后再改吧
                    neighbour_selected.add(left_neighbour_index)
                    src_sat.left_neighbour = self.orbits[left_orbit_index].satellites[left_neighbour_index].name
                    self.orbits[left_orbit_index].satellites[left_neighbour_index].right_neighbour = src_sat.name

    def output_shell(self):
        # 将星座输出，输出样式为字典，key为卫星名称，value为邻居和自己的笛卡尔坐标      sat:[[front,behind,left,right,up,down],(x,y,z)]
        shell_topo_dict = dict()
        shell_pos_dict = dict()
        for i in range(self.num_of_orbit):
            for j in range(self.num_of_sat_per_orbit):  # 定位到每一颗卫星
                sat = self.orbits[i].satellites[j]
                front_neighbour = sat.front_neighbour
                behind_neighbour = sat.behind_neighbour
                left_neighbour = sat.left_neighbour
                right_neighbour = sat.right_neighbour
                cart_coord = sat.cartesian_coordination
                shell_topo_dict[sat.name] = [front_neighbour, behind_neighbour, left_neighbour, right_neighbour]
                shell_pos_dict[sat.name] = cart_coord

        return shell_topo_dict, shell_pos_dict


class Constellation:
    def __init__(self, info_array, t):
        # info_array的每个元素是一个tuple，（shell_id,altitude(km),inclination,#orbits,#sats per orbit）
        self.t = t
        self.shells = []
        for info in info_array:
            self.shells.append(Shell(info[0], info[1], info[2], info[3], info[4], t))

    def constellation_topo(self):
        constellation_topo_dict = dict()
        constellation_pos_dict = dict()
        for shell in self.shells:
            std, spd = shell.output_shell()
            constellation_topo_dict.update(std)
            constellation_pos_dict.update(spd)

        nodes = list(constellation_topo_dict.keys())
        num_nodes = len(nodes)
        adjacent_matrix = np.zeros((num_nodes, num_nodes), int)
        for node, neighbors in constellation_topo_dict.items():
            row_index = nodes.index(node)
            for neighbor in neighbors:
                if neighbor is not None:
                    col_index = nodes.index(neighbor)
                    adjacent_matrix[row_index][col_index] = 1
                    adjacent_matrix[col_index][row_index] = 1

        return constellation_pos_dict, adjacent_matrix, nodes
