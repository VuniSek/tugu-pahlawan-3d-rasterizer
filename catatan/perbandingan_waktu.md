time python raster3d.py --model data/tugu_pahlawan.obj --w 256 --h 256 --out out/r256.ppm
model: 560 triangles   framebuffer 256x256
filled fragments: 3754   depth(ndc) range [0.603, 0.700]
wrote out/r256.ppm and out/r256.ppm

real    0m0.751s
user    0m0.658s
sys     0m0.068s


time python raytrace.py --model data/tugu_pahlawan.obj --w 256 --h 256 --out out/t256.ppm
model: 560 triangles   256x256   pixels hit: 3346/65536
wrote out/t256.ppm

real    0m4.638s
user    0m4.289s
sys     0m0.244s

python cull_test.py
cull_back = False  fragment terisi: 16717
cull_back = True  fragment terisi: 15035