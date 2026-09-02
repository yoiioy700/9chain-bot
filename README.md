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

## ✨ Daftar Lengkap Task & Fitur Otomatis

| Task / Fitur | Status | Deskripsi |
| :--- | :---: | :--- |
| 🔄 **24/7 Auto Loop** | ✅ | Berjalan otomatis tanpa henti dengan jeda siklus + *live countdown timer*. |
| 🔐 **Headless Login** | ✅ | Login otomatis via Email & Password langsung ke API resmi (tanpa browser). |
| 🎁 **Auto Daily Check-in** | ✅ | Mengklaim hadiah streak harian (*Daily Gift*) secara otomatis (`/me/check-in`). |
| ⚡ **Auto Push Taps** | ✅ | Menghabiskan kuota tap harian dengan kecepatan & jeda yang bisa diatur (*human-like*). |
| 🛠️ **Auto Hardware Upgrade** | ✅ | Otomatis menaikkan level modul hardware (CPU, RAM, Anti-Sybil, Storage) jika poin cukup. |
| ⬆️ **Auto Node Tier Upgrade** | ✅ | Otomatis menaikkan tingkatan Node Tier (Tier 1 → Tier 2 → Tier 3) jika poin mencukupi. |
| 📋 **Auto Claim Quests** | ✅ | Memindai dan mengklaim seluruh reward misi harian & sosial yang sudah selesai (`/program/quests`). |
| 💬 **Auto Pray Chat** | ✅ | Otomatis bergabung ke room doa komunitas dan mengirim pesan doa harian (`/prayer/rooms`). |
| 🌐 **Multi-Account & Proxy** | ✅ | Menjalankan banyak akun secara berurutan dengan sesi terisolasi + proxy support. |
| 📱 **Telegram Notification** | ✅ | Laporan detail status node, total poin, perolehan harian, dan riwayat upgrade. |

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
    "tap_batch_size": 5,
    "tap_delay_min": 1.0,
    "tap_delay_max": 2.5,
    "auto_upgrade_components": true,
    "auto_upgrade_node_tier": true,
    "auto_claim_quests": true,
    "auto_pray": true,
    "pray_room": "together"
  },
  "accounts": [
    {
      "name": "Akun Utama",
      "email": "email_anda@gmail.com",
      "password": "password_akun_anda",
      "totp_code": "",
      "proxy": ""
    }
  ]
}
```

### 💡 Penjelasan Pengaturan Task:
* **`loop_mode`**: `true` agar bot berjalan 24/7.
* **`loop_interval_hours`**: Jeda waktu antar siklus dalam jam (misal `6` jam sekali).
* **`tap_batch_size`**: Jumlah tap per request (default `5` tap, bisa disetel 1-50).
* **`tap_delay_min` & `tap_delay_max`**: Rentang jeda santai antar tap dalam detik (`1.0` - `2.5` detik).
* **`auto_upgrade_components`**: Otomatis upgrade level modul CPU, RAM, Anti-Sybil jika poin LOVE9 cukup.
* **`auto_upgrade_node_tier`**: Otomatis naikkan tingkatan Node Tier (Tier 1 ➔ Tier 2 ➔ Tier 3).
* **`auto_claim_quests`**: Otomatis klaim semua quest yang sudah selesai.
* **`auto_pray`**: Otomatis mengirim pesan doa komunitas ke room `pray_room` (default: `"together"`).

---

## 🖥️ Menjalankan 24/7 di Background VPS (Screen)

```bash
# 1. Buat session screen baru
screen -S 9chain

# 2. Jalankan bot
python3 bot.py

# 3. Keluar dari screen tanpa mematikan bot:
# Tekan tombol CTRL + A lalu tekan D
```

**Melihat bot kembali:**
```bash
screen -r 9chain
```
