import numpy as np

pos1 = np.array([0,1,5], dtype=np.float32)
dir1 = np.array([0.1, 0.5, 0.2], dtype=np.float32)
pos2 = np.array([1,6,6], dtype=np.float32)
dir2 = np.array([0.4,0.5,0.1], dtype=np.float32)
stack = np.vstack([pos1, dir1, pos2, dir2])

hermite_matrix = np.array([[ 2,-2, 1, 1],
                           [-3, 3,-2,-1],
                           [ 0, 0, 1, 0],
                           [ 1, 0, 0, 0]])

t = 0.364
t_arr = np.array([t**3, t**2, t, 1], dtype=np.float32)

ctrl_points = []
ctrl_points.append([np.array(pos1),dir1])

print(ctrl_points)

pos1 += dir2

print(ctrl_points)

ctrl_points.append([pos2,dir2])
print()