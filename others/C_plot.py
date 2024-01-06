import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

ret = np.loadtxt("C4_result.csv", delimiter=',', dtype=int)
print(ret)

altitude_list = np.array([600, 700, 800, 900, 1000])
incline_list = np.array([55, 60, 65, 70, 75])
X, Y = np.meshgrid(incline_list, altitude_list)

print(X)
print(Y)

fig = plt.figure()
ax1 = plt.axes(projection='3d')
ax1.set_xlabel('Inclination')
ax1.set_ylabel('Altitude')
ax1.set_zlabel('#Satellites')
ax1.set_zlim(500, 2500)
ax1.plot_surface(X, Y, ret, cmap='viridis')
# plt.title("Satellites with different inclination and altitude")
ax1.view_init(25, 20)
plt.show()
