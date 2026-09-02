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
import datetime
import requests

API_BASE = "https://api.9chain.com/v2"

# Terminal Color Codes & Styles (ANSI)
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"

# Palette
C_PRIMARY = "\033[38;5;39m"     # Neon Sky Blue
C_ACCENT = "\033[38;5;220m"     # Gold / Yellow
C_SUCCESS = "\033[38;5;48m"     # Mint Green
C_ERROR = "\033[38;5;196m"      # Bright Red
C_WARN = "\033[38;5;208m"       # Orange
C_PURPLE = "\033[38;5;141m"     # Lavender
C_CYAN = "\033[38;5;51m"        # Cyan
C_MUTED = "\033[38;5;243m"      # Gray
C_BG_DARK = "\033[48;5;236m"

BANNER = f"""{C_PRIMARY}{BOLD}
  ██████╗  ██████╗██╗  ██╗ █████╗ ██╗███╗   ██╗
  ██╔══██╗██╔════╝██║  ██║██╔══██╗██║████╗  ██║
  ╚██████╔╝██║     ███████║███████║██║██╔██╗ ██║
   ╚═══██║ ██║     ██╔══██║██╔══██║██║██║╚██╗██║
  ██████╔╝ ╚██████╗██║  ██║██║  ██║██║██║ ╚████║
  ╚═════╝   ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
{RESET}{C_ACCENT}  ⚡ 9Chain Virtual Node 24/7 Automation Suite {RESET}{C_MUTED}| v2.2-pro{RESET}
{C_MUTED}  ─────────────────────────────────────────────────────────────{RESET}
"""

PRAYER_MESSAGES = [
    "Semoga ekosistem 9Chain semakin sukses, berkah, dan maju untuk semua.",
    "Wishing health, happiness, and peace for everyone in 9Chain community.",
    "May this project bring good fortune and growth to all nodes.",
    "Semoga hari ini penuh berkah dan kelancaran untuk kita semua.",
    "Peace, prosperity, and blessings to the global 9Chain family.",
    "Keep building, keep growing, wishing success for 9Chain testnet and mainnet."
]

def mask_email(email):
    """Menyamarkan email untuk privasi dan keamanan tampilan log."""
    if not email or "@" not in email:
        return email
    user, domain = email.split("@", 1)
    if len(user) <= 3:
        masked_user = user[0] + "*"
    else:
        masked_user = user[:2] + "*" * (len(user) - 3) + user[-1]
    return f"{masked_user}@{domain}"


def format_num(val):
    """Format angka dengan pemisah koma ribuan."""
    try:
        f = float(val)
        return f"{f:,.1f}" if f % 1 != 0 else f"{int(f):,}"
    except Exception:
        return str(val)


