# Tugu Pahlawan 3D: rasterizer NumPy, ray tracer, dan viewer WebGL

Pipeline grafika 3D yang ditulis dari nol dengan NumPy (transformasi homogen 4x4, near clipping,
pembagian w, z-buffer barycentric, texture perspective-correct, shading Lambert), sebuah ray tracer
pembanding (Moller-Trumbore), dan viewer real-time Three.js. Objek yang dirender adalah model low-poly
**Tugu Pahlawan Surabaya** (560 segitiga). Candi low-poly bawaan (180 segitiga) tetap dipakai sebagai
kasus uji referensi dan untuk demonstrasi bug dan mipmap.

Demo: `https://<username>.github.io/tugu-pahlawan-3d-rasterizer/web/` (isi setelah Pages aktif)

**Aturan:** tumpukan transformasi, rasterizer z-buffer, dan ray tracer hanya memakai NumPy. Pillow dipakai
untuk membaca/menulis gambar referensi dan membuat texture. Viewer real-time (`web/`) memakai Three.js.

**Konvensi** (dipatok di bagian atas `transforms.py`, tidak dicampur): column vector, pre-multiply
(`p' = M @ p`), rantai dibaca kanan ke kiri; right-handed; kamera menghadap `-z`; NDC `[-1,1]^3` dengan
near di `z=-1`; viewport membalik sumbu y.

## Cara menjalankan

```bash
python -m pip install -r requirements.txt
python make_model.py        # data/pusaka_model.obj (180 segitiga) + data/relief.ppm (candi bawaan)
python make_tugu.py         # data/tugu_pahlawan.obj (skala 0.05) + data/tugu_atlas.ppm dari assets/
python tests.py             # -> ALL CHECKS PASSED

python worked_tugu.py       # satu vertex tugu melewati seluruh ruang koordinat
python raster_tugu.py  --model data/tugu_pahlawan.obj --w 512 --h 512 --out out/tugu_raster.ppm
python raytrace_tugu.py --model data/tugu_pahlawan.obj --w 512 --h 512 --out out/tugu_rt.ppm
python compare.py out/tugu_raster.ppm out/tugu_rt.ppm --diff out/diff_tugu.ppm

python broken_scene.py --all   # tiga bug (inside-out, zfight, stretched) dengan bukti
python cull_test.py            # fragmen dengan dan tanpa backface culling
python tahap6.py               # UV naif vs perspective-correct, mipmap, histogram depth

npx serve .                    # buka http://localhost:3000/web/ (Three.js, OrbitControls, Export PPM)
```

Folder `out/` dibuat ulang oleh skrip dan tidak di-commit.

## Isi repo

| File | Fungsi |
|---|---|
| `transforms.py` | matriks T/S/R, `perspective`, `look_at`, `project`, `viewport` |
| `objio.py` | loader OBJ minimal (`v`/`vt`/`f`, triangulasi fan) dan `save_obj` |
| `make_model.py` | candi bertingkat deterministik (180 segitiga) dan texture `relief.ppm` |
| `make_tugu.py` | skala model tugu 0.05 dan atlas warna `tugu_atlas.ppm` dari `assets/Tugu_Pahlawan.obj` |
| `raster3d.py`, `raytrace.py` | renderer raster dan ray tracer asli (candi bawaan, kamera bawaan) |
| `raster_tugu.py`, `raytrace_tugu.py` | salinan keduanya untuk tugu: texture `tugu_atlas.ppm`, kamera `center=(0, 1.4, 0)` |
| `worked_example.py`, `worked_tugu.py` | satu titik melewati object, world, view, clip, NDC, screen (titik acuan dan vertex tugu) |
| `broken_scene.py` | tiga bug dengan bukti SSIM dan kedalaman, masing-masing diperbaiki satu perubahan |
| `cull_test.py` | jumlah fragmen dengan dan tanpa backface culling pada tugu |
| `tahap6.py` | perspective-correct vs naif, mipmap 4 level, histogram kode depth z-fighting |
| `metrics.py`, `compare.py` | PSNR dan SSIM global; selisih frame (diperbesar x6) |
| `ppm_io.py`, `srgb.py` | baca/tulis PPM P6 dan konversi sRGB-linear |
| `tests.py` | E1 sampai E5, bentuk pipeline, render satu segitiga, kecocokan frame dengan `ref/temple_ref.ppm` |
| `web/` | viewer Three.js untuk tugu: kamera, cahaya, dan matriks model disamakan dengan `raster_tugu.py` |
| `assets/` | `Tugu_Pahlawan.obj`, sumber model |
| `ref/` | `temple_ref.ppm`, frame referensi untuk `tests.py` |
| `catatan/` | log terminal, pengukuran waktu, dan diagnosis tiga bug |

## Model Tugu Pahlawan

- Asal model: `<isi: alat dan cara pembuatan model, mis. skrip, editor 3D, atau bantuan AI>`.
- 560 segitiga, 282 vertex, mesh tertutup, winding CCW menghadap luar, tinggi 41,15 m, sumbu Y ke atas,
  pusat alas di (0, 0, 0). Bagian: alas hijau melebar (radius 4,9 turun ke 2,3), tiang putih beralur yang
  mengecil ke atas, dua pita emas, dan puncak runcing.
