# 9Chain All-in-One Multi-Account Bot 🚀

Bot automasi terminal super ringan untuk platform **9Chain** (https://www.9chain.com).
Didesain khusus untuk VPS Headless low-spec (tidak butuh Chromium / browser GUI, hanya butuh RAM ~20 MB).

## Fitur Utama
1. **Auto Daily Gift**: Klaim hadiah harian untuk menjaga streak.
2. **Auto Push Taps**: Eksekusi 1.000 tap harian otomatis dengan jeda natural (humanized delay).
3. **Auto Hardware Upgrade**: Otomatis menaikkan level CPU & RAM jika poin mencukupi.
4. **Auto Pray Message**: Otomatis mengirim pesan doa komunitas.
5. **Multi-Account & Proxy Support**: Menjalankan banyak akun secara berurutan dengan sesi terisolasi dan dukungan proxy.
6. **Telegram Notification**: Mengirim laporan ringkasan eksekusi harian ke bot Telegram Anda.

## Cara Instalasi & Penggunaan

### 1. Masuk ke Direktori Proyek
```bash
cd 9chain-bot
```

### 2. Install Dependensi
```bash
pip install -r requirements.txt
```

### 3. Konfigurasi Akun (`accounts.json`)
Salin template konfigurasi:
```bash
cp accounts.example.json accounts.json
```
Lalu edit file `accounts.json` dan masukkan email serta password akun 9Chain Anda:
```bash
nano accounts.json
```

### 4. Jalankan Bot
```bash
python bot_9chain.py
```

### 5. Jadwalkan Otomatis (Cron Job VPS)
Buka crontab:
```bash
crontab -e
```
Tambahkan baris berikut agar bot berjalan otomatis setiap hari jam 06:00 WIB:
```bash
0 6 * * * /usr/bin/python3 /path/to/9chain-bot/bot_9chain.py >> /path/to/9chain-bot/bot.log 2>&1
```
