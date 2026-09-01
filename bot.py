import os
import json
import time
import uuid
import random
import requests

API_BASE = "https://api.9chain.com/v2"

class NineChainBot:
    def __init__(self, account_config):
        self.name = account_config.get("name", "Unknown Account")
        self.token = account_config.get("token", "").strip()
        self.proxy = account_config.get("proxy", "").strip()
        self.device_id = str(uuid.uuid4())
        
        self.session = requests.Session()
        if self.proxy:
            self.session.proxies = {"http": self.proxy, "https": self.proxy}

        # Bersihkan kata Bearer jika user tidak sengaja menyertakannya
        clean_token = self.token.replace("Bearer ", "").strip()

        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://www.9chain.com",
            "Referer": "https://www.9chain.com/",
            "x-device-id": self.device_id,
            "Authorization": f"Bearer {clean_token}"
        })

        self.stats = {
            "name": self.name,
            "status": "Failed",
            "tier": 1,
            "xp_total": "0",
            "contribution_rate": "0",
            "taps_done": 0,
            "taps_remaining": 0,
            "upgrades": []
        }

    def fetch_state(self):
        if not self.token or self.token.startswith("PASTE_"):
            print(f"[{self.name}] ✗ Token belum diisi di accounts.json!")
            return None

        print(f"[{self.name}] 🔑 Menghubungkan ke 9Chain Node...")
        try:
            res = self.session.get(f"{API_BASE}/program/state", timeout=15)
            if res.status_code == 200:
                data = res.json().get("data", {})
                self.stats["status"] = "Success"
                self.stats["tier"] = data.get("nodeTier", 1)
                self.stats["xp_total"] = str(data.get("xpTotal", "0"))
                self.stats["contribution_rate"] = str(data.get("contributionRate", "0"))
                self.stats["taps_remaining"] = int(data.get("tapsRemaining", 0))

                print(f"[{self.name}] ✓ Akun Terhubung!")
                print(f"[{self.name}] 📊 Poin (XP): {self.stats['xp_total']} | Mining Rate: {self.stats['contribution_rate']}/jam | Sisa Tap: {self.stats['taps_remaining']}")
                return data
            elif res.status_code == 401:
                print(f"[{self.name}] ✗ Token Expired (HTTP 401). Silakan copy token baru dari browser.")
                return None
            else:
                err = res.json().get("error", {}).get("message", f"HTTP {res.status_code}")
                print(f"[{self.name}] ✗ Error server: {err}")
                return None
        except Exception as e:
            print(f"[{self.name}] ✗ Error koneksi: {e}")
            return None

    def push_taps(self, taps_to_do=None):
        if taps_to_do is None:
            taps_to_do = self.stats["taps_remaining"]

        if taps_to_do <= 0:
            print(f"[{self.name}] ⚡ Kuota PUSH tap harian sudah habis (0 remaining).")
            return

        print(f"[{self.name}] ⚡ Memulai Auto-Push {taps_to_do} Taps...")
        total_pushed = 0
        batch_size = 50  # Batch size aman

        while total_pushed < taps_to_do:
            count = min(batch_size, taps_to_do - total_pushed)
            try:
                res = self.session.post(f"{API_BASE}/program/tap", json={"count": count}, timeout=15)
                if res.status_code in [200, 201]:
                    data = res.json().get("data", {})
                    state = data.get("state", {})
                    total_pushed += count
                    self.stats["xp_total"] = str(state.get("xpTotal", self.stats["xp_total"]))
                    remaining = state.get("tapsRemaining", 0)

                    print(f"[{self.name}] [+] PUSH +{count} Taps Sukses! (Total: {total_pushed}/{taps_to_do} | Sisa Kuota: {remaining})")
                    if remaining == 0:
                        break

                    time.sleep(random.uniform(0.3, 0.7))
                else:
                    err = res.json().get("error", {}).get("message", f"HTTP {res.status_code}")
                    print(f"[{self.name}] - PUSH Stop: {err}")
                    break
            except Exception as e:
                print(f"[{self.name}] - Error PUSH: {e}")
                break

        self.stats["taps_done"] = total_pushed
        print(f"[{self.name}] ✓ Selesai PUSH! Total {total_pushed} Taps berhasil ditambahkan.")

    def auto_upgrade(self):
        print(f"[{self.name}] 🛠️ Mengecek kemungkinan Upgrade Hardware...")
        try:
            res = self.session.get(f"{API_BASE}/program/catalog", timeout=15)
            if res.status_code != 200:
                return

            components = res.json().get("data", {}).get("components", [])
            current_xp = float(self.stats["xp_total"])

            for comp in components:
                if comp.get("unlocked") and comp.get("nextCost"):
                    cost = float(comp["nextCost"])
                    key = comp["componentKey"]
                    next_lvl = comp["level"] + 1

                    if current_xp >= cost:
                        print(f"[{self.name}] ⬆️ Poin cukup ({current_xp:.1f} >= {cost:.1f}). Mengupgrade {key.upper()} ke Level {next_lvl}...")
                        up_res = self.session.post(f"{API_BASE}/program/upgrade", json={
                            "componentKey": key,
                            "toLevel": next_lvl
                        }, timeout=15)

                        if up_res.status_code in [200, 201]:
                            print(f"[{self.name}] ✓ Upgrade {key.upper()} Level {next_lvl} Berhasil!")
                            self.stats["upgrades"].append(f"{key.upper()} Lv.{next_lvl}")
                            current_xp -= cost
                            self.stats["xp_total"] = str(current_xp)
                        else:
                            pass
        except Exception as e:
            print(f"[{self.name}] - Error saat cek upgrade: {e}")


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
        
        text += f"{status_icon} <b>{s['name']}</b> (Tier {s['tier']})\n"
        text += f"• Total Poin (XP): <b>{s['xp_total']}</b>\n"
        text += f"• Mining Rate: <b>{s['contribution_rate']}/jam</b>\n"
        text += f"• PUSH Selesai: <b>+{s['taps_done']} taps</b>\n"
        text += f"• Upgrade Hardware: {upgrades_str}\n"
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

        state = bot.fetch_state()
        if state:
            # 1. Auto Push Taps
            if settings.get("auto_push_taps", True):
                bot.push_taps()

            # 2. Auto Upgrade Node
            if settings.get("auto_upgrade_node", True):
                bot.auto_upgrade()

            # Ambil state terakhir
            bot.fetch_state()

        summary_stats.append(bot.stats)

        # Jeda natural antar akun
        if idx < len(accounts):
            pause = random.randint(2, 5)
            print(f"[*] Menunggu {pause} detik sebelum akun berikutnya...")
            time.sleep(pause)

    # Kirim Laporan Telegram
    send_telegram_notification(tg_config, summary_stats)

    print("\n" + "=" * 60)
    print("🎉 SEMUA AKUN SELESAI DIPROSES!")
    print("=" * 60)

if __name__ == "__main__":
    main()