- `make_tugu.py` menskalakan koordinat 0,05 supaya muat di kamera bawaan (`model = Ry(35) @ S(1.4)`).
- **Texture berupa atlas tiga kolom** (hijau, putih berbintik, emas). UV tiap bagian dipetakan ke satu
  segitiga di dalam tile warnanya (60 face alas, 260 face tiang dan puncak, 240 face pita). UV ini tidak
  membuka permukaan, jadi satu-satunya detail texture adalah bintik halus pada tile putih. Demonstrasi
  perspective-correct dan mipmap karena itu memakai lantai bertexture dan candi bawaan (`relief.ppm`).

## Perubahan terhadap kerangka awal

- Model tugu, `make_tugu.py`, dan skrip khusus tugu (`raster_tugu.py`, `raytrace_tugu.py`, `worked_tugu.py`).
- `raster3d.py` dan `raytrace.py` tidak diubah (`tests.py` dan `broken_scene.py` memakainya untuk candi bawaan).
- `cull_test.py` dan `tahap6.py` untuk perbaikan berbasis pitfall dan eksperimen texture.
- **Viewer:** `web/viewer.js` memuat `data/tugu_pahlawan.obj` dan `data/tugu_atlas.ppm`, target kamera
  `(0, 1.4, 0)`, dan intensitas lampu ambient dan directional dikali `Math.PI`. Sejak Three.js r155 lampu
  bersifat fisik (pantulan Lambert dibagi pi), sehingga tanpa perkalian itu gambar tampak sekitar 1/pi
  lebih gelap dari render NumPy.
- `.gitignore` mengabaikan `out/`, cache Python, dan data candi yang dibuat ulang oleh `make_model.py`;
  data tugu di-commit karena dibutuhkan viewer di GitHub Pages.

## Hasil pengukuran

| Pengukuran | Hasil |
|---|---|
| `tests.py` | ALL CHECKS PASSED (dua kali jalan; frame candi identik byte dengan `ref/temple_ref.ppm`) |
| Candi bawaan, raster vs ray tracer (256x256) | PSNR 76,9 dB, SSIM 1,000, 1 dari 65.536 piksel berbeda (maks 10) |
| Tugu, raster vs ray tracer (512x512) | selisih 0 di semua piksel (PSNR tak hingga, SSIM 1,000) |
| Tugu, raster NumPy vs WebGL, lampu belum dikali pi | PSNR 23,8 dB, SSIM 0,754 (gambar WebGL lebih gelap) |
| Tugu, raster NumPy vs WebGL, lampu dikali pi | PSNR 38,6 dB, SSIM 0,997, selisih rata-rata 0,3, maks 115 (siluet, batas bagian, bintik poros) |
| Waktu, 256x256, 560 segitiga, satu kali jalan | raster 0,751 s, ray tracer 4,638 s (rasio sekitar 6,2; termasuk start Python dan muat model) |
| Backface culling, tugu 512x512 | fragmen 16.717 menjadi 15.035 (piksel terlihat 14.953) |
| Bug inside-out | SSIM 0,790, PSNR 14,3 dB terhadap render benar |
| Bug z-fighting | 2.852 piksel salah (near 0,001) menjadi 184 (near 1,0); kode depth 1 menjadi 13 |
| Bug stretched | SSIM 0,594, PSNR 11,5 dB; panjang kolom model 3,08 / 0,7 / 1,4 |
| Mipmap 4 level (candi dari jauh) | energi frekuensi tinggi 29.833 menjadi 11.090 (referensi 1.326); PSNR 27,10 menjadi 30,33 dB |
| UV naif vs perspective-correct (lantai) | 19,4% piksel berbeda lebih dari 60 level, PSNR 12,8 dB |

Waktu diukur dengan `raster3d.py` dan `raytrace.py` asli (kamera bawaan), jadi tugu sebagian keluar bingkai;
jumlah segitiga sama. Sisa aliasing setelah mipmap diduga berasal dari LOD yang dihitung per segitiga
(belum dibuktikan; piramida 8 level memberi hasil hampir sama).

## Verified

| Item | Status | Tanggal | Lingkungan |
|---|---|---|---|
| `python tests.py` | ALL CHECKS PASSED | `<isi>` | Nobara Linux 44 (KDE), Python 3.14.8, NumPy 2.4.6, Pillow `<isi>` |
| `worked_tugu.py` | cocok dengan hitungan tangan hingga 6 desimal | `<isi>` | sama |
| `broken_scene.py --all`, `tahap6.py`, `cull_test.py` | dijalankan, angka di atas | `<isi>` | sama |
| Viewer `web/` | tugu tampil dan bisa di-orbit; PSNR 38,6 dB terhadap raster | `<isi>` | `<isi: browser dan versi>`, Three.js 0.160.0, Node v22.23.1 |
| Clone bersih | `<isi setelah uji: clone, pip install, make_model.py, make_tugu.py, tests.py hijau, npx serve .>` | `<isi>` | `<isi>` |

## Atribusi

- Texture: dibuat prosedural oleh `make_tugu.py` dan `make_model.py` (tanpa aset pihak ketiga).
- Model tugu: `<isi sumber dan lisensi bila berasal dari pihak lain>`.
