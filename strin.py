import numpy as np
str1 = np.array("1 4 5 2 7 3".split())
str2 = str1.reshape((3,2))
str2[1:] = np.zeros((2,2))
print(str1, str2)