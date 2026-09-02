# 9Chain All-in-One Multi-Account Bot 🚀

Bot automasi terminal super ringan untuk platform **9Chain** (https://www.9chain.com).
Didesain khusus untuk VPS Headless low-spec (tidak butuh Chromium / browser GUI, hanya butuh RAM ~15 MB).

## Fitur Utama
1. **Auto Login / Token Support**: Mendukung login otomatis menggunakan **Email & Password** maupun langsung via **Access Token (JWT)**.
2. **Auto Daily Gift / Streak**: Otomatis mengklaim hadiah check-in harian (`/me/check-in`).
3. **Auto Push Taps**: Eksekusi 1.000 tap harian otomatis dengan batch request efisien dan jeda natural.
4. **Auto Hardware Upgrade**: Otomatis menaikkan level modul hardware (CPU, RAM, Anti-Sybil) jika poin LOVE9 mencukupi.
5. **Auto Claim Quests**: Otomatis memeriksa dan mengklaim reward misi harian yang sudah selesai.
6. **Multi-Account & Proxy Support**: Menjalankan banyak akun secara berurutan dengan sesi terisolasi dan dukungan proxy HTTP/HTTPS.
7. **Telegram Notification**: Mengirim laporan ringkasan eksekusi harian ke bot Telegram Anda.

---

## Cara Konfigurasi Akun (`accounts.json`)

Anda bisa menggunakan **Opsi A (Email & Password)** atau **Opsi B (Access Token)**:

### Opsi A: Login Menggunakan Email & Password (Paling Praktis)
Cukup masukkan email dan password akun 9Chain Anda di `accounts.json`:
```json
{
  "name": "Akun Utama",
  "email": "email_anda@gmail.com",
  "password": "password_akun_anda",
  "totp_code": "",
  "proxy": ""
}
```

### Opsi B: Menggunakan Access Token (Jika menggunakan 2FA atau Wallet)
1. Buka https://www.9chain.com di browser PC / HP dan login ke akun Anda.
2. Buka **Developer Tools** (Tekan `F12` di keyboard) lalu pilih tab **Console**.
3. Ketik perintah berikut lalu tekan **Enter**:
   ```javascript
   JSON.parse(localStorage.getItem('9chain-auth')).state.accessToken
   ```
4. Salin string token dan tempelkan ke `accounts.json`:
```json
{
  "name": "Akun Utama",
  "token": "eyJhbGciOiJIUzI1NiIsIn...",
  "proxy": ""
}
```

---

## Cara Instalasi & Penggunaan di VPS / Terminal

### 1. Clone / Masuk ke Direktori Proyek
```bash
git clone https://github.com/yoiioy700/9chain-bot.git
cd 9chain-bot
```

### 2. Install Dependensi
```bash
pip install -r requirements.txt
```

### 3. Konfigurasi `accounts.json`
Salin template:
```bash
cp accounts.example.json accounts.json
```
Edit file:
```bash
nano accounts.json
```

### 4. Jalankan Bot
```bash
python bot.py
```
*(atau `python3 bot.py` di VPS)*

---

## Jadwalkan Otomatis (Cron Job VPS)
Agar bot berjalan otomatis setiap hari pada jam 06:00 WIB:
```bash
crontab -e
```
Tambahkan baris:
```bash
0 6 * * * /usr/bin/python3 /path/to/9chain-bot/bot.py >> /path/to/9chain-bot/bot.log 2>&1
```
