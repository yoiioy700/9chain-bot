#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
9Chain All-in-One Multi-Account Bot (24/7 Headless)
GitHub: https://github.com/yoiioy700/9chain-bot
"""

import os
import sys
import json
import time
import uuid
import random
import requests

API_BASE = "https://api.9chain.com/v2"

# Terminal Color Codes (ANSI)
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

BANNER = f"""{CYAN}{BOLD}
  ██████╗  ██████╗██╗  ██╗ █████╗ ██╗███╗   ██╗
  ██╔══██╗██╔════╝██║  ██║██╔══██╗██║████╗  ██║
  ╚██████╔╝██║     ███████║███████║██║██╔██╗ ██║
   ╚═══██║ ██║     ██╔══██║██╔══██║██║██║╚██╗██║
  ██████╔╝ ╚██████╗██║  ██║██║  ██║██║██║ ╚████║
  ╚═════╝   ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
{RESET}{DIM}  9Chain Virtual Node 24/7 Automation Bot | v2.0
{RESET}"""

def mask_email(email):
    """Menyamarkan email untuk keamanan log."""
    if not email or "@" not in email:
        return email
    user, domain = email.split("@", 1)
    if len(user) <= 2:
        masked_user = user[0] + "*"
    else:
        masked_user = user[0] + "*" * (len(user) - 2) + user[-1]
    return f"{masked_user}@{domain}"


class NineChainBot:
    def __init__(self, account_config):
        self.name = account_config.get("name", "Akun")
        self.email = account_config.get("email", "").strip()
        self.password = account_config.get("password", "").strip()
        self.totp_code = account_config.get("totp_code", "").strip()
        self.token = account_config.get("token", "").strip()
        self.proxy = account_config.get("proxy", "").strip()
        self.device_id = account_config.get("device_id") or str(uuid.uuid4())
        
        self.session = requests.Session()
        if self.proxy:
            self.session.proxies = {"http": self.proxy, "https": self.proxy}

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

    def log(self, message, level="INFO"):
        prefix = {
            "INFO": f"{CYAN}[INFO]{RESET}",
            "SUCCESS": f"{GREEN}[✓]{RESET}",
            "WARN": f"{YELLOW}[!]{RESET}",
            "ERROR": f"{RED}[✗]{RESET}",
            "STEP": f"{MAGENTA}[▶]{RESET}"
        }.get(level, f"[{level}]")
        print(f"[{self.name}] {prefix} {message}")

    def login(self):
        """Melakukan login headless via Email & Password jika belum memiliki access token."""
        if self.token and not self.token.startswith("PASTE_"):
            return True

        if not self.email or not self.password or self.email.startswith("akun") or self.email.startswith("user@"):
            self.log("Token atau Email/Password belum diisi dengan benar di accounts.json!", "ERROR")
            return False

        masked = mask_email(self.email)
        self.log(f"Mencoba login headless ({masked})...", "INFO")
        
        payload = {
            "email": self.email,
            "password": self.password
        }
        if self.totp_code:
            payload["totpCode"] = self.totp_code

        for attempt in range(1, 4):
            try:
                res = self.session.post(f"{API_BASE}/auth/login", json=payload, timeout=20)
                if res.status_code in [200, 201]:
                    res_data = res.json()
                    access_token = res_data.get("accessToken") or res_data.get("data", {}).get("accessToken")
                    if access_token:
                        self.token = access_token
                        self.session.headers["Authorization"] = f"Bearer {self.token}"
                        self.log("Login Email Sukses! Sesi aktif.", "SUCCESS")
                        return True
                    else:
                        self.log(f"Format respon login tidak dikenali: {res_data}", "ERROR")
                        return False
                else:
                    err_msg = res.json().get("message") or res.json().get("error", {}).get("message") or f"HTTP {res.status_code}"
                    self.log(f"Gagal login: {err_msg}", "ERROR")
                    return False
            except Exception as e:
                self.log(f"Percobaan login {attempt}/3 gagal ({e}). Mengulang...", "WARN")
                time.sleep(2)
        
        return False

    def enter_node(self):
        """Menginisialisasi sesi Virtual Node."""
        try:
            self.session.post(f"{API_BASE}/program/enter", timeout=15)
        except Exception:
            pass

    def daily_checkin(self):
        """Mengklaim hadiah harian (Daily Gift / Streak)."""
        self.log("Memeriksa Daily Gift / Check-in...", "INFO")
        try:
            res = self.session.post(f"{API_BASE}/me/check-in", timeout=15)
            if res.status_code in [200, 201]:
                data = res.json()
                reward = data.get("reward") or data.get("data", {}).get("reward", 0)
                already = data.get("alreadyCheckedIn", False) or data.get("data", {}).get("alreadyCheckedIn", False)
                if already:
                    self.stats["daily_gift"] = "Already Claimed"
                    self.log("Daily Gift hari ini sudah diklaim sebelumnya.", "INFO")
                else:
                    self.stats["daily_gift"] = f"Claimed (+{reward})"
                    self.log(f"Daily Gift Berhasil Diklaim! (+{reward} LOVE9)", "SUCCESS")
            elif res.status_code == 400:
                self.stats["daily_gift"] = "Already Claimed"
                self.log("Daily Gift sudah diklaim hari ini.", "INFO")
            else:
                err = res.json().get("error", {}).get("message", f"HTTP {res.status_code}")
                self.stats["daily_gift"] = "Failed"
                self.log(f"Respon Check-in: {err}", "WARN")
        except Exception as e:
            self.stats["daily_gift"] = "Error"
            self.log(f"Error Daily Check-in: {e}", "WARN")

    def fetch_state(self):
        """Mengambil informasi poin, kuota tap, dan level node."""
        try:
            res = self.session.get(f"{API_BASE}/program/state", timeout=15)
            if res.status_code == 200:
                data = res.json().get("data", res.json())
                self.stats["status"] = "Success"
                self.stats["tier"] = data.get("nodeTier", 1)
                self.stats["xp_total"] = str(data.get("xpTotal", "0"))
                self.stats["contribution_rate"] = str(data.get("contributionRate", "0"))
                self.stats["taps_remaining"] = int(data.get("tapsRemaining", 0))

                self.log(f"Status Node: Tier {self.stats['tier']} | Rate: {self.stats['contribution_rate']}/jam | Total LOVE9: {self.stats['xp_total']} | Sisa Tap: {self.stats['taps_remaining']}", "SUCCESS")
                return data
            elif res.status_code == 401:
                self.log("Token Kedaluwarsa (HTTP 401). Memerlukan login ulang.", "ERROR")
                return None
            else:
                err = res.json().get("error", {}).get("message", f"HTTP {res.status_code}")
                self.log(f"Error server: {err}", "ERROR")
                return None
        except Exception as e:
            self.log(f"Error koneksi state: {e}", "ERROR")
            return None

    def push_taps(self, max_taps=1000):
        """Melakukan auto-tap / PUSH hingga kuota hari ini habis."""
        taps_to_do = self.stats["taps_remaining"]
        if max_taps:
            taps_to_do = min(taps_to_do, max_taps)

        if taps_to_do <= 0:
            self.log("Kuota PUSH tap harian sudah habis (0 remaining).", "INFO")
            return

        self.log(f"Memulai Auto-Push {taps_to_do} Taps...", "INFO")
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

                    self.log(f"PUSH +{count} Taps Sukses ({total_pushed}/{taps_to_do} | Sisa: {remaining})", "SUCCESS")
                    if remaining == 0:
                        break

                    time.sleep(random.uniform(0.3, 0.6))
                else:
                    err = res.json().get("error", {}).get("message", f"HTTP {res.status_code}")
                    self.log(f"PUSH Terhenti: {err}", "WARN")
                    break
            except Exception as e:
                self.log(f"Error saat PUSH: {e}", "WARN")
                break

        self.stats["taps_done"] = total_pushed
        self.log(f"Selesai PUSH! Total +{total_pushed} Taps berhasil ditambahkan.", "SUCCESS")

    def auto_upgrade(self):
        """Mengecek katalog hardware dan otomatis menaikkan level modul yang terjangkau."""
        self.log("Memeriksa kemungkinan Upgrade Hardware...", "INFO")
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
                        self.log(f"Poin cukup ({current_xp:.1f} >= {cost:.1f}). Mengupgrade {key.upper()} ke Lv.{next_lvl}...", "INFO")
                        up_res = self.session.post(f"{API_BASE}/program/upgrade", json={
                            "componentKey": key,
                            "toLevel": next_lvl
                        }, timeout=15)

                        if up_res.status_code in [200, 201]:
                            self.log(f"Upgrade {key.upper()} Lv.{next_lvl} Berhasil!", "SUCCESS")
                            self.stats["upgrades"].append(f"{key.upper()} Lv.{next_lvl}")
                            current_xp -= cost
                            self.stats["xp_total"] = str(current_xp)
                        else:
                            err = up_res.json().get("error", {}).get("message", "")
                            self.log(f"Upgrade {key.upper()} gagal: {err}", "WARN")
        except Exception as e:
            self.log(f"Error saat cek upgrade: {e}", "WARN")

    def claim_quests(self):
        """Mengecek misi harian dan otomatis mengklaim reward."""
        self.log("Memeriksa Quests harian...", "INFO")
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
                        self.log(f"Klaim Quest '{quest_key}' Berhasil!", "SUCCESS")
                        claimed_count += 1
            
            self.stats["quests_claimed"] = claimed_count
            if claimed_count > 0:
                self.log(f"Total {claimed_count} quest berhasil diklaim.", "SUCCESS")
        except Exception as e:
            self.log(f"Error cek quest: {e}", "WARN")


def send_telegram_notification(tg_config, all_stats):
    """Mengirim ringkasan laporan ke Telegram."""
    if not tg_config.get("enabled"):
        return

    bot_token = tg_config.get("bot_token")
    chat_id = tg_config.get("chat_id")
    if not bot_token or not chat_id or "YOUR_" in bot_token:
        return

    text = "📊 <b>Laporan 9Chain Bot (24/7)</b>\n"
    text += f"⏰ Waktu: <code>{time.strftime('%Y-%m-%d %H:%M:%S')}</code>\n"
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
        print(f"\n{GREEN}[✓] Notifikasi ringkasan terkirim ke Telegram!{RESET}")
    except Exception as e:
        print(f"\n{RED}[!] Gagal mengirim notifikasi Telegram: {e}{RESET}")


def sleep_with_countdown(seconds):
    """Menampilkan hitung mundur waktu tunggu sebelum siklus berikutnya."""
    while seconds > 0:
        hrs = seconds // 3600
        mins = (seconds % 3600) // 60
        secs = seconds % 60
        sys.stdout.write(f"\r⏳ {YELLOW}Menunggu siklus berikutnya: {BOLD}{hrs:02d}:{mins:02d}:{secs:02d}{RESET} ...")
        sys.stdout.flush()
        time.sleep(1)
        seconds -= 1
    sys.stdout.write("\r" + " " * 70 + "\r")
    sys.stdout.flush()


def run_all_accounts(config):
    """Menjalankan otomasi untuk seluruh akun terdaftar."""
    settings = config.get("settings", {})
    accounts = config.get("accounts", [])
    tg_config = config.get("telegram", {})

    print(f"\n{BOLD}{'═' * 60}{RESET}")
    print(f"🚀 {BOLD}Eksekusi Bot | Total: {len(accounts)} Akun | Waktu: {time.strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    print(f"{BOLD}{'═' * 60}{RESET}")

    summary_stats = []

    for idx, acc in enumerate(accounts, start=1):
        name = acc.get('name', f'Akun {idx}')
        print(f"\n{CYAN}{BOLD}▶ [{idx}/{len(accounts)}] Memproses: {name}{RESET}")
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
            print(f"{DIM}[*] Menunggu {pause} detik sebelum akun berikutnya...{RESET}")
            time.sleep(pause)

    # Kirim Laporan Telegram
    send_telegram_notification(tg_config, summary_stats)

    print(f"\n{BOLD}{'═' * 60}{RESET}")
    print(f"{GREEN}🎉 SEMUA AKUN SELESAI DIPROSES PADA SIKLUS INI!{RESET}")
    print(f"{BOLD}{'═' * 60}{RESET}")


def main():
    print(BANNER)
    config_path = os.path.join(os.path.dirname(__file__), "accounts.json")
    example_path = os.path.join(os.path.dirname(__file__), "accounts.example.json")

    if not os.path.exists(config_path):
        if os.path.exists(example_path):
            import shutil
            shutil.copy(example_path, config_path)
            print(f"{YELLOW}[!] File accounts.json otomatis dibuat dari accounts.example.json.{RESET}")
            print(f"[*] Silakan isi akun Anda di file accounts.json:")
            print(f"    {BOLD}nano accounts.json{RESET}\n")
        else:
            print(f"{RED}✗ File {config_path} tidak ditemukan!{RESET}")
        return

    cycle_count = 1
    try:
        while True:
            # Reload config tiap siklus agar perubahan akun langsung terbaca tanpa restart bot
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception as e:
                print(f"{RED}✗ Gagal membaca accounts.json: {e}{RESET}")
                time.sleep(10)
                continue

            settings = config.get("settings", {})
            loop_mode = settings.get("loop_mode", True)
            loop_hours = settings.get("loop_interval_hours", 6)

            print(f"{MAGENTA}{BOLD}[Siklus #{cycle_count}]{RESET}")
            run_all_accounts(config)
            cycle_count += 1

            if not loop_mode:
                print(f"\n{CYAN}[ℹ️] Mode loop nonaktif (loop_mode: false). Selesai.{RESET}")
                break

            interval_seconds = int(loop_hours * 3600)
            print(f"\n💤 Mode 24/7 Aktif. Siklus berikutnya dalam {BOLD}{loop_hours} jam{RESET}.")
            sleep_with_countdown(interval_seconds)
            print(f"\n🔄 {CYAN}Memulai siklus baru...{RESET}")
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}🛑 Bot dihentikan oleh pengguna (Ctrl+C). Sampai jumpa!{RESET}\n")

if __name__ == "__main__":
    main()
