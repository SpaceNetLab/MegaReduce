# MegaReduce

MegaReduce is a project investigating an important research problem facing the upcoming satellite Internet: from a network perspective, how many satellites exactly do we need to construct a survivable and performant LSN? 

To answer this question, MegaReduce first formulates the survivable and performant LSN design (SPLD) problem, which aims to find the minimum number of needed satellites to construct an LSN that can provide sufficient amount of redundant paths, required link capacity and acceptable latency for traffic carried by the LSN. Second, to efficiently solve the tricky SPLD problem, MegaReduce exploits a requirement-driven constellation optimization mechanism, which can calculate feasible solutions for SPLD in polynomial time. 

This repo contains the source codes of MegaReduce and examples to demonstrate its usage on optimizing the the incremental deployment and long-term maintenance of future satellite Internet.

## Working principle

This project can achieve automatic reduction of constellation size and avoid NP-hard problem.

Given the initial configuration of a constellation, the constellation size is optimized after being checked for survivability and performance requirements

![Working Principle of MegaReduce](./figures/figure1.png)
## Code Introduction
The working environment needs to use python 3 version, you just need`python3 MR_demo.py` to run this code.

### Each file's function
- `Topo.py` and `Constellation_model.py` describe how communication take place in satellite networks and generate the data structure of the graph.
- `utils.py` provide Coordinate transformation, graph algorithm and methods for finding disjoint paths.
- `gw_amazon.txt` and `gw_starlink.txt` describe the location of ground stations of each satellite network.

### how to use demo?

1. Specify the initial constellation configuration
    assign `init_con`,each item in list means [Shell number, altitude, orbital inclination, number of orbits, number of satellites per orbit] respectively.
2. Specify delay constraints `lr`,which means The hop count of the optional path should be less than the value multiplied by the shortest hop count.
3. Select the geographical location of the communication point, which you can specify in `gs`. Make them evenly distributed across the globe.
4. Specify the Survivability requirement in `K_T`,which means the disjoint path between any two communication pairs should not be less than this value.
5. Design expansion and reduction strategies for constellations in function `con_expand` and `con_expand`.
   We use the method described in paper by default.
6. In order not to take too long, we set the number of iterations to no more than ten. 
    `` if (shrink_count + expand_count) > 10 and ret`` as condition for the end of the program.
7. The iteration is shown in `con_log.txt` .