import os
import json
import time
import uuid
import random
import requests

API_BASE = "https://api.9chain.com/v2"

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
        self.token = account_config.get("token", "").strip()
        self.proxy = account_config.get("proxy", "").strip()
        self.device_id = str(uuid.uuid4())
        
        self.session = requests.Session()
        if self.proxy:
            self.session.proxies = {"http": self.proxy, "https": self.proxy}

        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://www.9chain.com",
            "Referer": "https://www.9chain.com/",
            "x-device-id": self.device_id
        })

        if self.token and not self.token.startswith("PASTE_"):
            if "=" in self.token or ";" in self.token:
                # User memasukkan Cookie string
                self.session.headers["Cookie"] = self.token
            else:
                # User memasukkan Bearer JWT token
                self.session.headers["Authorization"] = f"Bearer {self.token}"

        self.stats = {
            "name": self.name,
            "status": "Failed",
            "xp_total": "0",
            "taps_done": 0,
            "quests_claimed": 0,
            "upgrades": [],
            "prayed": False
        }

    def verify_auth(self):
        if not self.token or self.token.startswith("PASTE_"):
            print(f"[{self.name}] ✗ Token belum diisi! Silakan isi token di accounts.json.")
            return False

        print(f"[{self.name}] 🔑 Memeriksa status koneksi akun...")
        try:
            res = self.session.get(f"{API_BASE}/program/state", timeout=15)
            if res.status_code == 200:
                data = res.json().get("data", {})
                self.stats["status"] = "Success"
                self.stats["xp_total"] = str(data.get("xpTotal", 0))
                print(f"[{self.name}] ✓ Akun Aktif | Total Poin (XP): {self.stats['xp_total']}")
                return True
            elif res.status_code == 401:
                print(f"[{self.name}] ✗ Token Expired / Tidak Valid (HTTP 401). Silakan perbarui token.")
                return False
            else:
                err_msg = res.json().get("error", {}).get("message", f"HTTP {res.status_code}") if "application/json" in res.headers.get("content-type", "") else f"HTTP {res.status_code}"
                print(f"[{self.name}] ✗ Gagal connect: {err_msg}")
                return False
        except Exception as e:
            print(f"[{self.name}] ✗ Error koneksi ke server: {e}")
            return False

    def enter_program_if_needed(self):
        try:
            self.session.post(f"{API_BASE}/program/enter", timeout=15)
        except Exception:
            pass

    def claim_quests(self):
        print(f"[{self.name}] 🎁 Mengecek Quests & Hadiah Harian...")
        try:
            res = self.session.get(f"{API_BASE}/program/quests", timeout=15)
            if res.status_code == 200:
                quests = res.json().get("data", {}).get("quests", [])
                claimed = 0
                for q in quests:
                    q_key = q.get("key") or q.get("id")
                    if q.get("canClaim") and q_key:
                        claim_res = self.session.post(f"{API_BASE}/program/quests/claim", json={"questKey": q_key}, timeout=15)
                        if claim_res.status_code == 200:
                            claimed += 1
                            print(f"[{self.name}] ✓ Berhasil klaim quest: {q.get('title', q_key)}")
                
                self.stats["quests_claimed"] = claimed
                if claimed == 0:
                    print(f"[{self.name}] - Tidak ada quest baru yang siap diklaim saat ini.")
            else:
                print(f"[{self.name}] - Status Quests: HTTP {res.status_code}")
        except Exception as e:
            print(f"[{self.name}] - Error saat klaim quest: {e}")

    def push_taps(self, max_taps=1000):
        print(f"[{self.name}] ⚡ Menjalankan Auto-Push {max_taps} Taps...")
        total_success = 0
        batch_size = 100  # Kirim dalam batch agar efisien & cepat

        while total_success < max_taps:
            count_to_tap = min(batch_size, max_taps - total_success)
            try:
                res = self.session.post(f"{API_BASE}/program/tap", json={"count": count_to_tap}, timeout=15)
                if res.status_code == 200:
                    total_success += count_to_tap
                    print(f"[{self.name}] [+] Progress PUSH: {total_success}/{max_taps} Taps selesai")
                    time.sleep(random.uniform(0.5, 1.2))
                else:
                    err_data = res.json() if "application/json" in res.headers.get("content-type", "") else {}
                    err_msg = err_data.get("error", {}).get("message", f"Limit tercapai (HTTP {res.status_code})")
                    print(f"[{self.name}] - Stop PUSH: {err_msg}")
                    break
            except Exception as e:
                print(f"[{self.name}] - Error saat tap batch: {e}")
                break

        self.stats["taps_done"] = total_success
        print(f"[{self.name}] ✓ Selesai! Total {total_success} Taps berhasil diproses.")

    def auto_upgrade(self):
        print(f"[{self.name}] 🛠️ Mengecek Upgrade Hardware Node...")
        components = ["cpu", "ram"]
        for comp in components:
            try:
                res = self.session.post(f"{API_BASE}/program/upgrade", json={"componentKey": comp}, timeout=15)
                if res.status_code == 200:
                    print(f"[{self.name}] ✓ Upgrade {comp.upper()} Berhasil!")
                    self.stats["upgrades"].append(comp.upper())
            except Exception:
                pass

    def send_prayer(self):
        print(f"[{self.name}] 🙏 Mengirim pesan doa komunitas...")
        try:
            msg = random.choice(PRAYER_MESSAGES)
            res = self.session.post(f"{API_BASE}/prayer/post", json={"room": "Together", "message": msg}, timeout=15)
            if res.status_code in [200, 201]:
                print(f"[{self.name}] ✓ Pesan doa terkirim ke room Together!")
                self.stats["prayed"] = True
            else:
                print(f"[{self.name}] - Prayer: limit / sudah terkirim.")
        except Exception as e:
            print(f"[{self.name}] - Error Prayer: {e}")

    def refresh_final_state(self):
        try:
            res = self.session.get(f"{API_BASE}/program/state", timeout=15)
            if res.status_code == 200:
                data = res.json().get("data", {})
                self.stats["xp_total"] = str(data.get("xpTotal", self.stats["xp_total"]))
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
        text += f"• Poin/XP Total: <b>{s['xp_total']}</b>\n"
        text += f"• PUSH Taps: {s['taps_done']} taps\n"
        text += f"• Quest Claimed: {s['quests_claimed']}\n"
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
            print(f"[*] Silakan edit file accounts.json dan masukkan Token akun Anda:")
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

        if bot.verify_auth():
            bot.enter_program_if_needed()

            # 1. Quests & Daily
            if settings.get("auto_daily_gift", True):
                bot.claim_quests()

            # 2. Auto Push Taps
            if settings.get("auto_push_taps", True):
                bot.push_taps(settings.get("max_taps", 1000))

            # 3. Auto Upgrade Node
            if settings.get("auto_upgrade_node", True):
                bot.auto_upgrade()

            # 4. Auto Pray
            if settings.get("auto_pray", True):
                bot.send_prayer()

            bot.refresh_final_state()

        summary_stats.append(bot.stats)

        # Jeda natural antar akun
        if idx < len(accounts):
            pause = random.randint(3, 6)
            print(f"[*] Menunggu {pause} detik sebelum akun berikutnya...")
            time.sleep(pause)

    # Kirim Laporan Telegram
    send_telegram_notification(tg_config, summary_stats)

    print("\n" + "=" * 60)
    print("🎉 SEMUA AKUN SELESAI DIPROSES!")
    print("=" * 60)

if __name__ == "__main__":
    main()
