python raster3d.py --model data/tugu_pahlawan.obj --w 512 --h 512
model: 560 triangles   framebuffer 512x512
filled fragments: 16717   depth(ndc) range [0.622, 0.686]
wrote out/temple_raster.ppm and out/temple_depth.ppm

python raytrace.py --model data/tugu_pahlawan.obj --w 512 --h 512 --out out/tugu_rt.ppm
model: 560 triangles   512x512   pixels hit: 14953/262144
wrote out/tugu_rt.ppm

python compare.py out/temple_raster.ppm out/tugu_rt.ppm --diff out/diff_rt.ppm
same size 512x512   PSNR: inf dB   SSIM: 1.000   mean |diff|: 0.0   max |diff|: 0
wrote out/diff_rt.ppm (|A-B| x6)

python tests.py
OK   E1  running point (2,3,4) -> (3,3,-3); divide d=2 -> (2,2); order matters
OK   E2  camera +x == model -x (identical points)
OK   E3  perspective: z=-n -> ndc -1 ; z=-f -> ndc +1 ; z=-3 -> 0.5
OK   E4  perspective-correct u at screen centre = 0.1 (naive 0.5)
OK   E5  barycentric depth 0.20/0.50/0.90 at (.25,.25,.5) = 0.625
OK   projection pipeline shapes + viewport
OK   one-triangle z-buffer render fills a plausible region, flat depth
OK   temple frame matches ref/temple_ref.ppm (byte-identical on re-render)

ALL CHECKS PASSED