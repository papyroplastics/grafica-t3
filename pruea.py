import numpy as np

a = [None]
arr = np.array([1,2,4])
a += [[np.array(arr),np.array(arr)]]
a[1][1] += np.array([1,5,2])

print(a)