import os
import json
import time
import random
import requests

BASE_URL = "https://www.9chain.com"

PRAYER_MESSAGES = [
    "Wishing good health and peace for everyone in 9Chain.",
    "Together we build a better decentralized future!",
    "Blessings to the team and community. Keep growing!",
    "Peace, prosperity, and success to all nodes.",
    "Hope, strength, and joy for all believers."
]

class NineChainBot:
    def __init__(self, account_config):
        self.name = account_config.get("name", "Unknown Account")
        self.email = account_config.get("email")
        self.password = account_config.get("password")
        self.proxy = account_config.get("proxy", "")
        
        self.session = requests.Session()
        if self.proxy:
            self.session.proxies = {"http": self.proxy, "https": self.proxy}

        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/virtual-node"
        })

        self.stats = {
            "name": self.name,
            "status": "Failed",
            "daily_gift": "Skipped",
            "taps_done": 0,
            "upgrades": [],
            "prayed": False,
            "points": "N/A"
        }

    def login(self):
        print(f"[{self.name}] 🔑 Melakukan login ({self.email})...")
        try:
            res = self.session.post(f"{BASE_URL}/api/auth/login", json={
                "email": self.email,
                "password": self.password
            }, timeout=20)

            if res.status_code in [200, 201]:
                print(f"[{self.name}] ✓ Login Berhasil!")
                self.stats["status"] = "Success"
                return True
            else:
                print(f"[{self.name}] ✗ Gagal login: HTTP {res.status_code} - {res.text}")
                return False
        except Exception as e:
            print(f"[{self.name}] ✗ Error koneksi login: {e}")
            return False

    def claim_daily(self):
        print(f"[{self.name}] 🎁 Mengecek Daily Gift...")
        try:
            res = self.session.post(f"{BASE_URL}/api/node/daily-gift", timeout=15)
            if res.status_code == 200:
                print(f"[{self.name}] ✓ Daily Gift berhasil diklaim!")
                self.stats["daily_gift"] = "Claimed ✓"
            else:
                msg = res.json().get('message', 'Sudah diklaim / Belum tersedia') if 'application/json' in res.headers.get('content-type', '') else 'Already Claimed'
                print(f"[{self.name}] - Daily Gift: {msg}")
                self.stats["daily_gift"] = "Already Claimed"
        except Exception as e:
            print(f"[{self.name}] - Gagal claim Daily Gift: {e}")
            self.stats["daily_gift"] = "Error"

    def push_taps(self, max_taps=1000):
        print(f"[{self.name}] ⚡ Memulai auto-push ({max_taps} taps)...")
        count = 0
        for i in range(max_taps):
            try:
                res = self.session.post(f"{BASE_URL}/api/node/push", timeout=10)
                
                # Auto Re-login jika sesi expired tiba-tiba
                if res.status_code == 401:
                    print(f"\n[{self.name}] Token expired. Melakukan relogin...")
                    if self.login():
                        continue
                    else:
                        break

                if res.status_code == 200:
                    count += 1
                    if count % 100 == 0:
                        print(f"[{self.name}] Progress: {count}/{max_taps} PUSH")
                else:
                    print(f"\n[{self.name}] - PUSH dihentikan: Kuota habis / Limit tercapai.")
                    break

                # Jeda natural 80ms - 150ms
                time.sleep(random.uniform(0.08, 0.15))
            except Exception as e:
                print(f"[{self.name}] Error PUSH tap: {e}")
                time.sleep(1)

        self.stats["taps_done"] = count
        print(f"[{self.name}] ✓ Selesai PUSH! Total {count} taps berhasil dikirim.")

    def auto_upgrade(self):
        print(f"[{self.name}] 🛠️ Mengecek upgrade komponen Node (CPU & RAM)...")
        components = ["cpu", "ram"]
        for comp in components:
            try:
                res = self.session.post(f"{BASE_URL}/api/node/upgrade", json={"component": comp}, timeout=15)
                if res.status_code == 200:
                    print(f"[{self.name}] ✓ Upgrade {comp.upper()} Berhasil!")
                    self.stats["upgrades"].append(comp.upper())
            except Exception:
                pass

    def send_prayer(self):
        print(f"[{self.name}] 🙏 Mengirim pesan doa komunitas...")
        try:
            msg = random.choice(PRAYER_MESSAGES)
            res = self.session.post(f"{BASE_URL}/api/prayer/post", json={"room": "Together", "message": msg}, timeout=15)
            if res.status_code in [200, 201]:
                print(f"[{self.name}] ✓ Pesan doa berhasil dikirim!")
                self.stats["prayed"] = True
            else:
                print(f"[{self.name}] - Prayer skipped / limit")
        except Exception as e:
            print(f"[{self.name}] - Error Prayer: {e}")

    def fetch_stats(self):
        try:
            res = self.session.get(f"{BASE_URL}/api/node/info", timeout=15)
            if res.status_code == 200:
                data = res.json()
                self.stats["points"] = data.get("balance", data.get("total_points", "N/A"))
        except Exception:
            pass