def render_progress_bar(current, total, bar_length=20):
    """Menghasilkan string progress bar visual yang menarik."""
    if total <= 0:
        percent = 100
        filled = bar_length
    else:
        percent = min(100, int((current / total) * 100))
        filled = int(bar_length * current // total)
    
    bar = "█" * filled + "░" * (bar_length - filled)
    return f"{C_PRIMARY}[{C_SUCCESS}{bar}{C_PRIMARY}]{RESET} {C_ACCENT}{percent}%{RESET}"


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
            "quests_claimed": 0,
            "pray_status": "Skipped"
        }

    def badge(self, tag, color=C_PRIMARY):
        return f"{color}{BOLD} {tag} {RESET}"

    def log(self, tag, message, level="INFO"):
        color_map = {
            "AUTH": C_PURPLE,
            "NODE": C_PRIMARY,
            "DAILY": C_ACCENT,
            "TAP": C_CYAN,
            "UPGRADE": C_SUCCESS,
            "QUEST": C_WARN,
            "PRAY": C_PURPLE
        }
        icon_map = {
            "INFO": f"{C_PRIMARY}ℹ{RESET}",
            "SUCCESS": f"{C_SUCCESS}✓{RESET}",
            "WARN": f"{C_WARN}▲{RESET}",
            "ERROR": f"{C_ERROR}✗{RESET}"
        }
        tag_color = color_map.get(tag, C_PRIMARY)
        icon = icon_map.get(level, f"{C_PRIMARY}•{RESET}")
        
        tag_badge = f"{tag_color}{BOLD}[{tag}]{RESET}"
        print(f"  {icon} {tag_badge:<17} {message}")

    def login(self):
        """Melakukan login headless via Email & Password jika belum memiliki access token."""
        if self.token and not self.token.startswith("PASTE_"):
            return True

        if not self.email or not self.password or self.email.startswith("akun") or self.email.startswith("user@"):
            self.log("AUTH", "Email / Password belum dikonfigurasi di accounts.json", "ERROR")
            return False

        masked = mask_email(self.email)
        self.log("AUTH", f"Autentikasi headless untuk {BOLD}{masked}{RESET}...", "INFO")
        
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
                        self.log("AUTH", f"Login Berhasil! Sesi JWT aktif.", "SUCCESS")
                        return True
                    else:
                        self.log("AUTH", f"Format respon login tidak dikenali: {res_data}", "ERROR")
                        return False
                else:
                    err_msg = res.json().get("message") or res.json().get("error", {}).get("message") or f"HTTP {res.status_code}"
                    self.log("AUTH", f"Gagal login: {err_msg}", "ERROR")
                    return False
            except Exception as e:
                self.log("AUTH", f"Percobaan {attempt}/3 gagal ({e}). Mengulang...", "WARN")
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
        try:
            res = self.session.post(f"{API_BASE}/me/check-in", timeout=15)
            if res.status_code in [200, 201]:
                data = res.json()
                reward = data.get("reward") or data.get("data", {}).get("reward", 0)
                already = data.get("alreadyCheckedIn", False) or data.get("data", {}).get("alreadyCheckedIn", False)
                if already:
                    self.stats["daily_gift"] = "Already Claimed"
                    self.log("DAILY", "Daily Gift hari ini sudah diklaim sebelumnya.", "INFO")
                else:
                    self.stats["daily_gift"] = f"+{reward} LOVE9"
                    self.log("DAILY", f"Daily Gift Berhasil Diklaim! {BOLD}{C_SUCCESS}+{reward} LOVE9{RESET}", "SUCCESS")
            elif res.status_code == 400:
                self.stats["daily_gift"] = "Already Claimed"
                self.log("DAILY", "Daily Gift sudah diklaim hari ini.", "INFO")
            else:
                err = res.json().get("error", {}).get("message", f"HTTP {res.status_code}")
                self.stats["daily_gift"] = "Failed"
                self.log("DAILY", f"Respon check-in: {err}", "WARN")
        except Exception as e:
            self.stats["daily_gift"] = "Error"
            self.log("DAILY", f"Error check-in: {e}", "WARN")

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

                tier_name = f"Tier {self.stats['tier']}"
                xp_formatted = format_num(self.stats['xp_total'])
                rate_formatted = format_num(self.stats['contribution_rate'])
                
                info_line = (
                    f"Node: {BOLD}{C_ACCENT}{tier_name}{RESET} │ "
                    f"Saldo: {BOLD}{C_SUCCESS}{xp_formatted} LOVE9{RESET} │ "
                    f"Rate: {BOLD}{C_CYAN}{rate_formatted}/jam{RESET} │ "
                    f"Tap: {BOLD}{self.stats['taps_remaining']}{RESET}"
                )
                self.log("NODE", info_line, "SUCCESS")
                return data
            elif res.status_code == 401:
                self.log("NODE", "Token Kedaluwarsa (HTTP 401). Butuh login ulang.", "ERROR")
                return None
            else:
                err = res.json().get("error", {}).get("message", f"HTTP {res.status_code}")
                self.log("NODE", f"Error server: {err}", "ERROR")
                return None
        except Exception as e:
            self.log("NODE", f"Error koneksi state: {e}", "ERROR")
            return None

    def push_taps(self, max_taps=1000, batch_size=5, delay_min=1.0, delay_max=2.5):
        """Melakukan auto-tap / PUSH secara bertahap, santai, dengan live progress bar."""
        taps_to_do = self.stats["taps_remaining"]
        if max_taps:
            taps_to_do = min(taps_to_do, max_taps)

        if taps_to_do <= 0:
            self.log("TAP", "Kuota PUSH tap harian sudah habis (0 sisa).", "INFO")
            return

        total_pushed = 0
        self.log("TAP", f"Memulai Auto-Push {BOLD}{taps_to_do} Taps{RESET} (kecepatan ~{batch_size} taps/request)...", "INFO")

        while total_pushed < taps_to_do:
            if batch_size > 3:
                current_batch = random.randint(max(1, batch_size - 2), batch_size + 2)
            else:
                current_batch = batch_size

            count = min(current_batch, taps_to_do - total_pushed)
            try:
                res = self.session.post(f"{API_BASE}/program/tap", json={"count": count}, timeout=15)
                if res.status_code in [200, 201]:
                    data = res.json().get("data", res.json())
                    state = data.get("state", data)
                    total_pushed += count
                    self.stats["xp_total"] = str(state.get("xpTotal", self.stats["xp_total"]))
                    remaining = state.get("tapsRemaining", 0)

                    pbar = render_progress_bar(total_pushed, taps_to_do, bar_length=15)
                    sys.stdout.write(f"\r  {C_CYAN}⚡ [TAP]{RESET} {pbar} ({total_pushed}/{taps_to_do}) │ +{count} taps │ Sisa: {remaining}   ")
                    sys.stdout.flush()

                    if remaining == 0:
                        break

                    sleep_time = random.uniform(delay_min, delay_max)
                    time.sleep(sleep_time)
                else:
                    err = res.json().get("error", {}).get("message", f"HTTP {res.status_code}")
                    print()
                    self.log("TAP", f"PUSH Terhenti: {err}", "WARN")
                    break
            except Exception as e:
                print()
                self.log("TAP", f"Error saat PUSH: {e}", "WARN")
                break

        print() # Baris baru setelah progress bar selesai
        self.stats["taps_done"] = total_pushed
        self.log("TAP", f"Selesai! Berhasil menambahkan {BOLD}{C_SUCCESS}+{total_pushed} Taps{RESET} ke node.", "SUCCESS")

    def auto_upgrade_components(self):
        """Mengecek katalog hardware dan otomatis menaikkan level modul yang terjangkau."""
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
                        self.log("UPGRADE", f"Poin cukup ({format_num(current_xp)} >= {format_num(cost)}). Upgrade {BOLD}{key.upper()}{RESET} ke Lv.{next_lvl}...", "INFO")
                        up_res = self.session.post(f"{API_BASE}/program/upgrade", json={
                            "componentKey": key,
                            "toLevel": next_lvl
                        }, timeout=15)

                        if up_res.status_code in [200, 201]:
                            self.log("UPGRADE", f"Upgrade Modul {BOLD}{key.upper()} Lv.{next_lvl}{RESET} Sukses!", "SUCCESS")
                            self.stats["upgrades"].append(f"{key.upper()} Lv.{next_lvl}")
                            current_xp -= cost
                            self.stats["xp_total"] = str(current_xp)
                        else:
                            err = up_res.json().get("error", {}).get("message", "")
                            self.log("UPGRADE", f"Upgrade {key.upper()} gagal: {err}", "WARN")
        except Exception as e:
            self.log("UPGRADE", f"Error saat cek upgrade: {e}", "WARN")

    def auto_upgrade_node_tier(self):
        """Mengecek apakah poin mencukupi untuk upgrade tingkatan Node Tier (Tier 1 -> Tier 2 -> Tier 3)."""
        try:
            res = self.session.get(f"{API_BASE}/program/catalog", timeout=15)
            if res.status_code != 200:
                return

            data = res.json().get("data", res.json())
            tiers = data.get("tiers", [])
            current_tier = int(self.stats.get("tier", 1))
            current_xp = float(self.stats.get("xp_total", "0"))

            for t in tiers:
                tier_num = t.get("tier") or t.get("level")
                if tier_num == current_tier + 1:
                    cost = float(t.get("cost", 0) or t.get("xpCost", 0) or t.get("price", 0))
                    if cost > 0 and current_xp >= cost:
                        self.log("UPGRADE", f"Saldo cukup! Upgrade tingkatan Node ke {BOLD}Tier {tier_num}{RESET}...", "INFO")
                        up_res = self.session.post(
                            f"{API_BASE}/program/node/upgrade",
                            json={"toTier": tier_num},
                            timeout=15
                        )
                        if up_res.status_code in [200, 201]:
                            self.stats["tier"] = tier_num
                            self.stats["upgrades"].append(f"Node Tier {tier_num}")
                            self.log("UPGRADE", f"Selamat! Node naik ke {BOLD}{C_ACCENT}Tier {tier_num}{RESET}!", "SUCCESS")
                            current_xp -= cost
                            self.stats["xp_total"] = str(current_xp)
                        else:
                            err = up_res.json().get("error", {}).get("message", "")
                            self.log("UPGRADE", f"Upgrade Node Tier {tier_num} gagal: {err}", "WARN")
        except Exception as e:
            self.log("UPGRADE", f"Error saat cek upgrade node tier: {e}", "WARN")

    def claim_quests(self):
        """Mengecek misi harian & sosial, lalu otomatis mengklaim reward yang sudah selesai."""
        try:
            res = self.session.get(f"{API_BASE}/program/quests", timeout=15)
            if res.status_code != 200:
                return

            quests = res.json().get("data", {}).get("quests", [])
            claimed_count = 0

            for q in quests:
                quest_key = q.get("key") or q.get("questKey")
                is_completed = q.get("completed", False) or q.get("isCompleted", False) or q.get("canClaim", False)
                is_claimed = q.get("claimed", False) or q.get("isClaimed", False)

                if is_completed and not is_claimed and quest_key:
                    c_res = self.session.post(f"{API_BASE}/program/quests/claim", json={"questKey": quest_key}, timeout=15)
                    if c_res.status_code in [200, 201]:
                        self.log("QUEST", f"Klaim Reward Misi '{BOLD}{quest_key}{RESET}' Sukses!", "SUCCESS")
                        claimed_count += 1
            
            self.stats["quests_claimed"] = claimed_count
            if claimed_count > 0:
                self.log("QUEST", f"Total {BOLD}{claimed_count} Quest{RESET} berhasil diklaim.", "SUCCESS")
        except Exception as e:
            self.log("QUEST", f"Error cek quest: {e}", "WARN")

    def send_prayer(self, room_slug="together", custom_text=None):
        """Mengirim pesan doa komunitas harian ke room Pray Together."""
        try:
            self.session.post(f"{API_BASE}/prayer/rooms/{room_slug}/join", json={}, timeout=15)
            text = custom_text or random.choice(PRAYER_MESSAGES)
            res = self.session.post(
                f"{API_BASE}/prayer/rooms/{room_slug}/messages",
                json={"text": text},
                timeout=15
            )
            if res.status_code in [200, 201]:
                self.stats["pray_status"] = "Terkirim"
                short_text = (text[:35] + "...") if len(text) > 35 else text
                self.log("PRAY", f"Doa harian terkirim di room '{room_slug}': {ITALIC}\"{short_text}\"{RESET}", "SUCCESS")
            else:
                err = res.json().get("error", {}).get("message") or res.json().get("message") or f"HTTP {res.status_code}"
                self.stats["pray_status"] = "Gagal"
                self.log("PRAY", f"Kirim doa gagal: {err}", "WARN")
        except Exception as e:
            self.stats["pray_status"] = "Error"
            self.log("PRAY", f"Error Pray Together: {e}", "WARN")


