"""Tahap 6 -- eksperimen A5 (UV perspective-correct vs naif, mipmap) dan A3 (histogram depth z-fighting).

Jalankan dari folder Module3/ (setelah `python make_model.py`):
    python tahap6.py

Tidak mengubah raster3d.py. Varian renderer dibuat dengan menyalin sumber
raster3d.render() lalu mengganti SATU hal saja (cara interpolasi UV atau cara
sampling texture), jadi selisih hasilnya murni berasal dari hal itu.
Keluaran: out/tahap6_*.png dan angka di terminal.
"""
from __future__ import annotations

import inspect
import os

import numpy as np
from PIL import Image, ImageDraw

import raster3d
from objio import load_obj, Mesh
from ppm_io import read_ppm
from srgb import srgb_to_linear, linear_to_srgb
from metrics import psnr, ssim
from transforms import rot_y, scale
import broken_scene as bs

os.makedirs("out", exist_ok=True)
MIP_LEVELS = 4          # modul meminta piramida 4 level; coba 8 untuk melihat efeknya


def save(name, arr):
    Image.fromarray(np.asarray(arr, np.uint8)).save(f"out/{name}.png")
    print("  tulis out/%s.png" % name)


def variant(replacements, hooks=None):
    """Salin raster3d.render, ganti potongan kode tertentu, kembalikan fungsi baru."""
    src = inspect.getsource(raster3d.render)
    for old, new in replacements:
        assert old in src, "potongan kode tidak ditemukan: " + old
        src = src.replace(old, new)
    ns = dict(raster3d.__dict__)
    ns.update(hooks or {})
    exec(src, ns)
    return ns["render"]


# ======================================================================
# A5-1  UV perspective-correct vs naif (contoh E4 dan lantai bertexture)
# ======================================================================
def bagian_e4():
    print("\n[A5-1] Contoh E4: u di tengah layar, wL=1, wR=9")
    wl, wr = 1.0, 9.0
    naif = 0.5 * 0.0 + 0.5 * 1.0
    u_per_w = 0.5 * (0.0 / wl) + 0.5 * (1.0 / wr)
    satu_per_w = 0.5 * (1.0 / wl) + 0.5 * (1.0 / wr)
    print("  naif            u = %.3f" % naif)
    print("  perspective-correct u = (u/w) / (1/w) = %.4f / %.4f = %.3f"
          % (u_per_w, satu_per_w, u_per_w / satu_per_w))


