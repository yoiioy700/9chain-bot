# 9Chain All-in-One Multi-Account Bot 🚀

Bot automasi terminal super ringan untuk platform **9Chain** (https://www.9chain.com).
Didesain khusus untuk VPS Headless low-spec (tidak butuh Chromium / browser GUI, hanya butuh RAM ~15 MB).

## Fitur Utama
1. **Auto Push Taps**: Eksekusi 1.000 tap harian otomatis dengan batch request efisien dan jeda natural.
2. **Auto Daily Quests & Gifts**: Klaim quest dan hadiah harian otomatis.
3. **Auto Hardware Upgrade**: Otomatis menaikkan level CPU & RAM jika poin mencukupi.
4. **Auto Pray Message**: Otomatis mengirim pesan doa komunitas.
5. **Multi-Account & Proxy Support**: Menjalankan banyak akun secara berurutan dengan sesi terisolasi dan dukungan proxy.
6. **Telegram Notification**: Mengirim laporan ringkasan eksekusi harian ke bot Telegram Anda.

---

## Cara Mengambil Token Akun (Hanya 5 Detik)

1. Buka https://www.9chain.com di browser PC / HP Anda dan pastikan sudah login.
2. Buka **Developer Tools** (Tekan `F12` di keyboard) lalu pilih tab **Console**.
3. Ketik perintah berikut lalu tekan **Enter**:
   ```javascript
   JSON.parse(localStorage.getItem('9chain-auth')).state.accessToken
   ```
4. Salin teks token yang muncul (berupa string panjang JWT).

---

## Cara Instalasi & Penggunaan di VPS

### 1. Masuk ke Direktori Proyek
```bash
cd 9chain-bot
git pull origin main
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
Lalu edit file `accounts.json` dan tempelkan token akun Anda:
```bash
nano accounts.json
```

Contoh isi `accounts.json`:
```json
{
  "telegram": {
    "enabled": false,
    "bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
    "chat_id": "YOUR_TELEGRAM_CHAT_ID"
  },
  "settings": {
    "auto_daily_gift": true,
    "auto_push_taps": true,
    "max_taps": 1000,
    "auto_upgrade_node": true,
    "auto_pray": true
  },
  "accounts": [
    {
      "name": "Akun Utama",
      "token": "eyJhbGciOiJIUzI1NiIsIn...",
      "proxy": ""
    }
  ]
}
```

### 4. Jalankan Bot
```bash
python bot.py
```
*(atau `python3 bot.py` di VPS)*

### 5. Jadwalkan Otomatis (Cron Job VPS)
Buka crontab:
```bash
crontab -e
```
Tambahkan baris berikut agar bot berjalan otomatis setiap hari jam 06:00 WIB:
```bash
0 6 * * * /usr/bin/python3 /path/to/9chain-bot/bot.py >> /path/to/9chain-bot/bot.log 2>&1
```