def print_account_card(idx, total, name, email):
    """Menampilkan card header akun yang modern dan estetik."""
    masked = mask_email(email) if email else "Token Auth"
    width = 65
    
    title_left = f" 👤 AKUN [{idx}/{total}]: {name} "
    title_right = f" {masked} "
    
    border_len = width - len(title_left) - len(title_right) - 4
    if border_len < 2:
        border_len = 2
    
    print(f"\n{C_PRIMARY}╭─{C_ACCENT}{BOLD}{title_left}{C_PRIMARY}{'─' * border_len}{C_MUTED}{title_right}{C_PRIMARY}─╮{RESET}")


def print_account_card_footer():
    print(f"{C_PRIMARY}╰─────────────────────────────────────────────────────────────────╯{RESET}")


def print_summary_table(summary_stats):
    """Menampilkan tabel ringkasan hasil eksekusi seluruh akun."""
    print(f"\n{C_ACCENT}{BOLD}╭────────────────────────────────────────────────────────────────────────────────────────────╮{RESET}")
    print(f"{C_ACCENT}{BOLD}│ 📊 RINGKASAN HASIL SIKLUS EKSEKUSI (TOTAL {len(summary_stats)} AKUN)                                     │{RESET}")
    print(f"{C_ACCENT}{BOLD}├────┬────────────────────────┬──────┬────────────────┬──────────────┬────────────┬──────────────┤{RESET}")
    print(f"{C_ACCENT}{BOLD}│ No │ Nama Akun              │ Tier │ Total LOVE9    │ Rate / Jam   │ Tap PUSH   │ Hadiah Daily │{RESET}")
    print(f"{C_ACCENT}{BOLD}├────┼────────────────────────┼──────┼────────────────┼──────────────┼────────────┼──────────────┤{RESET}")

    for idx, s in enumerate(summary_stats, start=1):
        name = s["name"][:20]
        tier_str = f"T{s['tier']}"
        xp_str = format_num(s["xp_total"])
        rate_str = f"+{format_num(s['contribution_rate'])}/h"
        taps_str = f"+{s['taps_done']}" if s['taps_done'] > 0 else "0"
        gift_str = s.get("daily_gift", "-")
        if "Claimed" in gift_str or "+" in gift_str:
            gift_fmt = f"{C_SUCCESS}✓ OK{RESET}"
        elif gift_str == "Already Claimed":
            gift_fmt = f"{C_MUTED}Sudah{RESET}"
        else:
            gift_fmt = f"{C_MUTED}{gift_str[:10]}{RESET}"

        status_col = C_SUCCESS if s["status"] == "Success" else C_ERROR

        print(
            f"│ {C_MUTED}{idx:02d}{RESET} │ "
            f"{status_col}{name:<22}{RESET} │ "
            f"{C_ACCENT}{tier_str:^4}{RESET} │ "
            f"{C_SUCCESS}{xp_str:>14}{RESET} │ "
            f"{C_CYAN}{rate_str:>12}{RESET} │ "
            f"{BOLD}{taps_str:>10}{RESET} │ "
            f"{gift_fmt:<12} │"
        )

    print(f"{C_ACCENT}{BOLD}╰────┴────────────────────────┴──────┴────────────────┴──────────────┴────────────┴──────────────╯{RESET}")


