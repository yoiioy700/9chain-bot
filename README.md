# 9Chain All-in-One Multi-Account Bot 🚀

Bot automasi terminal super ringan untuk platform **9Chain** (https://www.9chain.com).
Didesain khusus untuk VPS Headless low-spec (tidak butuh Chromium / browser GUI, hanya butuh RAM ~15 MB).

## Fitur Utama
1. **Mode 24/7 Non-Stop (Auto-Loop)**: Berjalan otomatis terus-menerus dengan jeda siklus yang bisa diatur (misal per 6 jam) dan countdown timer live.
2. **Auto Login Headless (Email & Password)**: Mendukung login otomatis menggunakan **Email & Password** maupun langsung via **Access Token (JWT)**.
3. **Auto Daily Gift / Streak**: Otomatis mengklaim hadiah check-in harian (`/me/check-in`).
4. **Auto Push Taps**: Eksekusi 1.000 tap harian otomatis dengan batch request efisien dan jeda natural.
5. **Auto Hardware Upgrade**: Otomatis menaikkan level modul hardware (CPU, RAM, Anti-Sybil) jika poin LOVE9 mencukupi.
6. **Auto Claim Quests**: Otomatis memeriksa dan mengklaim reward misi harian yang sudah selesai.
7. **Multi-Account & Proxy Support**: Menjalankan banyak akun secara berurutan dengan sesi terisolasi dan dukungan proxy HTTP/HTTPS.
8. **Telegram Notification**: Mengirim laporan ringkasan eksekusi harian ke bot Telegram Anda.

---

## Cara Konfigurasi Akun (`accounts.json`)

Anda bisa menggunakan **Email & Password** atau **Access Token**:

```json
{
  "telegram": {
    "enabled": false,
    "bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
    "chat_id": "YOUR_TELEGRAM_CHAT_ID"
  },
  "settings": {
    "loop_mode": true,
    "loop_interval_hours": 6,
    "auto_daily_gift": true,
    "auto_push_taps": true,
    "max_taps": 1000,
    "auto_upgrade_node": true,
    "auto_claim_quests": true
  },
  "accounts": [
    {
      "name": "Akun 1 (Login Email)",
      "email": "email_anda@gmail.com",
      "password": "password_anda",
      "totp_code": "",
      "proxy": ""
    }
  ]
}
```

* **`loop_mode`**: `true` jika ingin bot berjalan terus 24/7 non-stop. Set ke `false` jika ingin bot jalan sekali lalu selesai (misal jika pakai cron job).
* **`loop_interval_hours`**: Jarak waktu (dalam jam) sebelum bot mengulang memproses akun Anda kembali (rekomendasi: `6` atau `8` jam).

---

## Cara Instalasi & Menjalankan di VPS (24/7)

### 1. Clone Repository
```bash
git clone https://github.com/yoiioy700/9chain-bot.git
cd 9chain-bot
```

### 2. Install Dependensi
```bash
pip install -r requirements.txt
```

### 3. Konfigurasi `accounts.json`
```bash
cp accounts.example.json accounts.json
nano accounts.json
```

### 4. Jalankan 24/7 di Background dengan `screen` atau `tmux`

Agar bot tetap berjalan di VPS meskipun terminal/SSH Anda ditutup:

**Menggunakan `screen` (Paling Mudah):**
```bash
# 1. Buat session screen baru
screen -S 9chain

# 2. Jalankan bot
python3 bot.py

# 3. Tekan CTRL + A lalu tekan D untuk detach (keluar dari screen tanpa mematikan bot)
```

Untuk melihat kembali bot yang sedang berjalan:
```bash
screen -r 9chain
```
