import numpy as np
M=np.arange(2,27)
print(M)
M=M.reshape(5,5)
print(M)
M[1:4,1:4]=0
print(M)
M=M@M
print(M)
print(np.sqrt(M[0]@M[0]))