def send_telegram_notification(tg_config, all_stats):
    """Mengirim ringkasan laporan ke Telegram."""
    if not tg_config.get("enabled"):
        return

    bot_token = tg_config.get("bot_token")
    chat_id = tg_config.get("chat_id")
    if not bot_token or not chat_id or "YOUR_" in bot_token:
        return

    text = "📊 <b>Laporan 9Chain 24/7 Bot</b>\n"
    text += f"⏰ Waktu: <code>{time.strftime('%Y-%m-%d %H:%M:%S')}</code>\n"
    text += "────────────────────────\n"

    for s in all_stats:
        status_icon = "✅" if s["status"] == "Success" else "❌"
        upgrades_str = ", ".join(s["upgrades"]) if s["upgrades"] else "None"
        
        text += f"{status_icon} <b>{s['name']}</b> (Tier {s['tier']})\n"
        text += f"• Saldo LOVE9: <b>{format_num(s['xp_total'])}</b>\n"
        text += f"• Mining Rate: <b>+{format_num(s['contribution_rate'])}/jam</b>\n"
        text += f"• Tap PUSH: <b>+{s['taps_done']}</b>\n"
        text += f"• Daily Gift: <b>{s.get('daily_gift', '-')}</b>\n"
        text += f"• Pray Chat: <b>{s.get('pray_status', '-')}</b>\n"
        text += f"• Upgrade: {upgrades_str}\n"
        text += "────────────────────────\n"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=15)
        print(f"\n  {C_SUCCESS}[✓] Notifikasi ringkasan terkirim ke Telegram!{RESET}")
    except Exception as e:
        print(f"\n  {C_ERROR}[!] Gagal mengirim notifikasi Telegram: {e}{RESET}")


