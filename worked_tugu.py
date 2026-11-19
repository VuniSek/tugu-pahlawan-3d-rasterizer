import numpy as np
from transforms import rot_y, scale, look_at, perspective, viewport
np.set_printoptions(precision=6, suppress=True)

p = np.array([4.9 * 0.05, 0.0, 0.0, 1.0])
M = rot_y(35) @ scale((1.4, 1.4, 1.4))
V = look_at((2.6, 2.0, 3.4), (0, 1.4, 0))
P = perspective(45, 1, 1.0, 14.0)

w = M @ p; e = V @ w; c = P @ e; ndc = c[:3] / c[3]
s = viewport(ndc[None, :], 512, 512)[0]
print("object p     =", p)
print("world  M p   =", w)
print("eye    V(Mp) =", e)
print("clip   P e   =", c)
print("ndc          =", ndc)
print("screen       =", s)