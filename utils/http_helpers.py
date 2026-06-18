"""
Shared HTTP helpers for Facebook registration flows.

Eliminates duplication between register_account() and register_manual()
by centralizing URL construction, header building, form token extraction,
POST parameter assembly, and response handling.
"""

import random
import string
import time

from rich.console import Console
from rich.table import Table

from utils.constants import (
    FB_A_TOKEN,
    FB_APP_ID,
    FB_DTSG_DEFAULT,
    FB_DYN,
    FB_REG_DOMAINS,
    SEC_CH_UA,
    SEC_CH_UA_FULL,
)

console = Console()


def build_registration_url():
    """
    Build a Facebook mobile registration URL with random tokens.

    Returns:
        tuple: (full_url, selected_domain)
    """
    domain = random.choice(FB_REG_DOMAINS)
    token = "".join(random.choices(string.ascii_letters + string.digits, k=20))
    d_hash = "".join(random.choices(string.hexdigits, k=40)).upper()
    cid = str(random.randint(10000, 99999))
    rwtsid = str(random.randint(10000, 99999))

    url = (
        f"https://{domain}/mreg?e_token={token}"
        f"&d_hash={d_hash}&cid={cid}"
        f"&app_version=310&tg=201&cct=1&src=0&cah=1&rwtsid={rwtsid}"
    )
    return url, domain


def build_get_headers(user_agent, accept_lang):
    """
    Build headers for the initial GET request to the registration page.
    """
    return {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "accept-language": accept_lang,
        "sec-ch-ua": SEC_CH_UA,
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "upgrade-insecure-requests": "1",
        "user-agent": user_agent,
    }


def build_post_headers(user_agent, accept_lang, device_name):
    """
    Build headers for the POST registration submission.
    """
    return {
        "authority": "m.facebook.com",
        "accept": "*/*",
        "accept-language": accept_lang,
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://m.facebook.com",
        "referer": "https://m.facebook.com",
        "sec-ch-prefers-color-scheme": "dark",
        "sec-ch-ua": SEC_CH_UA,
        "sec-ch-ua-full-version-list": SEC_CH_UA_FULL,
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-model": f'"{device_name}"',
        "sec-ch-ua-platform": '"Android"',
        "sec-ch-ua-platform-version": '"14.0.0"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": user_agent,
    }


def extract_form_tokens(extracted_data):
    """
    Extract Facebook form tokens from the parsed registration page.

    Returns:
        dict with keys: fb_dtsg, jazoest, lsd, reg_instance, reg_impression_id,
                        app_id, logger_id, __dyn, __req, __user, __a, __fmt
    """
    return {
        "fb_dtsg": extracted_data.get("fb_dtsg", FB_DTSG_DEFAULT),
        "jazoest": extracted_data.get("jazoest", ""),
        "lsd": extracted_data.get("lsd", ""),
        "reg_instance": extracted_data.get("reg_instance", ""),
        "reg_impression_id": extracted_data.get("reg_impression_id", ""),
        "app_id": extracted_data.get("app_id", FB_APP_ID),
        "logger_id": extracted_data.get("logger_id", ""),
        "__dyn": FB_DYN,
        "__req": "",
        "__user": "0",
        "__a": FB_A_TOKEN,
        "__fmt": "",
    }


def build_registration_params(tokens, fullname, password, birth_day, birth_month,
                              birth_year, gender_code, email, encpass):
    """
    Assemble the full POST parameter dict for Facebook registration.
    """
    fname_parts = fullname.split(" ", 1)
    firstname = fname_parts[0]
    lastname = fname_parts[1] if len(fname_parts) > 1 else ""

    params = {
        "fb_dtsg": tokens["fb_dtsg"],
        "jazoest": tokens["jazoest"],
        "lsd": tokens["lsd"],
        "reg_instance": tokens["reg_instance"],
        "reg_impression_id": tokens["reg_impression_id"],
        "app_id": tokens["app_id"],
        "logger_id": tokens["logger_id"],
        "__dyn": tokens["__dyn"],
        "__req": tokens["__req"],
        "__user": tokens["__user"],
        "__a": tokens["__a"],
        "__fmt": tokens["__fmt"],
        "ccp": "2",
        "submission_request": "true",
        "helper": "",
        "ns": "0",
        "zero_header_af_client": "",
        "field_names[0]": "firstname",
        "field_names[1]": "birthday_wrapper",
        "birthday_day": str(birth_day),
        "birthday_month": str(birth_month),
        "birthday_year": str(birth_year),
        "age_step_input": "",
        "did_use_age": "false",
        "field_names[2]": "reg_email__",
        "reg_email__": email,
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
        "encpass": encpass,
        "firstname": firstname,
        "lastname": lastname,
        "submit": "Daftar",
    }
    return params


def build_encpass(password):
    """
    Build the encrypted password token for Facebook registration.
    """
    timestamp = str(int(time.time()))
    return f"#PWD_BROWSER:0:{timestamp}:{password}"


def extract_cookies_string(session):
    """
    Extract cookies from a requests.Session as a semicolon-separated string.
    """
    parts = []
    for k, v in session.cookies.get_dict().items():
        parts.append(f"{k}={v}")
    return "; ".join(parts)


def display_account_table(account_data, title="AKUN BERHASIL DIBUAT"):
    """
    Display a Rich table showing the created account details.
    Used by both register_account() and register_manual().
    """
    table = Table(title=title, style="bold green", show_lines=True)
    table.add_column("Key", style="bold cyan")
    table.add_column("Value", style="bold white")

    uid = account_data.get("uid", "")
    password = account_data.get("password", "")
    table.add_row("UID|Pass", f"[bold green]{uid}|{password}[/bold green]")
    table.add_row("Nama Lengkap", account_data.get("nama", ""))
    table.add_row("Email / Nomor", account_data.get("email", ""))
    table.add_row("Jenis Kelamin", account_data.get("gender", ""))
    table.add_row("Tanggal Lahir", account_data.get("tgl_lahir", ""))
    table.add_row("Tanggal Dibuat", account_data.get("timestamp", ""))

    locale_str = account_data.get("locale", "")
    language_str = account_data.get("language", "")
    if locale_str:
        table.add_row("Locale", f"[bold cyan]{locale_str} ({language_str})[/bold cyan]")

    cookie = account_data.get("cookie", "")
    if cookie:
        half = len(cookie) // 2
        if len(cookie) > 80:
            table.add_row("Cookie (1/2)", f"[bold purple]{cookie[:half]}...[/bold purple]")
            table.add_row("Cookie (2/2)", f"[bold purple]...{cookie[half:]}[/bold purple]")
        else:
            table.add_row("Cookie", cookie)

    console.print(table)