def sleep_with_countdown(seconds, cycle_num=1):
    """Menampilkan hitung mundur waktu tunggu dengan tampilan jam berikutnya."""
    next_time = (datetime.datetime.now() + datetime.timedelta(seconds=seconds)).strftime("%H:%M:%S WIB")
    
    spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    spin_idx = 0

    while seconds > 0:
        hrs = seconds // 3600
        mins = (seconds % 3600) // 60
        secs = seconds % 60
        spin_char = spinner[spin_idx % len(spinner)]
        spin_idx += 1

        sys.stdout.write(
            f"\r  {C_PRIMARY}{spin_char}{RESET} {C_MUTED}Mode 24/7 Standby:{RESET} "
            f"{C_ACCENT}{BOLD}{hrs:02d}:{mins:02d}:{secs:02d}{RESET} "
            f"{C_MUTED}│ Siklus #{cycle_num} dimulai pukul {BOLD}{next_time}{RESET}   "
        )
        sys.stdout.flush()
        time.sleep(1)
        seconds -= 1
    
    sys.stdout.write("\r" + " " * 85 + "\r")
    sys.stdout.flush()


def run_all_accounts(config):
    """Menjalankan otomasi untuk seluruh akun terdaftar."""
    settings = config.get("settings", {})
    accounts = config.get("accounts", [])
    tg_config = config.get("telegram", {})

    print(f"  {C_MUTED}Waktu Mulai:{RESET} {BOLD}{time.strftime('%Y-%m-%d %H:%M:%S')}{RESET} │ {C_MUTED}Total Antrean:{RESET} {BOLD}{len(accounts)} Akun{RESET}")

    summary_stats = []

    for idx, acc in enumerate(accounts, start=1):
        name = acc.get('name', f'Akun {idx}')
        email = acc.get('email', '')
        
        print_account_card(idx, len(accounts), name, email)
        bot = NineChainBot(acc)

        # Login jika token belum tersedia
        if not bot.token or bot.token.startswith("PASTE_"):
            if not bot.login():
                print_account_card_footer()
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
                batch_size = int(settings.get("tap_batch_size", 5))
                delay_min = float(settings.get("tap_delay_min", 1.0))
                delay_max = float(settings.get("tap_delay_max", 2.5))
                bot.push_taps(
                    max_taps=settings.get("max_taps", 1000),
                    batch_size=batch_size,
                    delay_min=delay_min,
                    delay_max=delay_max
                )

            # 4. Auto Upgrade Modul Hardware (CPU, RAM, Anti-Sybil)
            if settings.get("auto_upgrade_node", True) or settings.get("auto_upgrade_components", True):
                bot.auto_upgrade_components()

            # 5. Auto Upgrade Node Tier (Tier 1 -> Tier 2 -> Tier 3)
            if settings.get("auto_upgrade_node_tier", True):
                bot.auto_upgrade_node_tier()

            # 6. Auto Klaim Quest (Quests harian / sosial yang sudah selesai)
            if settings.get("auto_claim_quests", True):
                bot.claim_quests()

            # 7. Auto Chat Pray Together (Doa Harian Komunitas)
            if settings.get("auto_pray", True):
                room_slug = settings.get("pray_room", "together")
                custom_msgs = settings.get("prayer_messages", [])
                chosen_msg = random.choice(custom_msgs) if custom_msgs else None
                bot.send_prayer(room_slug=room_slug, custom_text=chosen_msg)

            # Ambil state terakhir setelah semua aksi
            bot.fetch_state()

        print_account_card_footer()
        summary_stats.append(bot.stats)

        # Jeda natural antar akun
        if idx < len(accounts):
            pause = random.randint(2, 4)
            time.sleep(pause)

    # Tampilkan Tabel Ringkasan Estetik
    print_summary_table(summary_stats)

    # Kirim Laporan Telegram
    send_telegram_notification(tg_config, summary_stats)


