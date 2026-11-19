python tahap6.py

[A5-1] Contoh E4: u di tengah layar, wL=1, wR=9
  naif            u = 0.500
  perspective-correct u = (u/w) / (1/w) = 0.0556 / 0.5556 = 0.100

[A5-1] Lantai bertexture: perspective-correct vs naif (texture berenang)
  pixel yang berbeda jauh (>60 level): 12712 dari 65536 (19.4%)
  PSNR(naif, benar) = 12.8 dB   SSIM = 0.749
  tulis out/tahap6_lantai_perspective_correct.png
  tulis out/tahap6_lantai_naif.png
  tulis out/tahap6_lantai_berdampingan.png

[A5-2] Mipmap: candi bawaan dari jauh (texture relief.ppm)
  piramida mip: [256, 128, 64, 32] (ukuran sisi tiap level)
  piksel di dalam objek (tanpa tepi): 4147
                              energi HF     PSNR     SSIM
  tanpa mipmap                  29833.4    27.10   0.9507
  dengan mipmap                 11090.5    30.33   0.9771
  referensi 4x SS                1325.6      inf   1.0000
  selisih antar-frame (yaw 35 -> 36 derajat), rata-rata di dalam objek:
    tanpa mipmap  : 147.82
    dengan mipmap : 65.78
    referensi 4x  : 21.13  (batas bawah: perubahan geometri murni)
  tulis out/tahap6_mip_tanpa.png
  tulis out/tahap6_mip_dengan.png
  tulis out/tahap6_mip_referensi.png
  tulis out/tahap6_mip_selisih_vs_referensi_x4.png
  tulis out/tahap6_mip_berdampingan.png

[A3] Histogram kode depth 16-bit, scene z-fighting
  near=0.001   pixel=5704  kode unik=1  rentang kode=0  (1 langkah = 3.05e-05 NDC)
  near=1       pixel=5704  kode unik=13  rentang kode=12  (1 langkah = 3.05e-05 NDC)
  tulis out/tahap6_histogram_depth_zfight.png

selesai.