def bagian_lantai():
    print("\n[A5-1] Lantai bertexture: perspective-correct vs naif (texture berenang)")
    # texture papan catur 64x64 (8x8 kotak, kotak 8 px)
    yy, xx = np.mgrid[0:64, 0:64]
    cek = ((yy // 8 + xx // 8) % 2).astype(bool)
    tex = np.where(cek[..., None], np.array([235, 235, 235]), np.array([40, 60, 140])).astype(np.uint8)

    pos = [[-6, 0, -1], [6, 0, -1], [6, 0, -40], [-6, 0, -40]]
    uvs = [[0, 0], [3, 0], [3, 9.75], [0, 9.75]]
    faces = [[0, 1, 2], [0, 2, 3]]
    mesh = Mesh(pos, uvs, faces, faces)
    cam = dict(eye=(0, 1.5, 2.0), center=(0, 1.0, -10.0), fovy=60.0, near=0.5, far=100.0)

    render_naif = variant([
        ("u_i = (l0 * uvw[0, 0] + l1 * uvw[1, 0] + l2 * uvw[2, 0]) / inv_w_i",
         "u_i = l0 * cattr[0, 0] + l1 * cattr[1, 0] + l2 * cattr[2, 0]"),
        ("v_i = (l0 * uvw[0, 1] + l1 * uvw[1, 1] + l2 * uvw[2, 1]) / inv_w_i",
         "v_i = l0 * cattr[0, 1] + l1 * cattr[1, 1] + l2 * cattr[2, 1]"),
    ])
    benar, _, _ = raster3d.render(mesh, w=256, h=256, tex_u8=tex, **cam)
    naif, _, _ = render_naif(mesh, w=256, h=256, tex_u8=tex, **cam)
    beda = np.abs(benar.astype(int) - naif.astype(int)).max(2) > 60
    print("  pixel yang berbeda jauh (>60 level): %d dari %d (%.1f%%)"
          % (beda.sum(), beda.size, 100.0 * beda.mean()))
    print("  PSNR(naif, benar) = %.1f dB   SSIM = %.3f" % (psnr(naif, benar), ssim(naif, benar)))
    save("tahap6_lantai_perspective_correct", benar)
    save("tahap6_lantai_naif", naif)
    save("tahap6_lantai_berdampingan", np.hstack([benar, naif]))


# ======================================================================
# A5-2  Mipmap 4 level (box downscale di cahaya linear) pada candi dari jauh
# ======================================================================
def bangun_mip(tex_u8, levels=4):
    lin = srgb_to_linear(tex_u8.astype(np.float64) / 255.0)
    pyr = [lin]
    for _ in range(levels - 1):
        a = pyr[-1]
        h, w = a.shape[:2]
        pyr.append(a.reshape(h // 2, 2, w // 2, 2, 3).mean(axis=(1, 3)))
    return pyr


def buat_hook_mip(pyr):
    n0 = pyr[0].shape[0]

    def hook(tex_lin, u, v, cattr, sx, sy):
        # LOD per segitiga: rasio luas texel (di texture) terhadap luas pixel (di layar)
        uv = cattr[:, :2]
        luas_tex = 0.5 * abs((uv[1, 0] - uv[0, 0]) * (uv[2, 1] - uv[0, 1])
                             - (uv[1, 1] - uv[0, 1]) * (uv[2, 0] - uv[0, 0])) * n0 * n0
        luas_pix = 0.5 * abs((sx[1] - sx[0]) * (sy[2] - sy[0]) - (sy[1] - sy[0]) * (sx[2] - sx[0]))
        rasio = max(luas_tex / max(luas_pix, 1e-9), 1.0)
        lod = min(0.5 * np.log2(rasio), len(pyr) - 1)
        l0 = int(np.floor(lod)); l1 = min(l0 + 1, len(pyr) - 1); f = lod - l0
        a = raster3d.sample_bilinear(pyr[l0], u, v)
        b = raster3d.sample_bilinear(pyr[l1], u, v)
        return a * (1 - f) + b * f          # trilinear

    return hook


def energi_hf(img, mask):
    """Energi frekuensi tinggi = rata-rata (Laplacian)^2 pada luminans, di dalam mask."""
    g = img.astype(np.float64) @ np.array([0.299, 0.587, 0.114])
    lap = 4 * g[1:-1, 1:-1] - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]
    m = mask[1:-1, 1:-1]
    return float((lap[m] ** 2).mean())


def erosi(mask):
    m = mask.copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            m &= np.roll(np.roll(mask, dy, 0), dx, 1)
    return m


def bagian_mipmap():
    print("\n[A5-2] Mipmap: candi bawaan dari jauh (texture relief.ppm)")
    mesh = load_obj("data/pusaka_model.obj")
    tex = read_ppm("data/relief.ppm")
    pyr = bangun_mip(tex, MIP_LEVELS)
    print("  piramida mip:", [p.shape[0] for p in pyr], "(ukuran sisi tiap level)")
    render_mip = variant(
        [("tex_rgb = sample_bilinear(tex_lin, u_i, v_i)",
          "tex_rgb = MIP_HOOK(tex_lin, u_i, v_i, cattr, sx, sy)")],
        hooks={"MIP_HOOK": buat_hook_mip(pyr)})

    W = H = 256
    cam = dict(eye=(6.5, 5.0, 8.5), center=(0, 0.7, 0), far=40.0)

    def frame(fn, yaw, w=W, h=H):
        M = rot_y(yaw) @ scale((1.4, 1.4, 1.4))
        img, _, _ = fn(mesh, w=w, h=h, tex_u8=tex, model=M, **cam)
        return img

    def referensi(yaw):
        # supersample 4x (bilinear biasa), lalu box-downscale di cahaya linear
        hi = frame(raster3d.render, yaw, w=4 * W, h=4 * H)
        lin = srgb_to_linear(hi.astype(np.float64) / 255.0)
        lin = lin.reshape(H, 4, W, 4, 3).mean(axis=(1, 3))
        return np.clip(linear_to_srgb(lin) * 255 + 0.5, 0, 255).astype(np.uint8)

    yaws = (35.0, 36.0)
    off = [frame(raster3d.render, y) for y in yaws]
    on = [frame(render_mip, y) for y in yaws]
    ref = [referensi(y) for y in yaws]
    mask = erosi(ref[0].sum(2) > 0)

    print("  piksel di dalam objek (tanpa tepi): %d" % mask.sum())
    print("  %-26s %10s %8s %8s" % ("", "energi HF", "PSNR", "SSIM"))
    for nama, im in (("tanpa mipmap", off[0]), ("dengan mipmap", on[0]), ("referensi 4x SS", ref[0])):
        p = psnr(im, ref[0]); s = ssim(im, ref[0])
        print("  %-26s %10.1f %8.2f %8.4f" % (nama, energi_hf(im, mask), p, s))
    # proxy 'kelap-kelip': selisih frame ke frame saat model diputar 1 derajat
    def kedip(a, b):
        return float(np.abs(a.astype(int) - b.astype(int)).sum(2)[mask].mean())
    print("  selisih antar-frame (yaw 35 -> 36 derajat), rata-rata di dalam objek:")
    print("    tanpa mipmap  : %.2f" % kedip(off[0], off[1]))
    print("    dengan mipmap : %.2f" % kedip(on[0], on[1]))
    print("    referensi 4x  : %.2f  (batas bawah: perubahan geometri murni)" % kedip(ref[0], ref[1]))

    def amp(a, b):
        return np.clip(np.abs(a.astype(int) - b.astype(int)) * 4, 0, 255)
    save("tahap6_mip_tanpa", off[0])
    save("tahap6_mip_dengan", on[0])
    save("tahap6_mip_referensi", ref[0])
    save("tahap6_mip_selisih_vs_referensi_x4", np.hstack([amp(off[0], ref[0]), amp(on[0], ref[0])]))
    save("tahap6_mip_berdampingan", np.hstack([off[0], on[0], ref[0]]))


# ======================================================================
# A3  Histogram kode depth 16-bit pada scene z-fighting
# ======================================================================
def bagian_zfight_hist():
    print("\n[A3] Histogram kode depth 16-bit, scene z-fighting")
    m = bs._zfight_scene()
    cam = dict(eye=(0, 1, 6), center=(0, 1, -1), cull_back=False, far=200,
               tri_colors=bs.TRI_COLS, light_dir=(0, 0.2, 1))
    hasil = []
    for near in (1e-3, 1.0):
        _, dep, _ = raster3d.render(m, w=192, h=192, near=near, depth_bits=None, **cam)
        d = dep[np.isfinite(dep)]
        kode = np.floor((d * 0.5 + 0.5) * (2 ** 16 - 1)).astype(int)
        vals, cnt = np.unique(kode, return_counts=True)
        print("  near=%-6g  pixel=%d  kode unik=%d  rentang kode=%d  (1 langkah = %.2e NDC)"
              % (near, d.size, len(vals), kode.max() - kode.min(), 2 / (2 ** 16 - 1)))
        hasil.append((near, vals - vals.min(), cnt))

    # gambar histogram dengan PIL (tanpa matplotlib)
    W, H = 760, 330
    im = Image.new("RGB", (W, H), "white")
    dr = ImageDraw.Draw(im)
    ymax = max(c.max() for _, _, c in hasil)
    for k, (near, x, c) in enumerate(hasil):
        ox = 40 + k * 370
        dr.text((ox, 8), "near = %g  (%d kode depth unik)" % (near, len(x)), fill="black")
        dr.line([(ox, 290), (ox + 320, 290)], fill="black")
        dr.line([(ox, 30), (ox, 290)], fill="black")
        n = max(int(x.max()) + 1, 8)
        bw = 300 / n
        for xi, ci in zip(x, c):
            hbar = 250 * ci / ymax
            x0 = ox + 10 + xi * bw
            dr.rectangle([x0, 290 - hbar, x0 + max(bw - 2, 2), 290], fill=(60, 120, 210))
        dr.text((ox, 298), "kode depth - kode minimum", fill="black")
        dr.text((ox + 4, 30), "jumlah pixel (maks %d)" % ymax, fill="black")
    save("tahap6_histogram_depth_zfight", np.array(im))


if __name__ == "__main__":
    bagian_e4()
    bagian_lantai()
    bagian_mipmap()
    bagian_zfight_hist()
    print("\nselesai.")