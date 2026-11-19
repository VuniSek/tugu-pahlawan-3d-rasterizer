from objio import load_obj
from ppm_io import read_ppm
from raster3d import render
from transforms import rot_y, scale
m = load_obj("data/tugu_pahlawan.obj")
tex = read_ppm("data/tugu_atlas.ppm")
M = rot_y(35) @ scale((1.4, 1.4, 1.4))
for cb in (False, True):
    _, _, filled = render(m, w=512, h=512, tex_u8=tex, model=M, center=(0, 1.4, 0), cull_back=cb)
    print("cull_back =", cb, " fragment terisi:", filled)