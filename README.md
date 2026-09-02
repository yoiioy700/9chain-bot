<div align="center">

# 🚀 9Chain All-in-One Automation Bot

**Bot Terminal Otomatis 24/7 Super Ringan untuk Ekosistem 9Chain**

[![Platform](https://img.shields.io/badge/Platform-9Chain-blue.svg)](https://www.9chain.com)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://python.org)
[![Headless](https://img.shields.io/badge/Mode-100%25%20Headless-success.svg)]()
[![License](https://img.shields.io/badge/License-MIT-purple.svg)]()

*Didesain khusus untuk VPS Headless low-spec (tidak memerlukan Chromium/Browser GUI, konsumsi RAM hanya ~15 MB).*

</div>

---

## ✨ Fitur Utama

| Fitur | Deskripsi |
| :--- | :--- |
| 🔄 **24/7 Loop Mode** | Berjalan otomatis tanpa henti dengan jeda siklus yang bisa dikonfigurasi + *live countdown timer*. |
| 🔐 **Headless Email Login** | Login otomatis via Email & Password langsung melalui REST API resmi tanpa browser. |
| 🔑 **Token Auth Support** | Mendukung login langsung via Access Token (JWT). |
| 🎁 **Auto Daily Check-in** | Mengklaim hadiah streak harian (*Daily Gift*) secara otomatis (`/me/check-in`). |
| ⚡ **Auto Push Taps** | Menghabiskan 1.000 kuota tap harian dengan batch request aman dan delay natural. |
| 🛠️ **Auto Hardware Upgrade**| Otomatis menaikkan level modul hardware (CPU, RAM, Anti-Sybil) jika poin LOVE9 mencukupi. |
| 📋 **Auto Claim Quests** | Memeriksa dan mengklaim reward misi harian yang sudah rampung secara otomatis. |
| 🌐 **Multi-Account & Proxy**| Menjalankan banyak akun secara terisolasi dan mendukung proxy HTTP/HTTPS. |
| 📱 **Telegram Notification**| Mengirim ringkasan laporan status akun langsung ke bot Telegram Anda. |

---

## 🚀 Panduan Instalasi & Penggunaan (Mulai dari Nol)

### 1. Clone Repository
```bash
git clone https://github.com/yoiioy700/9chain-bot.git
cd 9chain-bot
```

### 2. Install Dependensi
```bash
pip install -r requirements.txt
```
*(atau `pip3 install -r requirements.txt`)*

### 3. Konfigurasi `accounts.json`
Salin template konfigurasi:
```bash
cp accounts.example.json accounts.json
```

Buka dan edit file `accounts.json`:
```bash
nano accounts.json
```

---

## ⚙️ Contoh Format `accounts.json`

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
      "name": "Akun Utama",
      "email": "email_anda@gmail.com",
      "password": "password_akun_anda",
      "totp_code": "",
      "proxy": ""
    },
    {
      "name": "Akun 2 (Tuyul)",
      "email": "akun2@gmail.com",
      "password": "password_akun2",
      "totp_code": "",
      "proxy": ""
    }
  ]
}
```

### 💡 Penjelasan Pengaturan:
* **`loop_mode`**: `true` agar bot berjalan terus 24/7. Set ke `false` jika ingin bot berjalan sekali saja lalu selesai.
* **`loop_interval_hours`**: Waktu tunggu (dalam jam) sebelum siklus berikutnya dijalankan (rekomendasi: `6`).
* **`max_taps`**: Maksimal kuota tap harian yang diproses (default: `1000`).
* **`tap_batch_size`**: Jumlah tap per request (default: `5` tap, bisa diatur `1` sampai `50`).
* **`tap_delay_min` & `tap_delay_max`**: Rentang jeda santai antar tap dalam detik (default: `1.0` - `2.5` detik).

---

## 🖥️ Menjalankan 24/7 di Background VPS (Screen)

Agar bot tetap aktif di VPS meskipun koneksi SSH Anda terputus:

```bash
# 1. Buat session screen baru
screen -S 9chain

# 2. Jalankan bot
python3 bot.py

# 3. Keluar dari screen tanpa mematikan bot:
# Tekan tombol CTRL + A lalu tekan D
```

**Mengecek bot kembali di kemudian hari:**
```bash
screen -r 9chain
```

---

## ⚠️ Disclaimer
Bot ini dibuat untuk tujuan otomasi dan edukasi. Gunakan dengan bijak sesuai dengan ketentuan layanan 9Chain.
