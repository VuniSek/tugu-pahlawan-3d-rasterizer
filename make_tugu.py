import numpy as np
from PIL import Image

with open("assets/Tugu_Pahlawan.obj") as f, open("data/tugu_pahlawan.obj", "w") as g:
    for line in f:
        if line.startswith("v "):
            x, y, z = map(float, line.split()[1:4])
            line = f"v {x*0.05:.6f} {y*0.05:.6f} {z*0.05:.6f}\n"
        g.write(line)

rng = np.random.default_rng(1)
img = np.zeros((256, 256, 3), np.uint8)
img[:, :85] = (0, 110, 70)                                   # alas hijau
noise = rng.integers(-12, 12, (256, 85, 1))
img[:, 85:170] = np.clip(np.array([235, 235, 230]) + noise, 0, 255)  # tiang+puncak putih
img[:, 170:] = (212, 175, 55)                                # pita emas
Image.fromarray(img).save("data/tugu_atlas.ppm")