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
        self.email = account_config.get("email", "").strip()
        self.password = account_config.get("password", "").strip()
        self.totp_code = account_config.get("totp_code", "").strip()
        self.token = account_config.get("token", "").strip()
        self.proxy = account_config.get("proxy", "").strip()
        self.device_id = account_config.get("device_id") or str(uuid.uuid4())
        
        self.session = requests.Session()
        if self.proxy:
            self.session.proxies = {"http": self.proxy, "https": self.proxy}

        # Bersihkan kata 'Bearer ' jika ada
        clean_token = self.token.replace("Bearer ", "").strip()

        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://www.9chain.com",
            "Referer": "https://www.9chain.com/",
            "x-device-id": self.device_id,
        })

        if clean_token:
            self.session.headers["Authorization"] = f"Bearer {clean_token}"

        self.stats = {
            "name": self.name,
            "status": "Failed",
            "tier": 1,
            "xp_total": "0",
            "contribution_rate": "0",
            "daily_gift": "Skipped",
            "taps_done": 0,
            "taps_remaining": 0,
            "upgrades": [],
            "quests_claimed": 0
        }

    def login(self):
        """Melakukan login menggunakan email dan password jika token belum ada."""
        if self.token and not self.token.startswith("PASTE_"):
            return True

        if not self.email or not self.password or self.email.startswith("akun"):
            print(f"[{self.name}] ✗ Token atau Email/Password belum dikonfigurasi dengan benar di accounts.json!")
            return False

        print(f"[{self.name}] 🔐 Mencoba login dengan email: {self.email}...")
        payload = {
            "email": self.email,
            "password": self.password
        }
        if self.totp_code:
            payload["totpCode"] = self.totp_code

        try:
            res = self.session.post(f"{API_BASE}/auth/login", json=payload, timeout=20)
            if res.status_code in [200, 201]:
                res_data = res.json()
                access_token = res_data.get("accessToken") or res_data.get("data", {}).get("accessToken")
                if access_token:
                    self.token = access_token
                    self.session.headers["Authorization"] = f"Bearer {self.token}"
                    print(f"[{self.name}] ✓ Login Email Sukses! Access Token diperoleh.")
                    return True
                else:
                    print(f"[{self.name}] ✗ Format respon login tidak sesuai: {res_data}")
                    return False
            else:
                err_msg = res.json().get("message") or res.json().get("error", {}).get("message") or f"HTTP {res.status_code}"
                print(f"[{self.name}] ✗ Gagal login: {err_msg}")
                return False
        except Exception as e:
            print(f"[{self.name}] ✗ Error saat melakukan login: {e}")
            return False

    def enter_node(self):
        """Memulai / mengaktifkan sesi virtual node."""
        try:
            self.session.post(f"{API_BASE}/program/enter", timeout=15)
        except Exception:
            pass

    def daily_checkin(self):
        """Mengklaim hadiah harian (Daily Gift / Streak)."""
        print(f"[{self.name}] 🎁 Memeriksa Daily Gift / Check-in...")
        try:
            res = self.session.post(f"{API_BASE}/me/check-in", timeout=15)
            if res.status_code in [200, 201]:
                data = res.json()
                reward = data.get("reward") or data.get("data", {}).get("reward", 0)
                already = data.get("alreadyCheckedIn", False) or data.get("data", {}).get("alreadyCheckedIn", False)
                if already:
                    self.stats["daily_gift"] = "Already Claimed"
                    print(f"[{self.name}] ℹ️ Daily Gift hari ini sudah diklaim sebelumnya.")
                else:
                    self.stats["daily_gift"] = f"Claimed (+{reward})"
                    print(f"[{self.name}] ✓ Daily Gift Berhasil Diklaim! (+{reward} LOVE9)")
            elif res.status_code == 400:
                self.stats["daily_gift"] = "Already Claimed"
                print(f"[{self.name}] ℹ️ Daily Gift sudah diklaim hari ini.")
            else:
                err = res.json().get("error", {}).get("message", f"HTTP {res.status_code}")
                self.stats["daily_gift"] = "Failed"
                print(f"[{self.name}] - Respon Check-in: {err}")
        except Exception as e:
            self.stats["daily_gift"] = "Error"
            print(f"[{self.name}] - Error Daily Check-in: {e}")

    def fetch_state(self):
        """Mengambil state dan informasi poin node."""
        print(f"[{self.name}] 🔑 Mengambil status Virtual Node...")
        try:
            res = self.session.get(f"{API_BASE}/program/state", timeout=15)
            if res.status_code == 200:
                data = res.json().get("data", res.json())
                self.stats["status"] = "Success"
                self.stats["tier"] = data.get("nodeTier", 1)
                self.stats["xp_total"] = str(data.get("xpTotal", "0"))
                self.stats["contribution_rate"] = str(data.get("contributionRate", "0"))
                self.stats["taps_remaining"] = int(data.get("tapsRemaining", 0))

                print(f"[{self.name}] ✓ Node Terhubung (Tier {self.stats['tier']})")
                print(f"[{self.name}] 📊 Total LOVE9: {self.stats['xp_total']} | Mining Rate: {self.stats['contribution_rate']}/jam | Sisa Tap: {self.stats['taps_remaining']}")
                return data
            elif res.status_code == 401:
                print(f"[{self.name}] ✗ Token Kadaluarsa (HTTP 401). Memerlukan login ulang / token baru.")
                return None
            else:
                err = res.json().get("error", {}).get("message", f"HTTP {res.status_code}")
                print(f"[{self.name}] ✗ Error server: {err}")
                return None
        except Exception as e:
            print(f"[{self.name}] ✗ Error koneksi: {e}")
            return None

    def push_taps(self, max_taps=1000):
        """Melakukan auto-tap / PUSH hingga kuota habis."""
        taps_to_do = self.stats["taps_remaining"]
        if max_taps:
            taps_to_do = min(taps_to_do, max_taps)

        if taps_to_do <= 0:
            print(f"[{self.name}] ⚡ Kuota PUSH tap harian sudah habis (0 remaining).")
            return

        print(f"[{self.name}] ⚡ Memulai Auto-Push {taps_to_do} Taps...")
        total_pushed = 0
        batch_size = 50

        while total_pushed < taps_to_do:
            count = min(batch_size, taps_to_do - total_pushed)
            try:
                res = self.session.post(f"{API_BASE}/program/tap", json={"count": count}, timeout=15)
                if res.status_code in [200, 201]:
                    data = res.json().get("data", res.json())
                    state = data.get("state", data)
                    total_pushed += count
                    self.stats["xp_total"] = str(state.get("xpTotal", self.stats["xp_total"]))
                    remaining = state.get("tapsRemaining", 0)

                    print(f"[{self.name}] [+] PUSH +{count} Taps Sukses! ({total_pushed}/{taps_to_do} | Sisa Kuota: {remaining})")
                    if remaining == 0:
                        break

                    time.sleep(random.uniform(0.3, 0.6))
                else:
                    err = res.json().get("error", {}).get("message", f"HTTP {res.status_code}")
                    print(f"[{self.name}] - PUSH Terhenti: {err}")
                    break
            except Exception as e:
                print(f"[{self.name}] - Error saat PUSH: {e}")
                break

        self.stats["taps_done"] = total_pushed
        print(f"[{self.name}] ✓ Selesai PUSH! Total {total_pushed} Taps berhasil ditambahkan.")

    def auto_upgrade(self):
        """Mengecek katalog dan melakukan upgrade hardware komponen yang terjangkau."""
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
                    next_lvl = comp.get("level", 0) + 1

                    if current_xp >= cost:
                        print(f"[{self.name}] ⬆️ Poin cukup ({current_xp:.1f} >= {cost:.1f}). Mengupgrade {key.upper()} ke Lv.{next_lvl}...")
                        up_res = self.session.post(f"{API_BASE}/program/upgrade", json={
                            "componentKey": key,
                            "toLevel": next_lvl
                        }, timeout=15)

                        if up_res.status_code in [200, 201]:
                            print(f"[{self.name}] ✓ Upgrade {key.upper()} Lv.{next_lvl} Berhasil!")
                            self.stats["upgrades"].append(f"{key.upper()} Lv.{next_lvl}")
                            current_xp -= cost
                            self.stats["xp_total"] = str(current_xp)
                        else:
                            err = up_res.json().get("error", {}).get("message", "")
                            print(f"[{self.name}] - Upgrade {key.upper()} gagal: {err}")
        except Exception as e:
            print(f"[{self.name}] - Error saat cek upgrade: {e}")

    def claim_quests(self):
        """Mengecek quest yang sudah selesai dan mengklaim hadiahnya."""
        print(f"[{self.name}] 📋 Memeriksa Quests harian...")
        try:
            res = self.session.get(f"{API_BASE}/program/quests", timeout=15)
            if res.status_code != 200:
                return

            quests = res.json().get("data", {}).get("quests", [])
            claimed_count = 0

            for q in quests:
                quest_key = q.get("key") or q.get("questKey")
                is_completed = q.get("completed", False) or q.get("isCompleted", False)
                is_claimed = q.get("claimed", False) or q.get("isClaimed", False)

                if is_completed and not is_claimed and quest_key:
                    c_res = self.session.post(f"{API_BASE}/program/quests/claim", json={"questKey": quest_key}, timeout=15)
                    if c_res.status_code in [200, 201]:
                        print(f"[{self.name}] ✓ Klaim Quest '{quest_key}' Berhasil!")
                        claimed_count += 1
            
            self.stats["quests_claimed"] = claimed_count
            if claimed_count > 0:
                print(f"[{self.name}] ✓ Total {claimed_count} quest berhasil diklaim.")
        except Exception as e:
            print(f"[{self.name}] - Error cek quest: {e}")


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
        text += f"• Daily Gift: <b>{s.get('daily_gift', '-')}</b>\n"
        text += f"• Total LOVE9: <b>{s['xp_total']}</b>\n"
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