def send_telegram_notification(tg_config, all_stats):
    if not tg_config.get("enabled"):
        return

    bot_token = tg_config.get("bot_token")
    chat_id = tg_config.get("chat_id")
    if not bot_token or not chat_id or "YOUR_" in bot_token:
        return

    text = "📊 <b>Laporan Harian 9Chain Bot</b>\n"
    text += f"⏰ Waktu: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    text += "────────────────────────\n"

    for s in all_stats:
        status_icon = "✅" if s["status"] == "Success" else "❌"
        upgrades_str = ", ".join(s["upgrades"]) if s["upgrades"] else "None"
        pray_str = "✓" if s["prayed"] else "-"
        
        text += f"{status_icon} <b>{s['name']}</b>\n"
        text += f"• Daily Gift: {s['daily_gift']}\n"
        text += f"• PUSH Taps: {s['taps_done']} taps\n"
        text += f"• Upgrade: {upgrades_str}\n"
        text += f"• Pray Room: {pray_str}\n"
        text += "────────────────────────\n"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=15)
        print("\n[✓] Notifikasi ringkasan terkirim ke Telegram!")
    except Exception as e:
        print(f"\n[!] Gagal mengirim notifikasi Telegram: {e}")


def main():
    config_path = os.path.join(os.path.dirname(__file__), "accounts.json")
    example_path = os.path.join(os.path.dirname(__file__), "accounts.example.json")

    if not os.path.exists(config_path):
        if os.path.exists(example_path):
            import shutil
            shutil.copy(example_path, config_path)
            print(f"[!] File accounts.json otomatis dibuat dari accounts.example.json.")
            print(f"[*] Silakan edit file accounts.json dan masukkan akun Anda:")
            print("    nano accounts.json")
        else:
            print(f"✗ File {config_path} tidak ditemukan!")
            print("[*] Silakan buat file accounts.json terlebih dahulu.")
        return

    with open(config_path, "r") as f:
        config = json.load(f)

    settings = config.get("settings", {})
    accounts = config.get("accounts", [])
    tg_config = config.get("telegram", {})

    print("=" * 60)
    print(f"🚀 9Chain All-in-One Bot | Total: {len(accounts)} Akun")
    print("=" * 60)

    summary_stats = []

    for idx, acc in enumerate(accounts, start=1):
        print(f"\n▶ [{idx}/{len(accounts)}] Memproses: {acc.get('name')}")
        bot = NineChainBot(acc)

        if bot.login():
            # 1. Daily Gift
            if settings.get("auto_daily_gift", True):
                bot.claim_daily()

            # 2. Auto Push 1000 Taps
            if settings.get("auto_push_taps", True):
                bot.push_taps(settings.get("max_taps", 1000))

            # 3. Auto Upgrade Node
            if settings.get("auto_upgrade_node", True):
                bot.auto_upgrade()

            # 4. Auto Pray
            if settings.get("auto_pray", True):
                bot.send_prayer()

            bot.fetch_stats()

        summary_stats.append(bot.stats)

        # Jeda natural antar akun (3-6 detik)
        if idx < len(accounts):
            pause = random.randint(3, 6)
            print(f"[*] Menunggu {pause} detik sebelum pindah akun...")
            time.sleep(pause)

    # Kirim Laporan ke Telegram jika diaktifkan
    send_telegram_notification(tg_config, summary_stats)

    print("\n" + "=" * 60)
    print("🎉 SEMUA AKUN SELESAI DIPROSES!")
    print("=" * 60)

if __name__ == "__main__":
    main()
