#!/usr/bin/env bash
# check_env.sh - cek lingkungan Stikman Cerita. Baris diawali [OK] / [GAGAL] / [INFO].
fail=0
ok()   { echo "[OK]    $*"; }
bad()  { echo "[GAGAL] $*"; fail=1; }
info() { echo "[INFO]  $*"; }
if command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null; then
  ok "ffmpeg $(ffmpeg -version | head -1 | awk '{print $3}')"
  ffmpeg -hide_banner -encoders 2>/dev/null | grep -q libx264 && ok "encoder libx264" || bad "libx264 tidak ada"
  ffmpeg -hide_banner -encoders 2>/dev/null | grep -qE ' aac ' && ok "encoder aac" || bad "encoder aac tidak ada"
  ffmpeg -hide_banner -filters 2>/dev/null | grep -q sidechaincompress && ok "ducking musik (sidechaincompress)" || info "tanpa sidechaincompress"
else
  bad "ffmpeg/ffprobe tidak ditemukan"
fi
python3 -c "import PIL, numpy; print('[OK]    Pillow', PIL.__version__, '+ numpy', numpy.__version__)" 2>/dev/null || bad "Pillow/numpy tidak ada (pip install pillow numpy)"
S="$(cd "$(dirname "$0")" && pwd)"
python3 -c "import sys; sys.path.insert(0,'$S'); import stik; f=stik.font('judul',40); print('[OK]    font bulat', f.path.split('/')[-1])" 2>/dev/null || bad "font tidak terbaca"
info "CPU: $(nproc 2>/dev/null || echo ?) core (render paralel)"
[ -d /mnt/user-data/outputs ] && info "mode chat: hasil akhir disalin ke /mnt/user-data/outputs; perintah dibatasi ±3 menit" || info "mode lokal / Claude Code"
exit $fail