def sleep_with_countdown(seconds):
    """Menampilkan countdown timer yang rapi sebelum siklus berikutnya."""
    while seconds > 0:
        hrs = seconds // 3600
        mins = (seconds % 3600) // 60
        secs = seconds % 60
        print(f"\r⏳ Menunggu siklus berikutnya: {hrs:02d}:{mins:02d}:{secs:02d} ...", end="", flush=True)
        time.sleep(1)
        seconds -= 1
    print("\r" + " " * 60 + "\r", end="", flush=True)


def run_all_accounts(config):
    settings = config.get("settings", {})
    accounts = config.get("accounts", [])
    tg_config = config.get("telegram", {})

    print("=" * 60)
    print(f"🚀 9Chain All-in-One Bot | Total: {len(accounts)} Akun")
    print(f"⏰ Waktu Eksekusi: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    summary_stats = []

    for idx, acc in enumerate(accounts, start=1):
        print(f"\n▶ [{idx}/{len(accounts)}] Memproses: {acc.get('name')}")
        bot = NineChainBot(acc)

        # Login jika token belum tersedia
        if not bot.token or bot.token.startswith("PASTE_"):
            if not bot.login():
                summary_stats.append(bot.stats)
                continue

        # Inisialisasi Sesi Node
        bot.enter_node()

        # 1. Klaim Hadiah Harian (Daily Gift / Streak)
        if settings.get("auto_daily_gift", True):
            bot.daily_checkin()

        # 2. Ambil Status Node
        state = bot.fetch_state()
        if state:
            # 3. Auto Push Taps
            if settings.get("auto_push_taps", True):
                bot.push_taps(max_taps=settings.get("max_taps", 1000))

            # 4. Auto Upgrade Komponen Node
            if settings.get("auto_upgrade_node", True):
                bot.auto_upgrade()

            # 5. Klaim Quest yang selesai
            if settings.get("auto_claim_quests", True):
                bot.claim_quests()

            # Ambil state terakhir setelah aksi
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
    print("🎉 SEMUA AKUN SELESAI DIPROSES PADA SIKLUS INI!")
    print("=" * 60)


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
        return

    try:
        while True:
            # Reload config tiap siklus agar perubahan setting/akun langsung terbaca
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception as e:
                print(f"✗ Gagal membaca accounts.json: {e}")
                time.sleep(10)
                continue

            settings = config.get("settings", {})
            loop_mode = settings.get("loop_mode", True)
            loop_hours = settings.get("loop_interval_hours", 6)

            run_all_accounts(config)

            if not loop_mode:
                print("\n[ℹ️] Loop mode nonaktif (loop_mode: false). Bot berhenti.")
                break

            interval_seconds = int(loop_hours * 3600)
            print(f"\n💤 Mode 24/7 Aktif. Bot akan tidur selama {loop_hours} jam.")
            sleep_with_countdown(interval_seconds)
            print("\n🔄 Memulai siklus baru...")
    except KeyboardInterrupt:
        print("\n\n🛑 Bot dihentikan oleh pengguna (Ctrl+C). Sampai jumpa!")

if __name__ == "__main__":
    main()
