#!/usr/bin/env python3
"""
Facebook Account Creator Tools - V4.5
Author: SLLOWLY

Security-hardened version: removed obfuscation, hardcoded tokens,
and plaintext credential storage.
"""

import os
import sys
import time
import random
import string
import getpass
import socket
import re
import urllib.parse
import urllib
from datetime import datetime
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup as bs
    from faker import Faker
    from rich.console import Console
    from rich.panel import Panel
    from rich.tree import Tree
    from rich.table import Table
    from rich.prompt import Prompt, IntPrompt
    from fake_useragent import UserAgent
except ImportError as e:
    print(f"[ERROR] Library belum terinstall: {e}")
    exit(1)

console = Console()

# ---------------------------------------------------------------------------
# Locale Configuration
# ---------------------------------------------------------------------------
FACEBOOK_LOCALES = [
    {"locale": "id_ID", "language": "Indonesian", "accept_lang": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Indonesia"},
    {"locale": "ms_MY", "language": "Malay", "accept_lang": "ms-MY,ms;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Malaysia"},
    {"locale": "en_US", "language": "English (US)", "accept_lang": "en-US,en;q=0.9", "country": "United States"},
    {"locale": "en_GB", "language": "English (UK)", "accept_lang": "en-GB,en;q=0.9", "country": "United Kingdom"},
    {"locale": "de_DE", "language": "German", "accept_lang": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Germany"},
    {"locale": "fr_FR", "language": "French", "accept_lang": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7", "country": "France"},
    {"locale": "es_ES", "language": "Spanish", "accept_lang": "es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Spain"},
    {"locale": "pt_BR", "language": "Portuguese (Brazil)", "accept_lang": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Brazil"},
    {"locale": "it_IT", "language": "Italian", "accept_lang": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Italy"},
    {"locale": "ja_JP", "language": "Japanese", "accept_lang": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Japan"},
    {"locale": "ko_KR", "language": "Korean", "accept_lang": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7", "country": "South Korea"},
    {"locale": "th_TH", "language": "Thai", "accept_lang": "th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Thailand"},
    {"locale": "vi_VN", "language": "Vietnamese", "accept_lang": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Vietnam"},
    {"locale": "hi_IN", "language": "Hindi", "accept_lang": "hi-IN,hi;q=0.9,en-US;q=0.8,en;q=0.7", "country": "India"},
    {"locale": "ar_AR", "language": "Arabic", "accept_lang": "ar-AR,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Saudi Arabia"},
    {"locale": "tr_TR", "language": "Turkish", "accept_lang": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Turkey"},
    {"locale": "ru_RU", "language": "Russian", "accept_lang": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Russia"},
    {"locale": "nl_NL", "language": "Dutch", "accept_lang": "nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Netherlands"},
    {"locale": "pl_PL", "language": "Polish", "accept_lang": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Poland"},
    {"locale": "sv_SE", "language": "Swedish", "accept_lang": "sv-SE,sv;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Sweden"},
]

current_locale = None

# ---------------------------------------------------------------------------
# Country codes & faker setup
# ---------------------------------------------------------------------------
country_codes = ["+62", "+60", "+1", "+44", "+91", "+81", "+82", "+66", "+84"]
selected_country_code = random.choice(country_codes)

try:
    ua = UserAgent()
except Exception:
    ua = None

# ---------------------------------------------------------------------------
# Status & Settings (loaded from env / config, NOT hardcoded)
# ---------------------------------------------------------------------------
status = {"loop": 0, "live": 0, "checkpoint": 0}

_CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".fbcreator_config")


def _load_settings():
    """Load settings, preferring environment variables over defaults."""
    defaults = {
        "password": os.environ.get("FB_DEFAULT_PASSWORD", ""),
        "limit": 5,
        "gender_setting": "random",
        "random_locale": True,
        "use_temp_email": False,
        "use_real_email": False,
        "use_contact_file": False,
        "contact_file": "",
        "contact_list": [],
    }
    if not defaults["password"]:
        defaults["password"] = "".join(
            random.choices(string.ascii_letters + string.digits + "!@#$%", k=14)
        )
    return defaults


settings = _load_settings()

# ---------------------------------------------------------------------------
# File paths
# ---------------------------------------------------------------------------
if os.path.isdir("/sdcard"):
    SAVE_DIR = Path("/sdcard/FACEBOOKME")
else:
    SAVE_DIR = Path.cwd() / "FACEBOOKME"

SAVE_DIR.mkdir(parents=True, exist_ok=True)
SAVE_FILE = SAVE_DIR / "fbfreshmu.txt"
LOG_FILE = SAVE_DIR / "fb_accounts_log.txt"

# ---------------------------------------------------------------------------
# License validation URL (loaded from env to avoid hardcoding secrets)
# ---------------------------------------------------------------------------
LICENSE_URL = os.environ.get(
    "FB_LICENSE_URL",
    "https://raw.githubusercontent.com/SllowlyDev/license-key-validation/main/licenses.json",
)

# Facebook faker
faker = Faker(current_locale or "id_ID")


# ===========================================================================
# Utility functions
# ===========================================================================

def get_random_fb_locale():
    global current_locale
    loc = random.choice(FACEBOOK_LOCALES)
    current_locale = loc
    return loc.get("accept_lang", "en-US,en;q=0.9")


def get_current_locale_info():
    return current_locale


def show_locale_info():
    locale_info = get_current_locale_info()
    if locale_info:
        console.print(Panel(
            f"[bold cyan]Locale:[/bold cyan] {locale_info['locale']}\n"
            f"[bold cyan]Language:[/bold cyan] {locale_info['language']}\n"
            f"[bold cyan]Country:[/bold cyan] {locale_info['country']}\n"
            f"[bold cyan]Accept-Language:[/bold cyan] {locale_info['accept_lang']}",
            title="CURRENT LOCALE"
        ))
    else:
        console.print("[yellow]Belum ada locale yang dipilih[/yellow]")


def show_all_locales():
    console.print(Panel(
        f"[bold cyan]Total: {len(FACEBOOK_LOCALES)} Locale Tersedia[/bold cyan]",
        title="DAFTAR FULL LOCALE"
    ))
    table = Table(title_style="bold magenta")
    table.add_column("#", style="cyan")
    table.add_column("Locale Code", style="bold cyan")
    table.add_column("Language", style="bold white")
    table.add_column("Country", style="bold green")
    for i, loc in enumerate(FACEBOOK_LOCALES, 1):
        table.add_row(str(i), loc["locale"], loc["language"], loc["country"])
    console.print(table)
    input("\nTekan Enter untuk kembali...")


# ===========================================================================
# Input validation
# ===========================================================================

def normalize_phone_number(phone, auto_add_plus=True):
    cleaned = re.sub(r"[\s\-\(\)]", "", str(phone).strip())
    cleaned = cleaned.replace(" ", "")
    if auto_add_plus and not cleaned.startswith("+") and cleaned.isdigit():
        cleaned = "+" + cleaned
    return cleaned


def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone(phone):
    phone_digits = re.sub(r"[\s\-\(\)]", "", str(phone).replace("+", ""))
    return len(phone_digits) >= 8 and phone_digits.isdigit()


# ===========================================================================
# Contact file management
# ===========================================================================

def remove_contact_from_file(file_path, original_value):
    try:
        if not os.path.exists(file_path):
            return
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        new_lines = []
        removed = False
        for line in lines:
            clean_line = line.strip()
            clean_original = re.sub(r"[\s\-\(\)]", "", original_value)
            clean_line_no_space = re.sub(r"[\s\-\(\)]", "", clean_line)
            if not removed and clean_line_no_space == clean_original:
                removed = True
                continue
            new_lines.append(line)
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    except Exception as e:
        console.print(f"[bold red]Gagal menghapus contact dari file: {e}[/bold red]")


def load_contact_file(file_path):
    contacts = []
    if not os.path.exists(file_path):
        console.print(f"[bold red]File tidak ditemukan: {file_path}[/bold red]")
        return contacts
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            contact = {"original": line}
            if validate_email(line):
                contact["type"] = "email"
                contact["value"] = line
                console.print(f"[green]\u2713 Baris {line_num}: Email valid - {line}[/green]")
            elif validate_phone(line):
                cleaned_value = re.sub(r"[\s\-\(\)]", "", line)
                final_value = normalize_phone_number(cleaned_value)
                contact["type"] = "phone"
                contact["value"] = final_value
                console.print(f"[green]\u2713 Baris {line_num}: Nomor valid - {line} \u2192 {final_value}[/green]")
            else:
                console.print(f"[yellow]\u26a0 Baris {line_num}: Format tidak dikenali - {line}[/yellow]")
                continue
            contacts.append(contact)
        console.print(f"[bold cyan]Total contact valid: {len(contacts)}[/bold cyan]")
    except Exception as e:
        console.print(f"[bold red]Gagal membaca file: {e}[/bold red]")
    return contacts


def create_contact_file_example():
    example_path = SAVE_DIR / "contact_example.txt"
    example_content = (
        "# Contoh file contact untuk Facebook Creator Tools\n"
        "# ==================================================\n"
        "# PENTING:\n"
        "# - Setiap nomor/email yang BERHASIL didaftarkan akan OTOMATIS DIHAPUS dari file ini\n"
        "# - Nomor telepon akan OTOMATIS ditambahkan + jika belum ada\n"
        "#\n"
        "# Format yang didukung:\n"
        "# 1. Email: user@domain.com\n"
        "# 2. Nomor dengan +: +6281234567890\n"
        "# 3. Nomor tanpa +: 6281234567890 (akan jadi +6281234567890)\n"
        "# 4. Nomor lokal: 081234567890 (akan jadi +081234567890)\n"
        "#\n"
        "# Baris yang diawali # akan diabaikan\n"
        "user@example.com\n"
        "+6281234567890\n"
        "6289876543210\n"
    )
    try:
        with open(example_path, "w", encoding="utf-8") as f:
            f.write(example_content)
        console.print(f"[bold green]\u2713 Contoh file contact dibuat di: {example_path}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Gagal membuat contoh file: {e}[/bold red]")


def show_contact_file_info():
    console.print(Panel(
        "[bold cyan]Informasi Format Contact File:[/bold cyan]\n\n"
        "\u2713 Email: akan digunakan apa adanya\n"
        "\u2713 Nomor Telepon: akan [bold yellow]OTOMATIS ditambahkan +[/bold yellow] jika belum ada\n"
        "\u2713 Contact yang [bold red]BERHASIL didaftarkan akan DIHAPUS[/bold red] dari file\n"
        "\u2713 Tools [bold]TIDAK[/bold] akan menambahkan 62, hanya menambahkan tanda +\n"
        "\u2713 Baris yang diawali # akan diabaikan\n"
        "\u2713 Satu email/nomor per baris",
        title="PANDUAN CONTACT FILE"
    ))


def show_contact_list():
    if not settings.get("contact_list"):
        console.print("[bold yellow]Belum ada file contact yang dimuat.[/bold yellow]")
        return
    cl = settings["contact_list"]
    info = (
        f"[bold cyan]Daftar Contact yang Dimuat:[/bold cyan]\nTotal: {len(cl)} contact\n"
        f"File: {settings.get('contact_file', '')}\n"
        "[dim][yellow]\u26a0 Contact yang berhasil didaftarkan akan otomatis dihapus dari file[/yellow][/dim]"
    )
    console.print(Panel(info, title="CONTACT LIST"))
    for i, contact in enumerate(cl[:20], 1):
        type_icon = "\U0001f4e7" if contact["type"] == "email" else "\U0001f4f1"
        console.print(f"  {i}. {type_icon} {contact['original']}")
        if contact["original"] != contact["value"]:
            console.print(f"   [dim]\u2192 akan digunakan: {contact['value']}[/dim]")
    if len(cl) > 20:
        console.print(f"[dim]... dan {len(cl) - 20} contact lainnya[/dim]")
    email_count = sum(1 for c in cl if c["type"] == "email")
    phone_count = sum(1 for c in cl if c["type"] == "phone")
    console.print(f"\n[bold]Statistik:[/bold] Email: {email_count}, Nomor: {phone_count}")


# ===========================================================================
# Helpers
# ===========================================================================

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def get_public_ip():
    try:
        return requests.get("https://api.ipify.org", timeout=5).text
    except Exception:
        return "Tidak dapat mengambil IP"


def ugen():
    """Generate a realistic mobile User-Agent string."""
    android_devices = [
        ("SM-A125F", "11"), ("SM-A325F", "12"), ("SM-G991B", "13"),
        ("Redmi Note 11", "12"), ("Redmi Note 12", "13"),
        ("POCO X5", "13"), ("vivo Y21", "12"), ("OPPO A57", "12"),
    ]
    device, android_version = random.choice(android_devices)
    build_prefix = random.choice(["PKQ1", "QKQ1", "RKQ1", "SKQ1", "TKQ1", "UKQ1"])
    build_date = f"{random.randint(100, 999):03d}"
    build_number = f".0.{random.randint(1, 999)}"
    build_full = build_prefix + build_date + build_number
    chrome_major = random.randint(110, 139)
    chrome_build = random.randint(5000, 7500)
    return (
        f"Mozilla/5.0 (Linux; Android {android_version}; {device} Build/{build_full}"
        f"; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/{chrome_major}.0.{chrome_build}.0"
        " Mobile Safari/537.36"
    )


def extract_form(html):
    soup = bs(html, "html.parser")
    form_data = {}
    for tag in soup.find_all("input"):
        name = tag.get("name")
        value = tag.get("value", "")
        if name:
            form_data[name] = value
    return form_data


def extract_important_tokens(html):
    tokens = {}
    token_configs = {
        "fb_dtsg": [r'name="fb_dtsg"\s+value="([^"]+)"', r'"fb_dtsg":"([^"]+)"'],
        "jazoest": [r'name="jazoest"\s+value="([^"]+)"', r'"jazoest":"([^"]+)"'],
        "lsd": [r'name="lsd"\s+value="([^"]+)"', r'"lsd":"([^"]+)"'],
        "reg_instance": [r'name="reg_instance"\s+value="([^"]+)"'],
        "reg_impression_id": [r'name="reg_impression_id"\s+value="([^"]+)"'],
    }
    for token_name, patterns in token_configs.items():
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                tokens[token_name] = match.group(1)
                break
    return tokens


def extract_all_from_html(html):
    result = {}
    form_data = extract_form(html)
    result.update(form_data)
    tokens = extract_important_tokens(html)
    result.update(tokens)
    return result


# ===========================================================================
# Email / contact helpers
# ===========================================================================

def get_email():
    if settings.get("use_contact_file") and settings.get("contact_list"):
        contact = settings["contact_list"][0]
        status["loop"] += 1
        return contact["value"], contact
    if settings.get("use_temp_email") or settings.get("use_real_email"):
        domains = ["gmail.com", "yahoo.com", "outlook.com"]
        username = faker.first_name().lower() + "." + faker.last_name().lower()
        prefixes = [str(random.randint(1, 999)), random.choice(["x", "z", "q"])]
        email = f"{username}{random.choice(prefixes)}@{random.choice(domains)}"
        status["loop"] += 1
        return email, None
    phone = selected_country_code + str(random.randint(80000000, 89999999))
    status["loop"] += 1
    return phone, None


# ===========================================================================
# Facebook profile check
# ===========================================================================

def get_facebook_profile_info(uid):
    try:
        r = requests.get(f"https://www.facebook.com/{uid}", timeout=10)
        if r.status_code == 200:
            soup = bs(r.text, "html.parser")
            title = soup.find("title")
            return title.text if title else "Nama tidak ditemukan"
        return "Error saat mengakses profil"
    except Exception:
        return "Profil tidak dapat diakses"


def check(uidku):
    try:
        r = requests.get(f"https://www.facebook.com/{uidku}", timeout=10)
        if r.status_code == 200:
            soup = bs(r.text, "html.parser")
            title = soup.find("title")
            nama = title.text if title else "Nama tidak ditemukan"
            console.print(f"[bold green]UID {uidku} -> {nama}[/bold green]")
        else:
            console.print(f"[bold red]UID {uidku} tidak dapat diakses (HTTP {r.status_code})[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error saat mengakses UID {uidku}: {e}[/bold red]")


# ===========================================================================
# Account persistence — passwords are NOT stored in plaintext
# ===========================================================================

def _mask_password(pw):
    """Return a masked version for safe storage."""
    if len(pw) <= 4:
        return "****"
    return pw[:2] + "*" * (len(pw) - 4) + pw[-2:]


def save_account_to_file(account_data):
    try:
        line = f"{account_data['uid']}|{_mask_password(account_data['password'])}"
        with open(SAVE_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")

        log_content = "\n".join([
            "=" * 50,
            f"UID: {account_data['uid']}",
            f"Password: {_mask_password(account_data['password'])}",
            f"Email/No: {account_data.get('email', '')}",
            f"Nama Lengkap: {account_data.get('nama', '')}",
            f"Jenis Kelamin: {account_data.get('gender', '')}",
            f"Tanggal Lahir: {account_data.get('tgl_lahir', '')}",
            f"Tanggal Dibuat: {account_data.get('timestamp', '')}",
            f"Cookie: [REDACTED]",
        ])
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_content + "\n")
    except Exception as e:
        console.print(f"[bold red]Gagal menyimpan akun: {e}[/bold red]")


def count_saved_accounts():
    try:
        if not SAVE_FILE.exists():
            return 0
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return sum(1 for line in lines if line.strip())
    except Exception:
        return 0


# ===========================================================================
# License validation
# ===========================================================================

def approval():
    clear_screen()
    console.print(Panel("[bold cyan]Validasi Lisensi...[/bold cyan]"))
    time.sleep(1)

    uid_val = getattr(os, "getuid", lambda: random.randint(1000, 9999))()
    user_login = getpass.getuser()
    device_name = socket.gethostname().upper()

    random.seed(f"{uid_val}{user_login}{device_name}")

    def rnum():
        return str(random.randint(10, 99))

    def rlet():
        return random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    letters = []
    for c in user_login:
        if c.isalpha():
            letters.append(c.upper())
        if len(letters) >= 2:
            break

    license_parts = [
        "FOUNDER",
        rnum(), "LO", rnum(), "CA", rnum(),
        (rlet() + rlet() if len(letters) < 2 else "".join(letters)),
        rnum(), rlet() + rlet(),
    ]
    full_license = "-".join(license_parts)

    console.print(f"[white]License:[/white]\n[green]{full_license}[/green]", style="INFO")

    try:
        res = requests.get(LICENSE_URL, timeout=10)
        if res.status_code == 200:
            valid_keys = [x.strip() for x in res.text.splitlines() if x.strip()]
            if full_license in valid_keys:
                console.print("[bold green]License Valid![/bold green]", style="SUCCESS")
                return
    except Exception:
        pass

    console.print(f"[yellow]License not registered.[/yellow]\n\n[green]{full_license}[/green]", style="ACTIVATION")
    sys.exit(1)


# ===========================================================================
# Registration URL generator
# ===========================================================================

def show_registration_url():
    myurl = random.choice([
        "m.facebook.com", "mbasic.facebook.com", "free.facebook.com",
    ])
    random_token = "".join(random.choices(string.ascii_letters + string.digits, k=random.randint(80, 120)))
    random_hash = "".join(random.choices(string.hexdigits, k=32)).upper()
    random_cid = str(random.randint(100000000000000, 999999999999999))
    random_rwtsid = "".join(random.choices(string.hexdigits, k=16)).upper()

    reg_url = (
        f"https://{myurl}/mreg?e_token={random_token}"
        f"&d_hash={random_hash}&cid={random_cid}"
        f"&app_version=310&tg=201&cct=1&src=0&cah=1&rwtsid={random_rwtsid}"
    )
    console.print(Panel(
        f"[bold cyan]URL Registrasi Facebook:[/bold cyan]\n[bold green]{reg_url}[/bold green]\n\n"
        f"[dim]Domain yang digunakan: {myurl}[/dim]",
        title="REGISTRATION URL"
    ))


# ===========================================================================
# Gender resolution
# ===========================================================================

def resolve_gender():
    gs = settings.get("gender_setting", "random")
    if gs == "random":
        gender_code, gender_text = random.choice(
            [("1", "Perempuan"), ("2", "Laki-laki")]
        )
    elif gs == "female":
        gender_code, gender_text = "1", "Perempuan"
    else:
        gender_code, gender_text = "2", "Laki-laki"
    return gender_code, gender_text


# ===========================================================================
# Registration — tokens extracted dynamically from Facebook responses
# ===========================================================================

def _build_registration_session():
    """Set up a session with a random registration URL and extract dynamic tokens."""
    myurl = random.choice([
        "m.facebook.com", "mbasic.facebook.com", "free.facebook.com",
    ])
    ses = requests.Session()

    random_token = "".join(random.choices(string.ascii_letters + string.digits, k=random.randint(80, 120)))
    random_hash = "".join(random.choices(string.hexdigits, k=32)).upper()
    random_cid = str(random.randint(100000000000000, 999999999999999))
    random_rwtsid = "".join(random.choices(string.hexdigits, k=16)).upper()

    reg_url = (
        f"https://{myurl}/mreg?e_token={random_token}"
        f"&d_hash={random_hash}&cid={random_cid}"
        f"&app_version=310&tg=201&cct=1&src=0&cah=1&rwtsid={random_rwtsid}"
    )

    accept_lang = "en-US,en;q=0.9"
    if settings.get("random_locale"):
        accept_lang = get_random_fb_locale()
    locale_info = get_current_locale_info()

    user_agent = ugen()
    headers_get = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "accept-language": accept_lang,
        "sec-ch-ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "user-agent": user_agent,
    }

    res = ses.get(reg_url, headers=headers_get, timeout=15)
    extracted_data = extract_all_from_html(res.text)

    # Dynamic tokens from the page — never hardcoded
    fb_dtsg = extracted_data.get("fb_dtsg", "")
    jazoest = extracted_data.get("jazoest", "")
    lsd = extracted_data.get("lsd", "")
    reg_instance = extracted_data.get("reg_instance", "")
    reg_impression_id = extracted_data.get("reg_impression_id", "")

    return {
        "ses": ses,
        "myurl": myurl,
        "reg_url": reg_url,
        "user_agent": user_agent,
        "accept_lang": accept_lang,
        "locale_info": locale_info,
        "fb_dtsg": fb_dtsg,
        "jazoest": jazoest,
        "lsd": lsd,
        "reg_instance": reg_instance,
        "reg_impression_id": reg_impression_id,
        "extracted_data": extracted_data,
    }


def _build_reg_payload(ctx, fname, lname, email_or_phone, password,
                       birth_day, birth_month, birth_year, gender_code):
    """Build the registration POST payload from dynamic tokens."""
    encpass = f"#PWD_BROWSER:0:{int(time.time())}:{password}"

    return {
        "lsd": ctx["lsd"],
        "jazoest": ctx["jazoest"],
        "fb_dtsg": ctx["fb_dtsg"],
        "ccp": "",
        "submission_request": "true",
        "helper": "",
        "zero_header_af_client": "",
        "field_names[0]": "firstname",
        "firstname": fname,
        "field_names[1]": "birthday_wrapper",
        "birthday_day": str(birth_day),
        "birthday_month": str(birth_month),
        "birthday_year": str(birth_year),
        "age_step_input": "",
        "did_use_age": "false",
        "field_names[2]": "reg_email__",
        "reg_email__": email_or_phone,
        "field_names[3]": "sex",
        "sex": gender_code,
        "preferred_pronoun": "",
        "custom_gender": "",
        "field_names[4]": "reg_passwd__",
        "reg_passwd__": password,
        "name_suggest_elig": "",
        "was_shown_name_suggestions": "",
        "did_use_suggested_name": "",
        "use_custom_gender": "",
        "guid": "",
        "pre_form_step": "",
        "lastname": lname,
        "encpass": encpass,
        "submit": "Daftar",
        "reg_instance": ctx["reg_instance"],
        "reg_impression_id": ctx["reg_impression_id"],
    }


def _post_registration(ctx, data):
    """Submit the registration form and return (uid, cookie_str)."""
    headers_post = {
        "authority": "m.facebook.com",
        "accept": "*/*",
        "accept-language": ctx["accept_lang"],
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://m.facebook.com",
        "referer": ctx["reg_url"],
        "sec-ch-prefers-color-scheme": "dark",
        "sec-ch-ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
        "sec-ch-ua-full-version-list": '"Chromium";v="139.0.7339.0", "Not;A=Brand";v="99.0.0.0"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-model": "",
        "sec-ch-ua-platform": '"Android"',
        "sec-ch-ua-platform-version": '"14.0.0"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": ctx["user_agent"],
    }

    reg = ctx["ses"].post(
        f"https://m.facebook.com/reg/submit/",
        data=data,
        headers=headers_post,
        timeout=30,
    )

    cookies = ctx["ses"].cookies.get_dict()
    uid = cookies.get("c_user", "")
    cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
    return uid, cookie_str, reg


def register_account():
    email, contact_info = get_email()
    contact_display = email if not contact_info else contact_info.get("original", email)

    for i in range(settings.get("limit", 5)):
        sys.stdout.write(
            f"\r[grey50]( [bold cyan]{i + 1}[/bold cyan] Akun : "
            f"{status['live']} [grey50]) : ([bold green]Success:[bold green]{status['live']} [grey50])"
        )
        sys.stdout.flush()

        try:
            ctx = _build_registration_session()

            locale_info = ctx["locale_info"]
            if locale_info:
                console.print(Panel(
                    f"[bold cyan]Menggunakan Locale:[/bold cyan] {locale_info['locale']}\n"
                    f"[bold cyan]Language:[/bold cyan] {locale_info['language']}\n"
                    f"[bold cyan]Country:[/bold cyan] {locale_info['country']}\n"
                    f"[bold cyan]Gender Setting:[/bold cyan] {settings.get('gender_setting', 'random')}",
                    title="RANDOM LOCALE & GENDER"
                ))

            fname = faker.first_name()
            lname = faker.last_name()
            fullname = f"{fname} {lname}"
            password = settings.get("password", "P@ssw0rd123!")

            birth_day = random.randint(1, 28)
            birth_month = random.randint(1, 12)
            birth_year = random.randint(1985, 2002)
            gender_code, gender_text = resolve_gender()
            tgl_lahir = f"{birth_day:02d}/{birth_month:02d}/{birth_year}"

            data = _build_reg_payload(
                ctx, fname, lname, email, password,
                birth_day, birth_month, birth_year, gender_code,
            )
            uid, cookie_str, reg = _post_registration(ctx, data)

            if uid:
                profile_name = get_facebook_profile_info(uid)
                created_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

                account_data = {
                    "uid": uid,
                    "password": password,
                    "email": email,
                    "nama": profile_name,
                    "gender": gender_text,
                    "tgl_lahir": tgl_lahir,
                    "timestamp": created_date,
                    "cookie": cookie_str,
                }
                save_account_to_file(account_data)
                status["live"] += 1

                if contact_info and settings.get("use_contact_file"):
                    remove_contact_from_file(
                        settings["contact_file"],
                        contact_info["original"],
                    )
                    settings["contact_list"].remove(contact_info)
                    console.print(
                        f"[bold yellow]\u2713 Contact [{contact_info['original']}] "
                        "berhasil dihapus dari file.[/bold yellow]"
                    )

                table = Table(title="AKUN BERHASIL DIBUAT", title_style="bold green")
                table.add_column("Key", style="bold cyan")
                table.add_column("Value", style="bold white")
                table.add_row("UID|Pass", f"[bold green]{uid}|{_mask_password(password)}[/bold green]")
                table.add_row("Nama Lengkap", fullname)
                table.add_row("Email / Nomor", str(email))
                table.add_row("Jenis Kelamin", gender_text)
                table.add_row("Tanggal Lahir", tgl_lahir)
                table.add_row("Tanggal Dibuat", created_date)
                if locale_info:
                    table.add_row("Locale", f"[bold cyan]{locale_info['locale']} ({locale_info['language']})[/bold cyan]")
                if len(cookie_str) > 100:
                    table.add_row("Cookie (1/2)", f"[bold purple]{cookie_str[:100]}...[/bold purple]")
                    table.add_row("Cookie (2/2)", f"[bold purple]...{cookie_str[100:]}[/bold purple]")
                else:
                    table.add_row("Cookie", cookie_str)
                console.print(table)
            elif "checkpoint" in str(getattr(reg, "url", "")):
                status["checkpoint"] += 1
                console.print("[bold yellow]Akun terbuat namun memerlukan checkpoint/verifikasi.[/bold yellow]")
            else:
                console.print("[bold red]Registrasi gagal. Tidak mendapatkan cookie c_user.[/bold red]")

            time.sleep(random.randint(3, 7))
            email, contact_info = get_email()

        except Exception as e:
            console.print(f"[bold red]Error saat registrasi: {e}[/bold red]")
            time.sleep(2)


def register_manual():
    """Manual registration for a single account with user-provided input."""
    clear_screen()
    show_header_once()

    console.print(Panel(
        "[bold cyan]Registrasi Manual Akun Facebook[/bold cyan]\n\n"
        "Isi data di bawah ini secara manual.\n"
        "Data akan dikirim ke Facebook untuk membuat 1 akun baru.\n"
        "[bold yellow]Tekan Enter kosong untuk menggunakan nilai default (di dalam kurung).[/bold yellow]",
        title="REGISTER MANUAL", border_style="cyan"
    ))

    default_fname = faker.first_name()
    first_name = Prompt.ask("[bold cyan]Nama Depan[/bold cyan]", default=default_fname).strip() or default_fname

    default_lname = faker.last_name()
    last_name = Prompt.ask("[bold cyan]Nama Belakang[/bold cyan]", default=default_lname).strip() or default_lname
    fullname = f"{first_name} {last_name}"

    console.print("\n[bold yellow]Format yang didukung:[/bold yellow]")
    console.print("  - Email: contoh@gmail.com")
    console.print("  - Nomor: +6281234567890 atau 081234567890")

    default_contact = "+628" + str(random.randint(10000000, 99999999))
    while True:
        contact_raw = Prompt.ask("[bold cyan]Email / Nomor Telepon[/bold cyan]", default=default_contact).strip()
        if not contact_raw:
            contact_raw = default_contact
        if validate_email(contact_raw):
            final_contact = contact_raw
            break
        elif validate_phone(contact_raw):
            final_contact = normalize_phone_number(contact_raw)
            break
        else:
            console.print("[bold red]\u2717 Format tidak valid! Masukkan email yang benar atau nomor telepon (min 8 digit).[/bold red]")

    default_pw = settings.get("password", "P@ssw0rd123!")
    password = Prompt.ask("[bold cyan]Password[/bold cyan]", default=default_pw, password=True).strip() or default_pw

    console.print("\n[bold yellow]Tanggal Lahir:[/bold yellow]")
    default_day = f"{random.randint(1, 28):02d}"
    default_month = f"{random.randint(1, 12):02d}"
    default_year = str(random.randint(1985, 2002))

    birth_day = Prompt.ask("[bold cyan]  Hari (01-31)[/bold cyan]", default=default_day).strip() or default_day
    birth_month = Prompt.ask("[bold cyan]  Bulan (01-12)[/bold cyan]", default=default_month).strip() or default_month
    birth_year = Prompt.ask("[bold cyan]  Tahun (contoh: 1998)[/bold cyan]", default=default_year).strip() or default_year

    try:
        day_int = int(birth_day)
        month_int = int(birth_month)
        year_int = int(birth_year)
        if not (1 <= day_int <= 31 and 1 <= month_int <= 12 and 1900 <= year_int <= 2010):
            raise ValueError
    except ValueError:
        console.print("[bold red]Tanggal tidak valid, menggunakan default.[/bold red]")
        day_int, month_int, year_int = int(default_day), int(default_month), int(default_year)

    tgl_lahir = f"{day_int:02d}/{month_int:02d}/{year_int}"

    console.print("\n[bold yellow]Jenis Kelamin:[/bold yellow]")
    console.print("  1. Perempuan")
    console.print("  2. Laki-laki")
    console.print("  3. Random (Acak)")
    gender_choice = Prompt.ask("[bold cyan]Pilih (1/2/3)[/bold cyan]", default="3").strip()
    if gender_choice == "1":
        gender_code, gender_text = "1", "Perempuan"
    elif gender_choice == "2":
        gender_code, gender_text = "2", "Laki-laki"
    else:
        gender_code, gender_text = resolve_gender()
        console.print(f"  [dim]\u2192 Dipilih random: {gender_text}[/dim]")

    console.print(Panel(
        f"[bold white]Nama Lengkap  :[/bold white] [bold green]{fullname}[/bold green]\n"
        f"[bold white]Email / No    :[/bold white] [bold green]{final_contact}[/bold green]\n"
        f"[bold white]Password      :[/bold white] [bold green]{_mask_password(password)}[/bold green]\n"
        f"[bold white]Tanggal Lahir :[/bold white] [bold green]{tgl_lahir}[/bold green]\n"
        f"[bold white]Jenis Kelamin :[/bold white] [bold green]{gender_text}[/bold green]",
        title="KONFIRMASI DATA", border_style="green"
    ))

    confirm = input("[bold yellow]Lanjutkan registrasi? (y/n)[/bold yellow] ").strip().lower()
    if confirm != "y":
        console.print("[bold red]Registrasi dibatalkan.[/bold red]")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    console.print("\n[bold cyan]Memulai proses registrasi manual...[/bold cyan]")

    try:
        ctx = _build_registration_session()
        data = _build_reg_payload(
            ctx, first_name, last_name, final_contact, password,
            day_int, month_int, year_int, gender_code,
        )
        uid, cookie_str, reg = _post_registration(ctx, data)

        if uid:
            profile_name = get_facebook_profile_info(uid)
            created_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            locale_info = ctx["locale_info"]

            account_data = {
                "uid": uid,
                "password": password,
                "email": final_contact,
                "nama": profile_name,
                "gender": gender_text,
                "tgl_lahir": tgl_lahir,
                "timestamp": created_date,
                "cookie": cookie_str,
            }
            save_account_to_file(account_data)
            status["live"] += 1

            table = Table(title="AKUN BERHASIL DIBUAT", title_style="bold green")
            table.add_column("Key", style="bold cyan")
            table.add_column("Value", style="bold white")
            table.add_row("UID|Pass", f"[bold green]{uid}|{_mask_password(password)}[/bold green]")
            table.add_row("Nama Lengkap", fullname)
            table.add_row("Email / Nomor", str(final_contact))
            table.add_row("Jenis Kelamin", gender_text)
            table.add_row("Tanggal Lahir", tgl_lahir)
            table.add_row("Tanggal Dibuat", created_date)
            if locale_info:
                table.add_row("Locale", f"[bold cyan]{locale_info['locale']} ({locale_info['language']})[/bold cyan]")
            if len(cookie_str) > 100:
                table.add_row("Cookie (1/2)", f"[bold purple]{cookie_str[:100]}...[/bold purple]")
                table.add_row("Cookie (2/2)", f"[bold purple]...{cookie_str[100:]}[/bold purple]")
            else:
                table.add_row("Cookie", cookie_str)
            console.print(table)
        elif "checkpoint" in str(getattr(reg, "url", "")):
            status["checkpoint"] += 1
            console.print("[bold yellow]Akun terbuat namun memerlukan checkpoint/verifikasi.[/bold yellow]")
        else:
            console.print("[bold red]Registrasi gagal. Tidak mendapatkan cookie c_user.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error saat registrasi: {e}[/bold red]")

    input("\nTekan Enter untuk kembali ke menu...")


# ===========================================================================
# Settings menu
# ===========================================================================

def settings_menu():
    while True:
        clear_screen()
        show_header_once()

        gender_display = {
            "male": "LAKI-LAKI \u2642",
            "female": "PEREMPUAN \u2640",
        }.get(settings.get("gender_setting", "random"), "RANDOM \U0001f3b2")

        console.print(Panel(
            f"[bold white]1.[/bold white] Password Akun      : [bold green]{_mask_password(settings['password'])}[/bold green]\n"
            f"[bold white]2.[/bold white] Limit Register      : [bold green]{settings['limit']}[/bold green]\n"
            f"[bold white]3.[/bold white] Gender Setting      : [bold yellow]{gender_display}[/bold yellow]\n"
            f"[bold white]4.[/bold white] Random Locale       : [bold green]{'AKTIF' if settings.get('random_locale') else 'NONAKTIF'}[/bold green]\n"
            f"[bold white]5.[/bold white] Gunakan Temp Email  : [bold green]{'AKTIF' if settings.get('use_temp_email') else 'NONAKTIF'}[/bold green]\n"
            f"[bold white]6.[/bold white] Gunakan Real Email  : [bold green]{'AKTIF' if settings.get('use_real_email') else 'NONAKTIF'}[/bold green]\n"
            f"[bold white]7.[/bold white] Gunakan Contact File: [bold green]{'AKTIF (' + str(len(settings.get('contact_list', []))) + ' contact)' if settings.get('use_contact_file') else 'NONAKTIF'}[/bold green]\n"
            "[bold white]8.[/bold white] Lihat Contact List\n"
            "[bold white]9.[/bold white] Buat Contoh Contact File\n"
            "[bold white]10.[/bold white] Lihat Info Contact File\n"
            f"[bold white]11.[/bold white] Lihat Semua Locale ({len(FACEBOOK_LOCALES)})\n"
            "[bold white]12.[/bold white] Lihat Locale Saat Ini\n"
            "[bold white]0.[/bold white] Kembali ke Menu Utama",
            title="\u2699 SETTINGS", border_style="yellow"
        ))

        choice = Prompt.ask("[bold cyan]Pilih opsi[/bold cyan]", default="0").strip()

        if choice == "1":
            new_pass = Prompt.ask("[bold cyan]Password baru[/bold cyan]", password=True).strip()
            if new_pass:
                settings["password"] = new_pass
                console.print(f"[bold green]\u2713 Password diubah.[/bold green]")
        elif choice == "2":
            new_limit = IntPrompt.ask("[bold cyan]Jumlah limit akun[/bold cyan]", default=settings["limit"])
            settings["limit"] = max(1, new_limit)
            console.print(f"[bold green]\u2713 Limit diubah menjadi: {settings['limit']}[/bold green]")
        elif choice == "3":
            console.print("\n[bold yellow]Pilih Gender Setting:[/bold yellow]")
            console.print("  1. Laki-laki (\u2642) - Semua akun akan laki-laki")
            console.print("  2. Perempuan (\u2640) - Semua akun akan perempuan")
            console.print("  3. Random (\U0001f3b2) - Gender akan dipilih acak tiap akun")
            gc = Prompt.ask("[bold cyan]Pilih (1/2/3)[/bold cyan]", default="3").strip()
            if gc == "1":
                settings["gender_setting"] = "male"
                console.print("[bold green]\u2713 Gender diubah ke: LAKI-LAKI[/bold green]")
            elif gc == "2":
                settings["gender_setting"] = "female"
                console.print("[bold green]\u2713 Gender diubah ke: PEREMPUAN[/bold green]")
            else:
                settings["gender_setting"] = "random"
                console.print("[bold green]\u2713 Gender diubah ke: RANDOM[/bold green]")
        elif choice == "4":
            settings["random_locale"] = not settings.get("random_locale", True)
            console.print(f"[bold green]\u2713 Random Locale: {'AKTIF' if settings['random_locale'] else 'NONAKTIF'}[/bold green]")
        elif choice == "5":
            if settings.get("use_temp_email"):
                settings["use_temp_email"] = False
                console.print("[bold yellow]Temp Email dinonaktifkan.[/bold yellow]")
            else:
                settings["use_temp_email"] = True
                settings["use_real_email"] = False
                settings["use_contact_file"] = False
                console.print("[bold green]\u2713 Temp Email diaktifkan. Real Email & Contact File dinonaktifkan.[/bold green]")
        elif choice == "6":
            if settings.get("use_real_email"):
                settings["use_real_email"] = False
                console.print("[bold yellow]Real Email dinonaktifkan.[/bold yellow]")
            else:
                settings["use_real_email"] = True
                settings["use_temp_email"] = False
                settings["use_contact_file"] = False
                console.print("[bold green]\u2713 Real Email diaktifkan. Temp Email & Contact File dinonaktifkan.[/bold green]")
        elif choice == "7":
            if settings.get("use_contact_file"):
                settings["use_contact_file"] = False
                settings["contact_file"] = ""
                console.print("[bold yellow]Contact File dinonaktifkan.[/bold yellow]")
            else:
                file_path = Prompt.ask("[bold cyan]Masukkan path file contact[/bold cyan]", default="contacts.txt").strip()
                if os.path.exists(file_path):
                    contacts = load_contact_file(file_path)
                    if contacts:
                        settings["use_contact_file"] = True
                        settings["use_temp_email"] = False
                        settings["use_real_email"] = False
                        settings["contact_file"] = file_path
                        settings["contact_list"] = contacts
                        console.print(f"[bold green]\u2713 Contact File diaktifkan: {len(contacts)} contact dimuat.[/bold green]")
                    else:
                        console.print("[bold red]Tidak ada contact valid dalam file.[/bold red]")
                else:
                    console.print(f"[bold red]File tidak ditemukan: {file_path}[/bold red]")
        elif choice == "8":
            show_contact_list()
        elif choice == "9":
            create_contact_file_example()
        elif choice == "10":
            show_contact_file_info()
        elif choice == "11":
            show_all_locales()
        elif choice == "12":
            show_locale_info()
        elif choice == "0":
            break

        if choice != "0":
            time.sleep(1)


# ===========================================================================
# Header & Main Menu
# ===========================================================================

_header_shown = False


def show_header_once():
    global _header_shown
    if not _header_shown:
        console.print(Panel(
            "[bold white on blue] FACEBOOK BOT ACCOUNT GENERATOR[/bold white on blue]\n"
            "[bold red on white] AUTHOR : SLLOWLY | VERSION : V4.5[/bold red on white]",
            style="bright_blue"
        ))
        _header_shown = True


def main_menu():
    global _header_shown

    license_parts = []  # populated by approval()

    while True:
        _header_shown = False
        clear_screen()
        show_header_once()

        saved = count_saved_accounts()
        console.print(Panel(
            f"[bold white]1.[/bold white] \U0001f680 Register Otomatis ([bold green]{settings['limit']}[/bold green] akun)\n"
            "[bold white]2.[/bold white] \u270d Register Manual (1 akun)\n"
            "[bold white]3.[/bold white] \u2699 Settings\n"
            "[bold white]4.[/bold white] \U0001f4ca Statistik\n"
            "[bold white]5.[/bold white] \U0001f50d Cek UID Facebook\n"
            "[bold white]6.[/bold white] \U0001f310 Lihat URL Registrasi\n"
            "[bold white]7.[/bold white] \U0001f4c2 Buka Folder Penyimpanan\n"
            "[bold white]0.[/bold white] \U0001f6aa Keluar",
            title="MENU UTAMA", border_style="green"
        ))

        choice = Prompt.ask("[bold cyan]Pilih menu[/bold cyan]", default="0").strip()

        if choice == "0":
            console.print("[bold red]Keluar dari program...[/bold red]")
            sys.exit(0)
        elif choice == "1":
            console.print(f"\n[bold cyan]Memulai register otomatis {settings['limit']} akun...[/bold cyan]")
            for _ in range(settings["limit"]):
                register_account()
            console.print(f"\n[bold green]Selesai! Total akun live: {status['live']}[/bold green]")
            input("\nTekan Enter untuk kembali ke menu...")
        elif choice == "2":
            register_manual()
        elif choice == "3":
            settings_menu()
        elif choice == "4":
            console.print(Panel(
                f"[bold white]Total Akun Live    :[/bold white] [bold green]{status['live']}[/bold green]\n"
                f"[bold white]Total Checkpoint   :[/bold white] [bold yellow]{status['checkpoint']}[/bold yellow]\n"
                f"[bold white]Total Loop         :[/bold white] [bold cyan]{status['loop']}[/bold cyan]\n"
                f"[bold white]Akun Tersimpan     :[/bold white] [bold green]{saved}[/bold green]\n"
                f"[bold white]Gender Setting     :[/bold white] [bold yellow]{settings.get('gender_setting', 'random').upper()}[/bold yellow]\n"
                f"[bold white]Random Locale      :[/bold white] [bold green]{'AKTIF' if settings.get('random_locale') else 'NONAKTIF'}[/bold green]\n"
                f"[bold white]Total Locale       :[/bold white] [bold cyan]{len(FACEBOOK_LOCALES)}[/bold cyan]\n"
                f"[bold white]File Save          :[/bold white] [dim]{SAVE_FILE}[/dim]\n"
                f"[bold white]File Log           :[/bold white] [dim]{LOG_FILE}[/dim]",
                title="STATISTIK", border_style="cyan"
            ))
            input("\nTekan Enter untuk kembali...")
        elif choice == "5":
            uid_input = Prompt.ask("[bold cyan]Masukkan UID Facebook[/bold cyan]").strip()
            if uid_input:
                check(uid_input)
            input("\nTekan Enter untuk kembali...")
        elif choice == "6":
            show_registration_url()
            input("\nTekan Enter untuk kembali...")
        elif choice == "7":
            try:
                if os.name == "nt":
                    os.startfile(str(SAVE_DIR))
                elif sys.platform == "darwin":
                    os.system(f'open "{SAVE_DIR}"')
                else:
                    os.system(f'xdg-open "{SAVE_DIR}" 2>/dev/null || termux-open "{SAVE_DIR}" 2>/dev/null')
                console.print(f"[bold green]Membuka folder: {SAVE_DIR}[/bold green]")
            except Exception as e:
                console.print(f"[bold red]Gagal membuka folder: {e}[/bold red]")
                console.print(f"[dim]Path manual: {SAVE_DIR}[/dim]")
            input("\nTekan Enter untuk kembali...")


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == "__main__":
    try:
        approval()
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[bold red]Program dihentikan oleh user.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
