"""
Shared validation and contact-handling utilities.

Consolidates duplicated phone/email validation and cleaning logic
from normalize_phone_number, validate_phone, validate_email,
load_contact_file, and remove_contact_from_file.
"""

import os
import re

from rich.console import Console
from rich.panel import Panel

from utils.constants import PHONE_CLEAN_REGEX

console = Console()


def clean_phone_string(value):
    """
    Remove whitespace, dashes, and parentheses from a phone string.
    This regex was duplicated across 4+ functions.
    """
    return re.sub(PHONE_CLEAN_REGEX, "", str(value))


def normalize_phone_number(phone, auto_add_plus=True):
    """
    Clean and normalize a phone number string.
    Removes formatting characters, fixes double-plus, optionally adds '+' prefix.
    """
    cleaned = clean_phone_string(phone).strip()
    cleaned = cleaned.replace("++", "+")
    if auto_add_plus and not cleaned.startswith("+"):
        if cleaned.startswith("0"):
            pass
        elif cleaned.isdigit():
            cleaned = "+" + cleaned
    return cleaned


def validate_email(email):
    """Validate an email address format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone(phone):
    """Validate a phone number (at least 8 digits after cleaning)."""
    phone_digits = clean_phone_string(str(phone)).replace("+", "")
    return len(phone_digits) >= 8 and phone_digits.isdigit()


def remove_contact_from_file(file_path, original_value):
    """
    Remove a used contact from the contact file after successful registration.
    """
    if not os.path.exists(file_path):
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        removed = False
        for line in lines:
            clean_line = clean_phone_string(line.strip())
            clean_original = clean_phone_string(original_value)
            clean_line_no_space = clean_line.replace(" ", "")
            clean_original_no_space = clean_original.replace(" ", "")

            if not removed and (clean_line_no_space == clean_original_no_space):
                removed = True
                continue
            new_lines.append(line)

        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    except Exception as e:
        console.print(f"[bold red]Gagal menghapus contact dari file: {e}[/bold red]")


def load_contact_file(file_path):
    """
    Load and validate contacts from a text file.

    Returns:
        list of dicts with keys: type, value, original
    """
    if not os.path.exists(file_path):
        console.print(f"[bold red]File tidak ditemukan: {file_path}[/bold red]")
        return []

    contacts = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            contact = line.strip()
            if not contact or contact.startswith("#"):
                continue

            if "@" in contact:
                if validate_email(contact):
                    contacts.append({
                        "type": "email",
                        "value": contact,
                        "original": contact,
                    })
                    console.print(f"[green]✓ Baris {line_num}: Email valid - {contact}[/green]")
            else:
                original_format = contact
                cleaned_value = clean_phone_string(contact)
                if not cleaned_value.startswith("+"):
                    final_value = "+" + cleaned_value
                    console.print(
                        f"[yellow]⚠ Baris {line_num}: Nomor {original_format} "
                        f"→ ditambahkan + menjadi {final_value}[/yellow]"
                    )
                else:
                    final_value = cleaned_value
                    console.print(
                        f"[green]✓ Baris {line_num}: Nomor valid - "
                        f"{original_format} → {final_value}[/green]"
                    )

                if validate_phone(final_value):
                    contacts.append({
                        "type": "phone",
                        "value": final_value,
                        "original": original_format,
                    })
                else:
                    console.print(
                        f"[yellow]⚠ Baris {line_num}: Format tidak dikenali - {contact}[/yellow]"
                    )

        console.print(f"[bold cyan]Total contact valid: {len(contacts)}[/bold cyan]")
    except Exception as e:
        console.print(f"[bold red]Gagal membaca file: {e}[/bold red]")

    return contacts


def create_contact_file_example(save_dir):
    """Create an example contact file showing the expected format."""
    example_path = os.path.join(save_dir, "contact_example.txt")
    example_content = (
        "# Contoh file contact untuk Facebook Creator Tools\n"
        "# ==================================================\n"
        "# PENTING: \n"
        "# - Setiap nomor/email yang BERHASIL didaftarkan akan OTOMATIS DIHAPUS dari file ini\n"
        "# - Satu contact per baris\n"
        "# - Baris yang dimulai dengan # akan diabaikan\n"
        "#\n"
        "# Format yang didukung:\n"
        "# Email:\n"
        "contoh@gmail.com\n"
        "user123@yahoo.com\n"
        "#\n"
        "# Nomor telepon (+ otomatis ditambahkan jika belum ada):\n"
        "+6281234567890\n"
        "081234567891\n"
        "6281234567892\n"
    )
    try:
        with open(example_path, "w", encoding="utf-8") as f:
            f.write(example_content)
        console.print(f"[bold green]✓ Contoh file contact dibuat di: {example_path}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Gagal membuat contoh file: {str(e)}[/bold red]")


def show_contact_file_info():
    """Display info panel about contact file format."""
    info_text = (
        "[bold cyan]Informasi Format Contact File:[/bold cyan]\n\n"
        "✓ Email: akan digunakan apa adanya\n"
        "✓ Nomor Telepon: akan [bold yellow]OTOMATIS ditambahkan +[/bold yellow] jika belum ada\n"
        "✓ Contact yang [bold red]BERHASIL[/bold red] didaftarkan akan otomatis dihapus dari file\n"
        "✓ Baris yang dimulai # akan diabaikan (komentar)\n"
        "✓ Satu contact per baris"
    )
    console.print(Panel(info_text, title="PANDUAN CONTACT FILE"))


def show_contact_list(settings):
    """Display the currently loaded contact list."""
    contact_list = settings.get("contact_list", [])
    if not contact_list:
        console.print("[bold yellow]Belum ada file contact yang dimuat.[/bold yellow]")
        return

    text = (
        f"[bold cyan]Daftar Contact yang Dimuat:[/bold cyan]\n"
        f"Total: {len(contact_list)} contact\n"
        f"File: {settings.get('contact_file', '')}"
        f"\n[dim][yellow]⚠ Contact yang berhasil didaftarkan akan otomatis dihapus dari file[/yellow][/dim]"
    )
    console.print(Panel(text, title="CONTACT LIST"))

    for i, contact in enumerate(contact_list[:20]):
        type_icon = "✉" if contact.get("type") == "email" else "📱"
        line = f"{i + 1}. {type_icon} {contact['original']}"
        if contact["original"] != contact["value"]:
            line += f"   [dim]→ akan digunakan: {contact['value']}[/dim]"
        console.print(line)

    if len(contact_list) > 20:
        console.print(f"[dim]... dan {len(contact_list) - 20} contact lainnya[/dim]")

    email_count = sum(1 for c in contact_list if c.get("type") == "email")
    phone_count = sum(1 for c in contact_list if c.get("type") == "phone")
    console.print(f"\n[bold]Statistik:[/bold] Email: {email_count}, Nomor: {phone_count}")
