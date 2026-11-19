python make_model.py
wrote data/pusaka_model.obj  (120 verts, 180 triangles)
wrote data/relief.ppm  (256x256, 196623 bytes)

Test(1)
python tests.py
OK   E1  running point (2,3,4) -> (3,3,-3); divide d=2 -> (2,2); order matters
OK   E2  camera +x == model -x (identical points)
OK   E3  perspective: z=-n -> ndc -1 ; z=-f -> ndc +1 ; z=-3 -> 0.5
OK   E4  perspective-correct u at screen centre = 0.1 (naive 0.5)
OK   E5  barycentric depth 0.20/0.50/0.90 at (.25,.25,.5) = 0.625
OK   projection pipeline shapes + viewport
OK   one-triangle z-buffer render fills a plausible region, flat depth
     (ref/temple_ref.ppm generated -- commit it)
OK   temple frame matches ref/temple_ref.ppm (byte-identical on re-render)

ALL CHECKS PASSED

Test(2)
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

python worked_example.py
object p        = [2. 3. 4. 1.]
model  M = Ry(90) . T(1,0,-1)        ; world  = M p       = [ 3.  3. -3.  1.]
view   V = lookAt(eye=[0,0,8], ctr=0); eye    = V world   = [  3.   3. -11.   1.]   (z=-11: in front, dist 11)
proj   P = perspective(60deg, 1, 1, 50)
clip            = P eye              = [ 5.196  5.196  9.408 11.   ]
ndc  = clip/clip.w                   = [0.472 0.472 0.855]
screen (800x600) = [589 158]  depth 0.928

--- Example E1 cross-check (bare similar-triangles projection) ---
world point (pre-view) = [ 3.  3. -3.]   -> after Ry(90) of (3,3,3): (3,3,-3)
perspective divide d=2 of (3,3,-3)   = [2. 2.]   (expected [2. 2.])

python raster3d.py --model data/pusaka_model.obj --w 512 --h 512
model: 180 triangles   framebuffer 512x512
filled fragments: 276078   depth(ndc) range [0.468, 0.729]
wrote out/temple_raster.ppm and out/temple_depth.ppm

python raytrace.py --model data/pusaka_model.obj --w 256 --h 256
model: 180 triangles   256x256   pixels hit: 33842/65536
wrote out/temple_rt.ppm

python compare.py out/temple_raster.ppm out/temple_rt.ppm
size mismatch: (512, 512, 3) vs (256, 256, 3) -- render both at the same w/h and setPixelRatio(1)