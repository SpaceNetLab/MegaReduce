from Constellation_model import *
from utils import *
import json


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
        gw_dict = dict()
        with open('./gw_amazon.json', 'r') as json_file:
            locations_data = json.load(json_file)
            for gw, location in locations_data.items():
                gw_dict[gw] = (float(location['longitude']), float(location['latitude']))

        return gw_dict
