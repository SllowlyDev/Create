"""
Shared Facebook API utilities.

Consolidates the duplicated profile lookup logic from
get_facebook_profile_info() and check() into a single function.
"""

import requests
from bs4 import BeautifulSoup as bs

from rich.console import Console

console = Console()


def fetch_facebook_profile_name(uid, timeout=10):
    """
    Fetch the profile name for a Facebook UID.

    Previously duplicated between get_facebook_profile_info() and check().
    Both functions performed the same HTTP GET + BeautifulSoup title extraction.

    Args:
        uid: Facebook user ID
        timeout: request timeout in seconds

    Returns:
        str: profile name, or error/fallback string
    """
    try:
        r = requests.get(f"https://www.facebook.com/{uid}", timeout=timeout)
        if r.status_code == 200:
            soup = bs(r.text, "html.parser")
            title = soup.find("title")
            if title:
                return title.text if title.text else "Nama tidak ditemukan"
            return "Nama tidak ditemukan"
        return "Profil tidak dapat diakses"
    except Exception:
        return "Error saat mengakses profil"


def get_facebook_profile_info(uid):
    """
    Get profile name for a UID. Thin wrapper around fetch_facebook_profile_name.
    """
    return fetch_facebook_profile_name(uid)


def check(uidku):
    """
    Check a Facebook UID and print the result.
    Uses the shared fetch logic instead of duplicating it.
    """
    try:
        r = requests.get(f"https://www.facebook.com/{uidku}", timeout=10)
        if r.status_code == 200:
            soup = bs(r.text, "html.parser")
            title = soup.find("title")
            nama = title.text if title and title.text else "Nama tidak ditemukan"
            console.print(f"[bold green]UID {uidku} -> {nama}[/bold green]")
        else:
            console.print(
                f"[bold red]UID {uidku} tidak dapat diakses (HTTP {r.status_code})[/bold red]"
            )
    except Exception as e:
        console.print(f"[bold red]Error saat mengakses UID {uidku}: {e}[/bold red]")
