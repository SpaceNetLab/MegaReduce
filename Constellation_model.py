from utils import *

"""
This document describes constellations, from satellites to satellite orbits, to single-layer constellations, and then to the entire constellation
"""


class Satellite:
    def __init__(self, name, angle_asc_node):
        self.name = name
        self.angle_asc_node = angle_asc_node
        self.cartesian_coordination = None
        self.front_neighbour = None  # front/behind neighbors can be constructed after the track is constructed, and will not change during the subsequent process
        self.behind_neighbour = None
        self.left_neighbour = None  # It's not strictly the right or left neighbor, the left neighbor is the nearest satellite in the orbit with the smaller orbital number, and the right neighbor is the nearest satellite in the orbit with the larger orbital number
        self.right_neighbour = None


# The satellites are evenly distributed in orbit
class EarthOrbit:
    EARTH_MASS = 5.972e24  # Earth's mass in kilograms

    def __init__(self, orbit_name, altitude, inclination, raan, init_offset,
                 num_of_sat, t):
        self.orbit_name = orbit_name
        self.altitude = altitude  # km
        self.inclination = inclination
        self.raan = raan
        self.init_offset = init_offset
        self.num_of_sat = num_of_sat
        self.a_speed = self.calculate_angular_speed()
        self.t = t
        self.satellites = []
        self.add_satellite()
        self.coordinate()  # Calculate the Cartesian coordinates for each satellite
        self.front_behind_neighbour_link()  # After all the satellites in an orbit are established, they can look for neighbors in this orbit, which is a one-time and permanent step

    def add_satellite(self):  # Initialization, construction of all satellites in an orbit
        sat_degree_interval = 360 / self.num_of_sat
        for i in range(self.num_of_sat):
            degree = (self.init_offset + i * sat_degree_interval + self.t * self.a_speed * 180 / math.pi) % 360
            sat = Satellite("{}_{}".format(self.orbit_name, i), degree)
            self.satellites.append(sat)

    def calculate_angular_speed(self):
        earth_radius = 6371  # Radius of the Earth in kilometers
        orbit_radius = (earth_radius + self.altitude) * 1000
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

    # Based on the orbital information and the position of the satellites, the coordinates in the Cartesian coordinate system of each satellite are calculated
    def coordinate(self):
        for i in self.satellites:
            cart_coord = calculate_cartesian_coordinates(self.altitude, self.inclination, self.raan, i.angle_asc_node)
            i.cartesian_coordination = cart_coord

    # Given a coordinate, find the index of the satellite closest to that coordinate in that orbit
    def find_nearest(self, coordinate):
        min_dist = 5e10
        nearest_sat_index = -1
        for i in range(self.num_of_sat):
            dist = calculate_distance(self.satellites[i].cartesian_coordination, coordinate)
            if dist < min_dist:
                min_dist = dist
                nearest_sat_index = i
        return nearest_sat_index  # Returns an index of the nearest satellites in that orbit


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
        self.left_right_neighbour_link()  # This step requires finding the left and right neighbors of each satellite, and from there, the initialization of the entire constellation is complete

    def add_orbit(
            self):  # This step constructs the orbits of the constellation, the lower function constructs the distribution of satellites within each orbit, calculates the Cartesian coordinates of each satellite, and finds the upper and lower neighbors of each satellite
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
            for j in range(self.num_of_sat_per_orbit):
                src_sat = self.orbits[i].satellites[j]
                left_neighbour_index = self.orbits[left_orbit_index].find_nearest(src_sat.cartesian_coordination)

                if left_neighbour_index not in neighbour_selected:
                    neighbour_selected.add(left_neighbour_index)
                    src_sat.left_neighbour = self.orbits[left_orbit_index].satellites[left_neighbour_index].name
                    self.orbits[left_orbit_index].satellites[left_neighbour_index].right_neighbour = src_sat.name

    def output_shell(self):
        # sat:[[front,behind,left,right,up,down],(x,y,z)]
        shell_topo_dict = dict()
        shell_pos_dict = dict()
        for i in range(self.num_of_orbit):
            for j in range(self.num_of_sat_per_orbit):
                sat = self.orbits[i].satellites[j]
                front_neighbour = sat.front_neighbour
                behind_neighbour = sat.behind_neighbour
                left_neighbour = sat.left_neighbour
                right_neighbour = sat.right_neighbour
                cart_coord = sat.cartesian_coordination
                shell_topo_dict[sat.name] = [front_neighbour, behind_neighbour, left_neighbour, right_neighbour]
                shell_pos_dict[sat.name] = cart_coord

        return shell_topo_dict, shell_pos_dict


"""
 Constellation object, using +grid configuration 
"""


class Constellation:
    def __init__(self, info_array, t):
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

        # ----------------------------------------------
        # If you need to show stochastic_down being in a cosmic environment, then call this stochastic_down function, randomly destroy the link, and the destruction rate can be adjusted
        # damage_rate = 0.2
        # stochastic_down(adjacent_matrix, damage_rate)
        # ------------------------------------------------------

        # --------------------------------
        # Simulate partial total damage, which can be caused by a solar storm or an attack from the ground(A pyramid with an apex Angle of ten degrees by default)
        # core_attacked = (10, 10) # Specifies the latitude and longitude of the vertex of the cone
        # sun_storm_emulation(adjacent_matrix, constellation_pos_dict, core_attack, self.t)
        # --------------------------------

        return constellation_pos_dict, adjacent_matrix, nodes
