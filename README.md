# MegaReduce

MegaReduce is a project investigating an important research problem facing the upcoming satellite Internet: from a network perspective, how many satellites exactly do we need to construct a survivable and performant LSN? 

To answer this question, MegaReduce first formulates the survivable and performant LSN design (SPLD) problem, which aims to find the minimum number of needed satellites to construct an LSN that can provide sufficient amount of redundant paths, required link capacity and acceptable latency for traffic carried by the LSN. Second, to efficiently solve the tricky SPLD problem, MegaReduce exploits a requirement-driven constellation optimization mechanism, which can calculate feasible solutions for SPLD in polynomial time. 

This repo contains the source codes of MegaReduce and examples to demonstrate its usage on optimizing the the incremental deployment and long-term maintenance of future satellite Internet.