def main():
    print(BANNER)
    config_path = os.path.join(os.path.dirname(__file__), "accounts.json")
    example_path = os.path.join(os.path.dirname(__file__), "accounts.example.json")

    if not os.path.exists(config_path):
        if os.path.exists(example_path):
            import shutil
            shutil.copy(example_path, config_path)
            print(f"  {C_WARN}[!] File accounts.json otomatis dibuat dari template accounts.example.json.{RESET}")
            print(f"  {C_MUTED}[*] Silakan edit file accounts.json dan masukkan akun Anda:{RESET}")
            print(f"      {BOLD}nano accounts.json{RESET}\n")
        else:
            print(f"  {C_ERROR}✗ File {config_path} tidak ditemukan!{RESET}")
        return

    cycle_count = 1
    try:
        while True:
            # Reload config tiap siklus agar perubahan akun langsung terbaca tanpa restart bot
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception as e:
                print(f"  {C_ERROR}✗ Gagal membaca accounts.json: {e}{RESET}")
                time.sleep(10)
                continue

            settings = config.get("settings", {})
            loop_mode = settings.get("loop_mode", True)
            loop_hours = settings.get("loop_interval_hours", 6)

            print(f"\n{C_ACCENT}{BOLD}▶ SIKLUS #{cycle_count}{RESET} {C_MUTED}(Loop Mode 24/7: {'Aktif' if loop_mode else 'Nonaktif'}){RESET}")
            run_all_accounts(config)
            cycle_count += 1

            if not loop_mode:
                print(f"\n  {C_PRIMARY}[ℹ] Mode loop nonaktif (loop_mode: false). Selesai.{RESET}\n")
                break

            interval_seconds = int(loop_hours * 3600)
            print(f"\n{C_SUCCESS}{BOLD}  ✓ Siklus selesai.{RESET} Memasuki mode standby selama {BOLD}{loop_hours} jam{RESET}.")
            sleep_with_countdown(interval_seconds, cycle_num=cycle_count)
            print(f"\n{C_PRIMARY}🔄 Memulai siklus #{cycle_count}...{RESET}")
    except KeyboardInterrupt:
        print(f"\n\n  {C_WARN}🛑 Bot dihentikan oleh pengguna (Ctrl+C). Sampai jumpa!{RESET}\n")

if __name__ == "__main__":
    main()
