# Examples

Use these to calibrate tone, density, and the interaction. Do not copy their facts into other suggestions.

## A. First turn from minimal input

**User:**
> Topik: Form Builder di One Service. Dulu tiap kuesioner (misal Party Scan AI Readiness) harus di-coding IT, rekap skor manual. Sekarang user bisa bikin form & kuis sendiri, skor otomatis, bisa ekspor. Live 10 Sep.

**Good response (short, focused):**
> Siap, ini sudah cukup untuk kerangka Kondisi Sebelum, Setelah, dan Solusi. Supaya Analisa Penyebab, Biaya, dan Manfaat tidak berisi asumsi, saya perlu beberapa hal:
> 1. Kenapa sebelumnya tidak memakai form builder siap pakai? (lisensi, biaya, integrasi SSO, atau lainnya)
> 2. Apakah ada biaya tambahan (lisensi, server, layanan), atau seluruhnya memakai resource yang sudah ada?
> 3. Ada angka hasil yang bisa dicantumkan? Misalnya jumlah respons nyata, waktu membuat form sebelum vs sesudah.
> 4. Dibuat oleh siapa saja (nama/NIK), dan kondisi awalnya divalidasi di mana?

**Weak response:** a 20-item questionnaire, or a full draft that invents a cost of Rp0 and a "70% faster" claim.

## B. Finished Sheet 1 content (good density)

**Tema/ Judul:** Membangun Form Builder internal di One Service untuk survei & kuesioner terintegrasi SSO

**Kondisi Sebelum Perbaikan/ Masalah**
```
- Setiap kuesioner/instrumen penilaian (mis. Party Scan AI Readiness) harus di-coding oleh IT, jadi user harus antre ke developer untuk setiap form baru.
- Belum ada form builder di platform internal yang terhubung SSO/HRIS LNK, sehingga identitas pengisi tidak terjamin.
- Rekap skor & distribusi jawaban masih dikerjakan manual.
- Form builder siap pakai yang bisa di-hosting sendiri berlisensi AGPL/GPL atau komersial (mulai US$1.299); tidak ada yang lolos syarat lisensi MIT.
- Undangan hanya berupa tautan yang harus disalin & dikirim manual oleh pemilik form.
```

**Kondisi Setelah Perbaikan/ Evaluasi**
```
- Live di produksi sejak 10 Sep 2026.
- User membuat sendiri form, kuis & template tanpa menunggu developer.
- Pemakaian nyata: Party Scan AI Readiness 4 respons (11 Sep) dan 8 respons (18 Sep), skor otomatis per responden.
- Rekap instan: ringkasan grafik + ekspor CSV/XLSX.
- Tanpa server tambahan (menumpang One Service).
```
Note: the original form also listed automated test results here. Those prove build quality, not the improvement, so they belong in a lampiran.

**Analisa Penyebab**
```
**Analisa penyebab menggunakan ANAKONDA:**
**Man:** user non-IT bergantung pada developer untuk setiap form baru.
**Method:** kuesioner dibuat sebagai kode program, bukan konfigurasi; rekap skor tidak otomatis.
**Environment:** layanan form publik menyimpan data di luar infrastruktur & SSO perusahaan.

**5-Why:**
1. Kenapa user tidak bisa membuat kuesioner sendiri? Party Scan di-hard-code.
2. Kenapa di-hard-code? Tidak ada form builder di platform internal.
3. Kenapa tidak memakai produk jadi? Semuanya AGPL/GPL atau berbayar.
4. Kenapa tidak dibuat sejak awal? Form belum diperlakukan sebagai kapabilitas platform yang bisa dipakai ulang.

**Akar masalah:** tidak ada form builder internal yang terintegrasi SSO dan bebas lisensi.
```

**Biaya/ Investasi**
```
Dikembangkan internal dengan library open-source berlisensi MIT (Rp0).
Menumpang infrastruktur One Service yang sudah ada (EKS, MongoDB, SSO, layanan email); tidak ada server atau lisensi baru.
**Total biaya/investasi:** Rp0.
```

**Manfaat (QCDSM)**
```
quality:  Before: skor manual/hard-code, identitas pengisi tidak terjamin. After: identitas dari SSO, skor dihitung server, 1 orang 1 jawaban.
cost:     Before: alternatif komersial FormEngine Designer StartUp US$1.299 (harga resmi formengine.io) ≈ Rp23,2 juta. After: Rp0 lisensi (cost avoidance).
delivery: Before: form baru = antre coding, rekap manual. After: form dibuat user dalam hitungan menit, rekap & ekspor instan.
morale:   Before: user bergantung pada IT. After: user mandiri membuat form & kuis.
```

## C. ANAKONDA row (good)

| Kategori | What Should Be Happen | What Actually Happen | PIC Validasi | Tempat | Hasil |
|---|---|---|---|---|---|
| Method | Kuesioner baru dapat dibuat lewat konfigurasi oleh user, dengan rekap skor otomatis | Kuesioner dibuat sebagai kode program oleh developer; rekap skor dikerjakan manual | Agung Prasetyo | One Service | Valid |

A weak row fills all five categories with generic statements ("Material: belum tersedia material yang memadai") just to complete the table.
