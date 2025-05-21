from gurobipy import * 
import numpy as np
import pandas as pd
import time

orbit = 72
sat_of_orbit = 22
num_of_sat = orbit*sat_of_orbit
num_of_user = 10000
cycle = 10
factors = []
user_paths = []
t0 = time.time()
for t in range(cycle):
    factor = np.loadtxt('factor/sat_t%d.csv'%(t), delimiter=',')
    factors.append(factor)
    user_path = np.load('factor/user_t%d.npy'%(t), allow_pickle=True)
    user_paths.append(user_path)
factors = np.array(factors)
user_paths = np.array(user_paths)
print('read data:',time.time()-t0)
t0 = time.time()
model = Model("MyModel")

power = model.addVars(cycle,num_of_sat,4,5, vtype=GRB.BINARY, name="power_level")
charge = model.addVars(cycle,num_of_sat, lb=0, ub=300, vtype=GRB.INTEGER, name='charge')
discharge = model.addVars(cycle,num_of_sat, lb=0, ub=600, vtype=GRB.INTEGER, name='discharge')
bandwidth = model.addVars(cycle,num_of_user, lb=0, vtype=GRB.CONTINUOUS, name='bandwidth')

model.update()

print('add vars:', time.time()-t0)
t0 = time.time()
model.setObjective(quicksum(bandwidth), GRB.MAXIMIZE)  
cap = [0,1.25,2.5,5,10]
p = [4, 40, 50, 80, 150]
for t in range(cycle):
    for i in range(num_of_sat):
        GSL = factors[t,i,4]
        total_power = LinExpr(GSL*100+(1-GSL)*10+100)
        for j in range(4):
            model.addConstr(quicksum(power[t,i,j,k] for k in range(5)) == 1) # only one power level
            total_power.add(quicksum(p[k]*power[t,i,j,k] for k in range(5)))
        # power constraint
        if factors[t,i,5]:
            model.addConstr(discharge[t,i]==0)
            total_power.add(charge[t,i])
            model.addConstr(total_power<=660)
        else:
            model.addConstr(charge[t,i]==0)
            model.addConstr(total_power<=discharge[t,i])
for t in range(cycle):
    for i in range(num_of_user):
        path = user_paths[t,i]
        for j in range(len(path)):
            sat = path[j][0]
            ISL = path[j][1]
            model.addConstr(bandwidth[t,i]<=factors[t,sat,ISL]*quicksum(cap[k]*power[t,sat,ISL,k]for k in range(5)))

battery_vol = 14400
for i in range(num_of_sat):
    eclipse_start = 0
    if factors[0,i,5]==1:
        k = 1
        while(k<cycle and factors[k,i,5]==1): k+=1
        eclipse_start = k
    while(eclipse_start<cycle):
        k = eclipse_start+1
        while(k<cycle and factors[k,i,5]==0): k+=1
        sunlight_start = k
        energy_consumption = quicksum(discharge[t,i] for t in range(eclipse_start, sunlight_start))
        model.addConstr(energy_consumption<=battery_vol)
        if sunlight_start==cycle:
            break
        else:
            k = sunlight_start+1
            while(k<cycle and factors[k,i,5]==1): k+=1
            eclipse_start = k
            if eclipse_start==cycle:
                for t in range(sunlight_start,cycle):
                    model.addConstr(charge[t,i]==300)
            else:
                model.addConstr(energy_consumption==quicksum(quicksum(charge[t,i] for t in range(sunlight_start,eclipse_start))))
print('add constraint:',time.time()-t0)

t0 = time.time()
model.optimize() 

print('optimize:',time.time()-t0)