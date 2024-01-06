from Constellation_model import *
from utils import *


# Heaven and earth fusion network, a time of constellations + all stations
class IntegratedNetwork:
    def __init__(self, constellation, gw_file_path, t):
        self.t = t
        self.constellation = Constellation(constellation, self.t)
        self.gw_file_path = gw_file_path
        self.num_gw = 0
        self.cpd, self.c_matrix, self.sat_lst = self.constellation.constellation_topo()
        self.num_sat = len(self.c_matrix)
        self.in_matrix = self.in_topo()

    def in_topo(self):
        gw_dict = self.read_gw_file()
        self.num_gw = len(gw_dict)
        in_topology = matrix_expand(self.c_matrix, gw_dict, self.cpd, self.t)

        return in_topology

    def fin_topo(self, src, dst, cp_pos_dict):
        cp_dict = dict()
        cp_dict[src] = cp_pos_dict[src]
        cp_dict[dst] = cp_pos_dict[dst]  # Get latitude and longitude

        fin_topology, k_max = matrix_expand(self.in_matrix, cp_dict, self.cpd, self.t)
        return fin_topology, k_max

    def read_gw_file(self):
        gw_file = open(self.gw_file_path, "r")
        line = gw_file.readline()
        gw_dict = dict()
        while line:
            line_stripe = line.strip()
            gw, gw_longitude, gw_latitude = line_stripe.split(" ")
            gw_dict[gw] = (float(gw_longitude.strip()), float(gw_latitude.strip()))
            line = gw_file.readline()
        gw_file.close()

        return gw_dict
