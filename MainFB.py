import os
import sys
import time
import random
import string
import getpass
import socket
import re
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
    print("Jalankan: pip install rich requests bs4 faker fake_useragent")
    exit(1)

console = Console()

# ============================================================
# LOCALE DATA
# ============================================================

FACEBOOK_LOCALES = [
    {"locale": "id_ID", "language": "Indonesian", "accept_lang": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Indonesia"},
    {"locale": "ms_MY", "language": "Malay", "accept_lang": "ms-MY,ms;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Malaysia"},
    {"locale": "en_US", "language": "English (US)", "accept_lang": "en-US,en;q=0.9", "country": "United States"},
    {"locale": "en_GB", "language": "English (UK)", "accept_lang": "en-GB,en;q=0.9", "country": "United Kingdom"},
    {"locale": "en_AU", "language": "English (Australia)", "accept_lang": "en-AU,en;q=0.9", "country": "Australia"},
    {"locale": "en_CA", "language": "English (Canada)", "accept_lang": "en-CA,en;q=0.9", "country": "Canada"},
    {"locale": "en_IN", "language": "English (India)", "accept_lang": "en-IN,en;q=0.9", "country": "India"},
    {"locale": "en_NZ", "language": "English (New Zealand)", "accept_lang": "en-NZ,en;q=0.9", "country": "New Zealand"},
    {"locale": "en_IE", "language": "English (Ireland)", "accept_lang": "en-IE,en;q=0.9", "country": "Ireland"},
    {"locale": "en_ZA", "language": "English (South Africa)", "accept_lang": "en-ZA,en;q=0.9", "country": "South Africa"},
    {"locale": "en_SG", "language": "English (Singapore)", "accept_lang": "en-SG,en;q=0.9", "country": "Singapore"},
    {"locale": "en_PH", "language": "English (Philippines)", "accept_lang": "en-PH,en;q=0.9", "country": "Philippines"},
    {"locale": "en_NG", "language": "English (Nigeria)", "accept_lang": "en-NG,en;q=0.9", "country": "Nigeria"},
    {"locale": "en_KE", "language": "English (Kenya)", "accept_lang": "en-KE,en;q=0.9", "country": "Kenya"},
    {"locale": "en_GH", "language": "English (Ghana)", "accept_lang": "en-GH,en;q=0.9", "country": "Ghana"},
    {"locale": "en_PK", "language": "English (Pakistan)", "accept_lang": "en-PK,en;q=0.9", "country": "Pakistan"},
    {"locale": "en_BD", "language": "English (Bangladesh)", "accept_lang": "en-BD,en;q=0.9", "country": "Bangladesh"},
    {"locale": "en_LK", "language": "English (Sri Lanka)", "accept_lang": "en-LK,en;q=0.9", "country": "Sri Lanka"},
    {"locale": "en_MY", "language": "English (Malaysia)", "accept_lang": "en-MY,en;q=0.9", "country": "Malaysia"},
    {"locale": "en_HK", "language": "English (Hong Kong)", "accept_lang": "en-HK,en;q=0.9", "country": "Hong Kong"},
    {"locale": "en_JM", "language": "English (Jamaica)", "accept_lang": "en-JM,en;q=0.9", "country": "Jamaica"},
    {"locale": "en_TT", "language": "English (Trinidad)", "accept_lang": "en-TT,en;q=0.9", "country": "Trinidad and Tobago"},
    {"locale": "de_DE", "language": "German", "accept_lang": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Germany"},
    {"locale": "de_AT", "language": "German (Austria)", "accept_lang": "de-AT,de;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Austria"},
    {"locale": "de_CH", "language": "German (Switzerland)", "accept_lang": "de-CH,de;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Switzerland"},
    {"locale": "fr_FR", "language": "French", "accept_lang": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7", "country": "France"},
    {"locale": "fr_CA", "language": "French (Canada)", "accept_lang": "fr-CA,fr;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Canada"},
    {"locale": "fr_BE", "language": "French (Belgium)", "accept_lang": "fr-BE,fr;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Belgium"},
    {"locale": "fr_CH", "language": "French (Switzerland)", "accept_lang": "fr-CH,fr;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Switzerland"},
    {"locale": "es_ES", "language": "Spanish", "accept_lang": "es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Spain"},
    {"locale": "es_LA", "language": "Spanish (Latin America)", "accept_lang": "es-LA,es;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Latin America"},
    {"locale": "es_MX", "language": "Spanish (Mexico)", "accept_lang": "es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Mexico"},
    {"locale": "es_AR", "language": "Spanish (Argentina)", "accept_lang": "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Argentina"},
    {"locale": "es_CO", "language": "Spanish (Colombia)", "accept_lang": "es-CO,es;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Colombia"},
    {"locale": "es_CL", "language": "Spanish (Chile)", "accept_lang": "es-CL,es;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Chile"},
    {"locale": "es_PE", "language": "Spanish (Peru)", "accept_lang": "es-PE,es;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Peru"},
    {"locale": "es_VE", "language": "Spanish (Venezuela)", "accept_lang": "es-VE,es;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Venezuela"},
    {"locale": "pt_BR", "language": "Portuguese (Brazil)", "accept_lang": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Brazil"},
    {"locale": "pt_PT", "language": "Portuguese", "accept_lang": "pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Portugal"},
    {"locale": "it_IT", "language": "Italian", "accept_lang": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Italy"},
    {"locale": "nl_NL", "language": "Dutch", "accept_lang": "nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Netherlands"},
    {"locale": "nl_BE", "language": "Dutch (Belgium)", "accept_lang": "nl-BE,nl;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Belgium"},
    {"locale": "pl_PL", "language": "Polish", "accept_lang": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Poland"},
    {"locale": "ru_RU", "language": "Russian", "accept_lang": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Russia"},
    {"locale": "uk_UA", "language": "Ukrainian", "accept_lang": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Ukraine"},
    {"locale": "cs_CZ", "language": "Czech", "accept_lang": "cs-CZ,cs;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Czech Republic"},
    {"locale": "sk_SK", "language": "Slovak", "accept_lang": "sk-SK,sk;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Slovakia"},
    {"locale": "hu_HU", "language": "Hungarian", "accept_lang": "hu-HU,hu;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Hungary"},
    {"locale": "ro_RO", "language": "Romanian", "accept_lang": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Romania"},
    {"locale": "bg_BG", "language": "Bulgarian", "accept_lang": "bg-BG,bg;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Bulgaria"},
    {"locale": "hr_HR", "language": "Croatian", "accept_lang": "hr-HR,hr;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Croatia"},
    {"locale": "sr_RS", "language": "Serbian", "accept_lang": "sr-RS,sr;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Serbia"},
    {"locale": "sl_SI", "language": "Slovenian", "accept_lang": "sl-SI,sl;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Slovenia"},
    {"locale": "bs_BA", "language": "Bosnian", "accept_lang": "bs-BA,bs;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Bosnia"},
    {"locale": "mk_MK", "language": "Macedonian", "accept_lang": "mk-MK,mk;q=0.9,en-US;q=0.8,en;q=0.7", "country": "North Macedonia"},
    {"locale": "sq_AL", "language": "Albanian", "accept_lang": "sq-AL,sq;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Albania"},
    {"locale": "el_GR", "language": "Greek", "accept_lang": "el-GR,el;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Greece"},
    {"locale": "tr_TR", "language": "Turkish", "accept_lang": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Turkey"},
    {"locale": "ar_AR", "language": "Arabic", "accept_lang": "ar-AR,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Arab World"},
    {"locale": "ar_SA", "language": "Arabic (Saudi)", "accept_lang": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Saudi Arabia"},
    {"locale": "ar_EG", "language": "Arabic (Egypt)", "accept_lang": "ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Egypt"},
    {"locale": "ar_MA", "language": "Arabic (Morocco)", "accept_lang": "ar-MA,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Morocco"},
    {"locale": "ar_DZ", "language": "Arabic (Algeria)", "accept_lang": "ar-DZ,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Algeria"},
    {"locale": "ar_TN", "language": "Arabic (Tunisia)", "accept_lang": "ar-TN,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Tunisia"},
    {"locale": "ar_IQ", "language": "Arabic (Iraq)", "accept_lang": "ar-IQ,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Iraq"},
    {"locale": "ar_JO", "language": "Arabic (Jordan)", "accept_lang": "ar-JO,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Jordan"},
    {"locale": "ar_LB", "language": "Arabic (Lebanon)", "accept_lang": "ar-LB,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Lebanon"},
    {"locale": "ar_AE", "language": "Arabic (UAE)", "accept_lang": "ar-AE,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "UAE"},
    {"locale": "ar_KW", "language": "Arabic (Kuwait)", "accept_lang": "ar-KW,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Kuwait"},
    {"locale": "ar_QA", "language": "Arabic (Qatar)", "accept_lang": "ar-QA,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Qatar"},
    {"locale": "ar_BH", "language": "Arabic (Bahrain)", "accept_lang": "ar-BH,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Bahrain"},
    {"locale": "ar_OM", "language": "Arabic (Oman)", "accept_lang": "ar-OM,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Oman"},
    {"locale": "ar_LY", "language": "Arabic (Libya)", "accept_lang": "ar-LY,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Libya"},
    {"locale": "ar_SD", "language": "Arabic (Sudan)", "accept_lang": "ar-SD,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Sudan"},
    {"locale": "ar_YE", "language": "Arabic (Yemen)", "accept_lang": "ar-YE,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Yemen"},
    {"locale": "ar_SY", "language": "Arabic (Syria)", "accept_lang": "ar-SY,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Syria"},
    {"locale": "ar_PS", "language": "Arabic (Palestine)", "accept_lang": "ar-PS,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Palestine"},
    {"locale": "fa_IR", "language": "Persian", "accept_lang": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Iran"},
    {"locale": "he_IL", "language": "Hebrew", "accept_lang": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Israel"},
    {"locale": "hi_IN", "language": "Hindi", "accept_lang": "hi-IN,hi;q=0.9,en-US;q=0.8,en;q=0.7", "country": "India"},
    {"locale": "bn_IN", "language": "Bengali", "accept_lang": "bn-IN,bn;q=0.9,en-US;q=0.8,en;q=0.7", "country": "India"},
    {"locale": "ta_IN", "language": "Tamil", "accept_lang": "ta-IN,ta;q=0.9,en-US;q=0.8,en;q=0.7", "country": "India"},
    {"locale": "te_IN", "language": "Telugu", "accept_lang": "te-IN,te;q=0.9,en-US;q=0.8,en;q=0.7", "country": "India"},
    {"locale": "ml_IN", "language": "Malayalam", "accept_lang": "ml-IN,ml;q=0.9,en-US;q=0.8,en;q=0.7", "country": "India"},
    {"locale": "kn_IN", "language": "Kannada", "accept_lang": "kn-IN,kn;q=0.9,en-US;q=0.8,en;q=0.7", "country": "India"},
    {"locale": "mr_IN", "language": "Marathi", "accept_lang": "mr-IN,mr;q=0.9,en-US;q=0.8,en;q=0.7", "country": "India"},
    {"locale": "gu_IN", "language": "Gujarati", "accept_lang": "gu-IN,gu;q=0.9,en-US;q=0.8,en;q=0.7", "country": "India"},
    {"locale": "pa_IN", "language": "Punjabi", "accept_lang": "pa-IN,pa;q=0.9,en-US;q=0.8,en;q=0.7", "country": "India"},
    {"locale": "ur_PK", "language": "Urdu", "accept_lang": "ur-PK,ur;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Pakistan"},
    {"locale": "ne_NP", "language": "Nepali", "accept_lang": "ne-NP,ne;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Nepal"},
    {"locale": "si_LK", "language": "Sinhala", "accept_lang": "si-LK,si;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Sri Lanka"},
    {"locale": "th_TH", "language": "Thai", "accept_lang": "th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Thailand"},
    {"locale": "vi_VN", "language": "Vietnamese", "accept_lang": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Vietnam"},
    {"locale": "tl_PH", "language": "Filipino", "accept_lang": "tl-PH,tl;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Philippines"},
    {"locale": "ja_JP", "language": "Japanese", "accept_lang": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Japan"},
    {"locale": "ko_KR", "language": "Korean", "accept_lang": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7", "country": "South Korea"},
    {"locale": "zh_CN", "language": "Chinese (Simplified)", "accept_lang": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7", "country": "China"},
    {"locale": "zh_TW", "language": "Chinese (Traditional)", "accept_lang": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Taiwan"},
    {"locale": "zh_HK", "language": "Chinese (Hong Kong)", "accept_lang": "zh-HK,zh;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Hong Kong"},
    {"locale": "jv_ID", "language": "Javanese", "accept_lang": "jv-ID,jv;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Indonesia"},
    {"locale": "su_ID", "language": "Sundanese", "accept_lang": "su-ID,su;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Indonesia"},
    {"locale": "da_DK", "language": "Danish", "accept_lang": "da-DK,da;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Denmark"},
    {"locale": "fi_FI", "language": "Finnish", "accept_lang": "fi-FI,fi;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Finland"},
    {"locale": "nb_NO", "language": "Norwegian (Bokmal)", "accept_lang": "nb-NO,nb;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Norway"},
    {"locale": "sv_SE", "language": "Swedish", "accept_lang": "sv-SE,sv;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Sweden"},
    {"locale": "et_EE", "language": "Estonian", "accept_lang": "et-EE,et;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Estonia"},
    {"locale": "lv_LV", "language": "Latvian", "accept_lang": "lv-LV,lv;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Latvia"},
    {"locale": "lt_LT", "language": "Lithuanian", "accept_lang": "lt-LT,lt;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Lithuania"},
    {"locale": "ka_GE", "language": "Georgian", "accept_lang": "ka-GE,ka;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Georgia"},
    {"locale": "hy_AM", "language": "Armenian", "accept_lang": "hy-AM,hy;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Armenia"},
    {"locale": "mn_MN", "language": "Mongolian", "accept_lang": "mn-MN,mn;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Mongolia"},
    {"locale": "my_MM", "language": "Burmese", "accept_lang": "my-MM,my;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Myanmar"},
    {"locale": "km_KH", "language": "Khmer", "accept_lang": "km-KH,km;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Cambodia"},
    {"locale": "lo_LA", "language": "Lao", "accept_lang": "lo-LA,lo;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Laos"},
    {"locale": "sw_KE", "language": "Swahili", "accept_lang": "sw-KE,sw;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Kenya"},
    {"locale": "af_ZA", "language": "Afrikaans", "accept_lang": "af-ZA,af;q=0.9,en-US;q=0.8,en;q=0.7", "country": "South Africa"},
    {"locale": "zu_ZA", "language": "Zulu", "accept_lang": "zu-ZA,zu;q=0.9,en-US;q=0.8,en;q=0.7", "country": "South Africa"},
    {"locale": "xh_ZA", "language": "Xhosa", "accept_lang": "xh-ZA,xh;q=0.9,en-US;q=0.8,en;q=0.7", "country": "South Africa"},
    {"locale": "sn_ZW", "language": "Shona", "accept_lang": "sn-ZW,sn;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Zimbabwe"},
    {"locale": "am_ET", "language": "Amharic", "accept_lang": "am-ET,am;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Ethiopia"},
    {"locale": "ha_NG", "language": "Hausa", "accept_lang": "ha-NG,ha;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Nigeria"},
    {"locale": "ig_NG", "language": "Igbo", "accept_lang": "ig-NG,ig;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Nigeria"},
    {"locale": "yo_NG", "language": "Yoruba", "accept_lang": "yo-NG,yo;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Nigeria"},
    {"locale": "rw_RW", "language": "Kinyarwanda", "accept_lang": "rw-RW,rw;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Rwanda"},
    {"locale": "mg_MG", "language": "Malagasy", "accept_lang": "mg-MG,mg;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Madagascar"},
    {"locale": "ht_HT", "language": "Haitian Creole", "accept_lang": "ht-HT,ht;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Haiti"},
    {"locale": "eo_EO", "language": "Esperanto", "accept_lang": "eo-EO,eo;q=0.9,en-US;q=0.8,en;q=0.7", "country": "International"},
    {"locale": "kk_KZ", "language": "Kazakh", "accept_lang": "kk-KZ,kk;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Kazakhstan"},
    {"locale": "uz_UZ", "language": "Uzbek", "accept_lang": "uz-UZ,uz;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Uzbekistan"},
    {"locale": "ky_KG", "language": "Kyrgyz", "accept_lang": "ky-KG,ky;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Kyrgyzstan"},
    {"locale": "tg_TJ", "language": "Tajik", "accept_lang": "tg-TJ,tg;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Tajikistan"},
    {"locale": "tk_TM", "language": "Turkmen", "accept_lang": "tk-TM,tk;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Turkmenistan"},
    {"locale": "az_AZ", "language": "Azerbaijani", "accept_lang": "az-AZ,az;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Azerbaijan"},
]

current_locale = None


def get_random_fb_locale():
    global current_locale
    current_locale = random.choice(FACEBOOK_LOCALES)
    return current_locale["accept_lang"]


def get_current_locale_info():
    return current_locale


def show_locale_info():
    locale_info = get_current_locale_info()
    if locale_info:
        console.print(Panel(
            f'[bold cyan]Locale:[/bold cyan] {locale_info["locale"]}'
            f'\n[bold cyan]Language:[/bold cyan] {locale_info["language"]}'
            f'\n[bold cyan]Country:[/bold cyan] {locale_info["country"]}'
            f'\n[bold cyan]Accept-Language:[/bold cyan] {locale_info["accept_lang"]}',
            title="CURRENT LOCALE"
        ))
    else:
        console.print("[yellow]Belum ada locale yang dipilih[/yellow]")


def show_all_locales():
    console.print(Panel(
        f'[bold cyan]Total: {len(FACEBOOK_LOCALES)} Locale Tersedia[/bold cyan]',
        title="DAFTAR FULL LOCALE",
        border_style="bold magenta"
    ))
    table = Table(border_style="cyan")
    table.add_column("No", style="dim")
    table.add_column("Locale Code", style="bold cyan")
    table.add_column("Language", style="bold white")
    table.add_column("Country", style="bold green")
    for i, loc in enumerate(FACEBOOK_LOCALES):
        table.add_row(str(i + 1), loc["locale"], loc["language"], loc["country"])
    console.print(table)
    input("\nTekan Enter untuk kembali...")


# ============================================================
# GLOBAL STATE
# ============================================================

country_codes = [loc["locale"] for loc in FACEBOOK_LOCALES]
selected_country_code = random.choice(country_codes)

try:
    ua = UserAgent()
except Exception as e:
    console.print(f"[bold yellow]Peringatan: Gagal inisialisasi UserAgent: {e}[/bold yellow]")
    ua = None

status = {"live": 0, "cp": 0, "loop": 0}
settings = {
    "limit": 10,
    "password": "FOUNDER",
    "use_temp_email": False,
    "use_real_email": True,
    "use_contact_file": False,
    "contact_file": "",
    "contact_list": [],
    "random_locale": "random",
    "gender_setting": "random",
}

try:
    SAVE_DIR = Path("/sdcard/FACEBOOKME")
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    console.print(f"[bold green]Folder penyimpanan: {SAVE_DIR}[/bold green]")
except OSError:
    cwd = Path.cwd()
    SAVE_DIR = cwd / "FACEBOOKME"
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    console.print(f"[bold yellow]Menggunakan folder alternatif: {SAVE_DIR}[/bold yellow]")

SAVE_FILE = SAVE_DIR / "fbfreshmu.txt"
LOG_FILE = SAVE_DIR / "fb_accounts_log.txt"

faker = Faker()


# ============================================================
# VALIDATION UTILITIES
# ============================================================

def normalize_phone_number(phone, auto_add_plus=True):
    cleaned = re.sub(r"[\s\-\(\)]", "", str(phone).strip())
    cleaned = cleaned.replace("++", "+")
    if auto_add_plus and not cleaned.startswith("+") and not cleaned.startswith("0"):
        cleaned = "+" + cleaned
    return cleaned


def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone(phone):
    phone_digits = re.sub(r"[\s\-\(\)]", "", str(phone).replace("+", ""))
    return len(phone_digits) >= 8 and phone_digits.isdigit()


# ============================================================
# CONTACT FILE MANAGEMENT
# ============================================================

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
            if clean_line_no_space == clean_original and not removed:
                removed = True
            else:
                new_lines.append(line)
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    except Exception as e:
        console.print(f"[bold red]Gagal menghapus contact dari file: {e}[/bold red]")


def load_contact_file(file_path):
    try:
        if not os.path.exists(file_path):
            console.print(f"[bold red]File tidak ditemukan: {file_path}[/bold red]")
            return []
        contacts = []
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "@" in line:
                if validate_email(line):
                    contacts.append({"type": "email", "value": line, "original": line})
                    console.print(f"[green]\u2713 Baris {line_num}: Email valid - {line}[/green]")
                else:
                    console.print(f"[yellow]\u26a0 Baris {line_num}: Format tidak dikenali - {line}[/yellow]")
            elif validate_phone(line):
                contact = line
                original_format = line
                cleaned_value = re.sub(r"[\s\-\(\)]", "", line)
                if not cleaned_value.startswith("+"):
                    final_value = "+" + cleaned_value
                    console.print(f"[yellow]\u26a0 Baris {line_num}: Nomor {original_format} \u2192 ditambahkan + menjadi {final_value}[/yellow]")
                else:
                    final_value = cleaned_value
                    console.print(f"[green]\u2713 Baris {line_num}: Nomor valid - {final_value}[/green]")
                contacts.append({"type": "phone", "value": final_value, "original": original_format})
            else:
                console.print(f"[yellow]\u26a0 Baris {line_num}: Format tidak dikenali - {line} \u2192 {line}[/yellow]")
        console.print(f"[bold cyan]Total contact valid: {len(contacts)}[/bold cyan]")
        return contacts
    except Exception as e:
        console.print(f"[bold red]Gagal membaca file: {e}[/bold red]")
        return []


def create_contact_file_example():
    example_path = SAVE_DIR / "contact_example.txt"
    example_content = (
        "# Contoh file contact untuk Facebook Creator Tools\n"
        "# ================================================\n"
        "# PENTING: \n"
        "# - Setiap nomor/email yang BERHASIL didaftarkan akan OTOMATIS DIHAPUS dari file ini\n"
        "# - Nomor telepon akan OTOMATIS ditambahkan + jika belum ada\n"
        "# \n"
        "# Format yang didukung:\n"
        "# 1. Email: user@domain.com\n"
        "# 2. Nomor dengan +: +6281234567890\n"
        "# 3. Nomor tanpa +: 6281234567890 (akan jadi +6281234567890)\n"
        "# 4. Nomor lokal: 081234567890 (akan jadi +081234567890)\n"
        "#\n"
        "# Baris yang diawali dengan # akan diabaikan\n"
        "# ================================================\n"
        "\n"
        "user1@gmail.com\n"
        "user2@yahoo.com\n"
        "+6281234567890\n"
        "081234567890\n"
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
        "\u2713 Contact yang [bold red]BERHASIL didaftarkan[/bold red] akan otomatis dihapus dari file",
        title="PANDUAN CONTACT FILE"
    ))


def show_contact_list():
    if not settings["contact_list"]:
        console.print("[bold yellow]Belum ada file contact yang dimuat.[/bold yellow]")
        return
    contact_list = settings["contact_list"]
    text = (
        f'[bold cyan]Daftar Contact yang Dimuat:[/bold cyan]\n'
        f'Total: {len(contact_list)} contact\n'
        f'File: {settings["contact_file"]}\n'
        f'[dim][yellow]\u26a0 Contact yang berhasil didaftarkan akan otomatis dihapus dari file[/yellow][/dim]'
    )
    console.print(Panel(text, title="CONTACT LIST"))
    for i, contact in enumerate(contact_list):
        type_icon = "\u2709" if contact["type"] == "email" else "\U0001f4f1"
        line = f'{i + 1}. {type_icon} {contact["original"]}'
        if contact["value"] != contact["original"]:
            line += f'   [dim]\u2192 akan digunakan: {contact["value"]}[/dim]'
        console.print(line)
        if i >= 19:
            console.print(f"[dim]... dan {len(contact_list) - 20} contact lainnya[/dim]")
            break
    email_count = sum(1 for c in contact_list if c["type"] == "email")
    phone_count = sum(1 for c in contact_list if c["type"] != "email")
    console.print(f"\n[bold]Statistik:[/bold] Email: {email_count}, Nomor: {phone_count}")


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def get_public_ip():
    try:
        return requests.get("https://api.ipify.org").text
    except requests.ConnectionError as e:
        console.print(f"[bold yellow]Peringatan: Koneksi gagal saat mengambil IP: {e}[/bold yellow]")
        return "Tidak dapat mengambil IP"
    except requests.Timeout as e:
        console.print(f"[bold yellow]Peringatan: Timeout saat mengambil IP: {e}[/bold yellow]")
        return "Tidak dapat mengambil IP"
    except Exception as e:
        console.print(f"[bold yellow]Peringatan: Gagal mengambil IP publik: {e}[/bold yellow]")
        return "Tidak dapat mengambil IP"


def ugen():
    android_devices = (
        "SM-G950F", "SM-G960F", "SM-G970F", "SM-G973F", "SM-G991B", "SM-G996B",
        "SM-G998B", "SM-S901B", "SM-S906B", "SM-S908B", "SM-S921B", "SM-S926B",
        "Redmi Note 7", "Redmi Note 8", "Redmi Note 9 Pro", "Redmi Note 10",
        "Redmi Note 11", "Redmi Note 12", "Redmi Note 13", "Mi 10T Pro", "Mi 11",
        "Xiaomi 12", "POCO F1", "POCO X3 Pro", "POCO F4", "POCO X6 Pro",
        "CPH1909", "CPH2023", "CPH2219", "CPH2239", "CPH2413", "CPH2481", "CPH2555",
        "V2023", "V2031", "V2043", "V2050", "V2111", "V2141", "V2241", "V2312",
        "RMX1941", "RMX2001", "RMX3081", "RMX3363", "RMX3686", "RMX3840",
        "Infinix X650", "Infinix X688B", "Infinix X683", "Infinix X670",
        "Infinix X695", "Infinix X671B",
        "ANE-LX2", "PRA-LA1", "MAR-LX1M", "JNY-LX2", "LYA-L29", "ELE-L29",
        "TAS-L29", "VOG-L29", "ANA-NX9",
        "Pixel 3a", "Pixel 4a", "Pixel 5", "Pixel 6", "Pixel 6a", "Pixel 7",
        "Pixel 8", "Pixel 8 Pro",
    )
    android_map = ("PKQ1", "QKQ1", "RKQ1", "SKQ1", "TKQ1", "UKQ1")
    android_version = random.randint(9, 14)
    build_prefix = random.choice(android_map)
    build_date = f"{random.randint(200000, 249999):03d}"
    build_number = f".{random.randint(1, 999):03d}"
    build_full = build_prefix + build_date + build_number
    chrome_major = random.randint(95, 129)
    chrome_build = f"{chrome_major}.0.{random.randint(4600, 6999)}.{random.randint(30, 200)}"
    device = random.choice(android_devices)
    return (
        f"Mozilla/5.0 (Linux; Android {android_version}; {device}"
        f" Build/{build_full}; wv) AppleWebKit/537.36 (KHTML, like Gecko)"
        f" Version/4.0 Chrome/{chrome_build} Mobile Safari/537.36"
    )


# ============================================================
# HTML EXTRACTION
# ============================================================

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
        "jazoest": (
            r'name="jazoest"\s+(?:value|content)="(\d+)"',
            r'jazoest"?\s*[:=]\s*"(\d+)"',
            r'"jazoest"\s*:\s*"(\d+)"',
            r'jazoest[=:](\d+)',
        ),
        "lsd": (
            r'name="lsd"\s+(?:value|content)="([^"]+)"',
            r'lsd"?\s*[:=]\s*"([^"]+)"',
            r'"lsd"\s*:\s*"([^"]+)"',
            r'lsd[=:]([^&\s"]+)',
        ),
        "fb_dtsg": (
            r'name="fb_dtsg"\s+(?:value|content)="([^"]+)"',
            r'fb_dtsg"?\s*[:=]\s*"([^"]+)"',
            r'"fb_dtsg"\s*:\s*"([^"]+)"',
            r'fb_dtsg[=:]([^&\s"]+)',
        ),
        "__user": (
            r'name="__user"\s+(?:value|content)="([^"]+)"',
            r'__user"?\s*[:=]\s*"([^"]+)"',
            r'"__user"\s*:\s*"([^"]+)"',
            r'__user[=:]([^&\s"]+)',
        ),
        "__a": (
            r'name="__a"\s+(?:value|content)="([^"]+)"',
            r'__a"?\s*[:=]\s*"([^"]+)"',
            r'"__a"\s*:\s*"([^"]+)"',
            r'__a[=:]([^&\s"]+)',
        ),
        "__dyn": (
            r'name="__dyn"\s+(?:value|content)="([^"]+)"',
            r'__dyn"?\s*[:=]\s*"([^"]+)"',
            r'"__dyn"\s*:\s*"([^"]+)"',
            r'__dyn[=:]([^&\s"]+)',
        ),
        "__req": (
            r'name="__req"\s+(?:value|content)="([^"]+)"',
            r'__req"?\s*[:=]\s*"([^"]+)"',
            r'"__req"\s*:\s*"([^"]+)"',
            r'__req[=:]([^&\s"]+)',
        ),
        "__csrf": (
            r'name="__csrf"\s+(?:value|content)="([^"]+)"',
            r'__csrf"?\s*[:=]\s*"([^"]+)"',
            r'"__csrf"\s*:\s*"([^"]+)"',
            r'__csrf[=:]([^&\s"]+)',
        ),
        "__fmt": (
            r'name="__fmt"\s+(?:value|content)="([^"]+)"',
            r'__fmt"?\s*[:=]\s*"([^"]+)"',
            r'"__fmt"\s*:\s*"([^"]+)"',
            r'__fmt[=:]([^&\s"]+)',
        ),
        "reg_instance": (
            r'name="reg_instance"\s+(?:value|content)="([^"]+)"',
            r'reg_instance"?\s*[:=]\s*"([^"]+)"',
            r'"reg_instance"\s*:\s*"([^"]+)"',
        ),
        "reg_impression_id": (
            r'name="reg_impression_id"\s+(?:value|content)="([^"]+)"',
            r'reg_impression_id"?\s*[:=]\s*"([^"]+)"',
            r'"reg_impression_id"\s*:\s*"([^"]+)"',
        ),
        "app_id": (
            r'name="app_id"\s+(?:value|content)="([^"]+)"',
            r'app_id"?\s*[:=]\s*"([^"]+)"',
            r'"app_id"\s*:\s*"([^"]+)"',
        ),
        "logger_id": (
            r'name="logger_id"\s+(?:value|content)="([^"]+)"',
            r'logger_id"?\s*[:=]\s*"([^"]+)"',
            r'"logger_id"\s*:\s*"([^"]+)"',
        ),
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


# ============================================================
# EMAIL / CONTACT GENERATION
# ============================================================

def get_email():
    if settings.get("use_contact_file") and settings.get("contact_list"):
        contact = settings["contact_list"][status["loop"] % len(settings["contact_list"])]
        return contact["value"], contact
    if settings.get("use_temp_email"):
        temp_domains = (
            "@1secmail.com", "@tempmail.net", "@tempmailo.com", "@maildrop.cc",
            "@guerrillamail.com", "@getnada.com", "@yopmail.com",
            "@mailinator.com", "@trashmail.com", "@fakemail.net",
        )
        email = faker.first_name().lower() + str(random.randint(10, 9999)) + random.choice(temp_domains)
        return email, None
    if settings.get("use_real_email"):
        domains = (
            "@gmail.com", "@yahoo.com", "@outlook.com", "@hotmail.com",
            "@icloud.com", "@aol.com", "@protonmail.com",
        )
        username = faker.first_name().lower() + "." + faker.last_name().lower() + str(random.randint(1, 9999))
        email = username + random.choice(domains)
        return email, None
    prefixes = (
        "+62811", "+62812", "+62813", "+62814", "+62815", "+62816", "+62817",
        "+62818", "+62819", "+62821", "+62822", "+62823", "+62831", "+62832",
        "+62833", "+62838", "+62851", "+62852", "+62853", "+62855", "+62856",
        "+62857", "+62858", "+62859", "+62877", "+62878", "+62879", "+62895",
        "+62896", "+62897", "+62898", "+62899",
    )
    phone = random.choice(prefixes) + str(random.randint(10000000, 99999999))
    return phone, None


# ============================================================
# FACEBOOK PROFILE CHECK
# ============================================================

def get_facebook_profile_info(uid):
    try:
        r = requests.get(f"https://www.facebook.com/{uid}")
        if r.status_code != 200:
            console.print(f"[bold yellow]Peringatan: HTTP {r.status_code} saat mengakses profil UID {uid}[/bold yellow]")
            return "Profil tidak dapat diakses"
        soup = bs(r.text, "html.parser")
        title = soup.find("title")
        if title and title.text:
            return title.text
        return "Nama tidak ditemukan"
    except requests.ConnectionError as e:
        console.print(f"[bold red]Error koneksi saat mengakses profil UID {uid}: {e}[/bold red]")
        return "Error saat mengakses profil"
    except requests.Timeout as e:
        console.print(f"[bold red]Timeout saat mengakses profil UID {uid}: {e}[/bold red]")
        return "Error saat mengakses profil"
    except Exception as e:
        console.print(f"[bold red]Error saat mengakses profil UID {uid}: {e}[/bold red]")
        return "Error saat mengakses profil"


def check(uidku):
    try:
        r = requests.get(f"https://www.facebook.com/{uidku}")
        if r.status_code == 200:
            soup = bs(r.text, "html.parser")
            title = soup.find("title")
            nama = title.text if title and title.text else "Nama tidak ditemukan"
            console.print(f"[bold green]UID {uidku} -> {nama}[/bold green]")
        else:
            console.print(f"[bold red]UID {uidku} tidak dapat diakses (HTTP {r.status_code})[/bold red]")
    except requests.ConnectionError as e:
        console.print(f"[bold red]Error koneksi saat mengakses UID {uidku}: {e}[/bold red]")
    except requests.Timeout as e:
        console.print(f"[bold red]Timeout saat mengakses UID {uidku}: {e}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error saat mengakses UID {uidku}: {e}[/bold red]")


# ============================================================
# ACCOUNT PERSISTENCE
# ============================================================

def save_account_to_file(account_data):
    try:
        line = account_data["uid"] + "|" + account_data["password"]
        with open(SAVE_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        log_content = "\n".join([
            "==================================================",
            f'UID: {account_data["uid"]}',
            f'Password: {account_data["password"]}',
            f'Email/No: {account_data["email"]}',
            f'Nama Lengkap: {account_data["nama"]}',
            f'Jenis Kelamin: {account_data["gender"]}',
            f'Tanggal Lahir: {account_data["tgl_lahir"]}',
            f'Tanggal Dibuat: {account_data["timestamp"]}',
            f'Cookie: {account_data["cookie"]}',
            "",
        ])
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_content + "\n")
    except PermissionError as e:
        console.print(f"[bold red]Gagal menyimpan akun (izin ditolak): {e}[/bold red]")
    except OSError as e:
        console.print(f"[bold red]Gagal menyimpan akun (error I/O): {e}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Gagal menyimpan akun: {e}[/bold red]")


def count_saved_accounts():
    try:
        if not SAVE_FILE.exists():
            return 0
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return sum(1 for line in lines if line.strip())
    except PermissionError as e:
        console.print(f"[bold yellow]Peringatan: Tidak bisa membaca file akun (izin ditolak): {e}[/bold yellow]")
        return 0
    except Exception as e:
        console.print(f"[bold yellow]Peringatan: Gagal menghitung akun tersimpan: {e}[/bold yellow]")
        return 0


# ============================================================
# LICENSE VALIDATION
# ============================================================

def approval():
    clear_screen()
    console.print(Panel("[bold cyan]Validasi Lisensi...[/bold cyan]", title="LICENSE"))
    time.sleep(1)

    uid_val = getattr(os, "getuid", lambda: 0)()
    user_login = getpass.getuser()
    device_id = socket.gethostname().upper()
    device_name = device_id

    def rnum():
        return str(random.randint(1, 9))

    def rlet():
        return random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    random.seed(user_login)
    letters = []
    for c in user_login:
        if c.isalpha():
            letters.append(c.upper())
    if len(letters) < 3:
        letters.append("X")
    license_parts = [
        "FOUNDER-",
        "".join(letters[:3]),
        rnum(), rnum(),
        "-",
        rlet(), rlet(),
        rnum(), rnum(), rnum(),
        "-",
        rlet(),
        rnum(), rnum(),
        rlet(), rlet(),
    ]
    full_license = "".join(license_parts)

    console.print(Panel(
        f"[white]License:[/white]\n[green]{full_license}[/green]",
        title="INFO"
    ))

    try:
        license_url = "https://raw.githubusercontent.com/SllowlyDev/license-key-validation/main/licenses.json"
        res = requests.get(license_url)
        if res.status_code != 200:
            console.print(f"[bold red]Gagal memvalidasi lisensi: HTTP {res.status_code}[/bold red]")
            sys.exit(1)
        valid_keys = []
        for x in res.text.splitlines():
            x = x.strip()
            if x:
                valid_keys.append(x)
        if full_license in valid_keys:
            console.print("[bold green]License Valid![/bold green]")
            time.sleep(1)
        else:
            console.print(Panel(
                f"[yellow]License not registered.[/yellow]\n\n[green]{full_license}[/green]",
                title="ACTIVATION"
            ))
            sys.exit(1)
    except requests.ConnectionError as e:
        console.print(f"[bold red]Gagal terhubung ke server lisensi: {e}[/bold red]")
        sys.exit(1)
    except requests.Timeout as e:
        console.print(f"[bold red]Timeout saat validasi lisensi: {e}[/bold red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error saat validasi lisensi: {e}[/bold red]")
        sys.exit(1)


# ============================================================
# REGISTRATION URL DISPLAY
# ============================================================

def show_registration_url():
    myurl = random.choice([
        "touch.facebook.com", "d.facebook.com", "m.facebook.com",
        "limited.facebook.com", "x.facebook.com", "mbasic.facebook.com",
    ])
    random_token = "".join(random.choices(string.ascii_letters + string.digits, k=random.randint(20, 40)))
    random_hash = "".join(random.choices(string.hexdigits, k=random.randint(20, 40))).upper()
    random_cid = "".join(random.choices(string.digits, k=random.randint(10, 20)))
    random_rwtsid = "".join(random.choices(string.hexdigits, k=random.randint(20, 40))).upper()
    reg_url = (
        f"https://{myurl}/mreg?e_token={random_token}"
        f"&d_hash={random_hash}&cid={random_cid}"
        f"&app_version=310&tg=201&cct=1&src=0&cah=1&rwtsid={random_rwtsid}"
    )
    console.print(Panel(
        f"[bold cyan]URL Registrasi Facebook:[/bold cyan]\n"
        f"[bold green]{reg_url}[/bold green]\n\n"
        f"[dim]Domain yang digunakan: {myurl}[/dim]",
        title="REGISTRATION URL"
    ))


# ============================================================
# GENDER RESOLVER
# ============================================================

def resolve_gender():
    """Resolve gender based on settings['gender_setting']. Returns (code, text)"""
    gs = settings.get("gender_setting", "random")
    if gs == "random":
        gender_code = random.choice(["1", "2"])
    elif gs == "male":
        gender_code = "2"
    elif gs == "female":
        gender_code = "1"
    else:
        gender_code = random.choice(["1", "2"])
    gender_text = "Perempuan" if gender_code == "1" else "Laki-laki"
    return gender_code, gender_text


# ============================================================
# ACCOUNT REGISTRATION (AUTO)
# ============================================================

def register_account():
    email, contact_info = get_email()
    contact_display = email
    for i in range(settings["limit"]):
        console.print(
            f'[grey50]( [bold cyan]{i + 1}[/bold cyan] Akun : '
            f'[grey50]) : ([bold green]Success:[bold green]{status["live"]} [grey50])',
            end="\r"
        )
        sys.stdout.flush()

        try:
            myurl = random.choice([
                "touch.facebook.com", "d.facebook.com", "m.facebook.com",
                "limited.facebook.com", "x.facebook.com", "mbasic.facebook.com",
            ])
            ses = requests.Session()
            random_token = "".join(random.choices(string.ascii_letters + string.digits, k=random.randint(20, 40)))
            random_hash = "".join(random.choices(string.hexdigits, k=random.randint(20, 40))).upper()
            random_cid = "".join(random.choices(string.digits, k=random.randint(10, 20)))
            random_rwtsid = "".join(random.choices(string.hexdigits, k=random.randint(20, 40))).upper()

            reg_url = (
                f"https://{myurl}/mreg?e_token={random_token}"
                f"&d_hash={random_hash}&cid={random_cid}"
                f"&app_version=310&tg=201&cct=1&src=0&cah=1&rwtsid={random_rwtsid}"
            )

            accept_lang = get_random_fb_locale() if settings.get("random_locale") == "random" else "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
            locale_info = get_current_locale_info()

            if locale_info:
                console.print(Panel(
                    f'[bold cyan]Menggunakan Locale:[/bold cyan] {locale_info["locale"]}'
                    f'\n[bold cyan]Language:[/bold cyan] {locale_info["language"]}'
                    f'\n[bold cyan]Country:[/bold cyan] {locale_info["country"]}'
                    f'\n[bold cyan]Gender Setting:[/bold cyan] {settings.get("gender_setting", "random").upper()}',
                    title="RANDOM LOCALE & GENDER"
                ))

            headers_get = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "accept-language": accept_lang,
                "user-agent": ugen(),
                "sec-ch-ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": '"Android"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "upgrade-insecure-requests": "1",
            }

            res = ses.get(reg_url, headers=headers_get)
            if res.status_code != 200:
                console.print(f"[bold red]Gagal mengakses halaman registrasi: HTTP {res.status_code}[/bold red]")
                status["loop"] += 1
                continue

            extracted_data = extract_all_from_html(res.text)
            fb_dtsg = extracted_data.get("fb_dtsg", "")
            jazoest = extracted_data.get("jazoest", "NAfvUo9HbSAZyVEr3Ze2DkSh1kFr46CUODpUQsIl1E6M6S43_DOC7Zw:0:0")
            lsd = extracted_data.get("lsd", "")
            reg_instance = extracted_data.get("reg_instance", "")
            reg_impression_id = extracted_data.get("reg_impression_id", "")
            app_id = extracted_data.get("app_id", "256002347743983")
            logger_id = extracted_data.get("logger_id", "")
            __dyn = extracted_data.get("__dyn", "1Z3pawlEnwm8_Bg9ppoW5UqxK12wAxu13w9y3q327E39x60zU3ex608ewk9E4W0pKq0FE6S0x81vohw5Owk8aE36wqEd8dE2YwbK0iC1qw8W0k-0n6aw4kwbS1Lw9C0le0ue0QU3yw")
            __req = extracted_data.get("__req", "")
            __user = extracted_data.get("__user", "0")
            __a = extracted_data.get("__a", "AYwkI2qG1sefZTwey-Vm7WRWA3RPT1ZCrNAJRz0MhiehwXf8WPdKD-NK4s28ccnUXcXs-McSqtWPWP-PDYhSzcpsYzu-fGJWOIU")
            __fmt = extracted_data.get("__fmt", "")

            fname = faker.first_name().lower()
            lname = faker.last_name().lower()
            fullname = fname + " " + lname
            password = settings["password"]

            birth_day = str(random.randint(1, 28))
            birth_month = str(random.randint(1, 12))
            birth_year = str(random.randint(1985, 2002))
            gender_code, gender_text = resolve_gender()
            tgl_lahir = f"{birth_day}-{birth_month}-{birth_year}"

            encpass = f"#PWD_BROWSER:0:{int(time.time())}:{password}"

            params = {
                "lsd": lsd,
                "jazoest": jazoest,
                "fb_dtsg": fb_dtsg,
                "__dyn": __dyn,
                "__req": __req,
                "__user": __user,
                "__a": __a,
                "__fmt": __fmt,
                "ccp": "2",
                "submission_request": "true",
                "helper": "",
                "ns": "0",
                "zero_header_af_client": "",
                "field_names[0]": "firstname",
                "firstname": fname,
                "field_names[1]": "birthday_wrapper",
                "birthday_day": birth_day,
                "birthday_month": birth_month,
                "birthday_year": birth_year,
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
                "submit": "Daftar",
            }

            data = params

            headers_post = {
                "authority": "m.facebook.com",
                "accept": "*/*",
                "accept-language": accept_lang,
                "content-type": "application/x-www-form-urlencoded",
                "origin": "https://m.facebook.com",
                "referer": reg_url,
                "sec-ch-prefers-color-scheme": "dark",
                "sec-ch-ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
                "sec-ch-ua-full-version-list": '"Chromium";v="139.0.7339.0", "Not;A=Brand";v="99.0.0.0"',
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-model": '"' + random.choice(["Infinix X6881", "SM-G998B", "Redmi Note 11", "Pixel 6"]) + '"',
                "sec-ch-ua-platform": '"Android"',
                "sec-ch-ua-platform-version": '"14.0.0"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": ugen(),
            }

            cookies = ses.cookies.get_dict()
            cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
            headers_post["cookie"] = cookie_str

            reg = ses.post(
                f"https://m.facebook.com/reg/submit/",
                params=params,
                data=data,
                headers=headers_post,
                allow_redirects=True,
            )

            uid = reg.cookies.get("c_user", "")

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
                    "locale": locale_info["locale"] if locale_info else "id_ID",
                    "language": locale_info["language"] if locale_info else "Indonesian",
                }
                save_account_to_file(account_data)
                status["live"] += 1

                if settings.get("use_contact_file") and contact_info:
                    remove_contact_from_file(
                        settings["contact_file"],
                        contact_info["original"],
                    )
                    if contact_info in settings["contact_list"]:
                        settings["contact_list"].remove(contact_info)
                    console.print(f'[bold yellow]\u2713 Contact [{contact_display}] berhasil dihapus dari file.[/bold yellow]')

                table = Table(
                    title="AKUN BERHASIL DIBUAT",
                    show_header=True,
                    title_style="bold green",
                    border_style="green",
                    padding=(0, 1),
                )
                table.add_column("Key", style="bold cyan", no_wrap=True, width=20)
                table.add_column("Value", style="bold white")
                table.add_row("UID|Pass", f'[bold green]{uid}|{password}[/bold green]')
                table.add_row("Nama Lengkap", profile_name)
                table.add_row("Email / Nomor", email)
                table.add_row("Jenis Kelamin", gender_text)
                table.add_row("Tanggal Lahir", tgl_lahir)
                table.add_row("Tanggal Dibuat", created_date)
                if locale_info:
                    table.add_row("Locale", f'[bold cyan]{locale_info["locale"]} ({locale_info["language"]})[/bold cyan]')
                if len(cookie_str) > 100:
                    table.add_row("Cookie (1/2)", f'[bold purple]{cookie_str[:100]}...[/bold purple]')
                    table.add_row("Cookie (2/2)", f'[bold purple]...{cookie_str[100:]}[/bold purple]')
                else:
                    table.add_row("Cookie", cookie_str)
                console.print(table)
            elif "checkpoint" in reg.url or "cp" in reg.url:
                status["cp"] += 1
                console.print("[bold yellow]Akun mungkin masuk checkpoint atau gagal membuat profil.[/bold yellow]")
            else:
                console.print("[bold red]Registrasi gagal. Tidak mendapatkan cookie c_user.[/bold red]")

            status["loop"] += 1
            email, contact_info = get_email()
            contact_display = email
            time.sleep(random.randint(2, 5))

        except requests.ConnectionError as e:
            console.print(f"[bold red]Error koneksi saat registrasi: {e}[/bold red]")
            status["loop"] += 1
            time.sleep(3)
        except requests.Timeout as e:
            console.print(f"[bold red]Timeout saat registrasi: {e}[/bold red]")
            status["loop"] += 1
            time.sleep(3)
        except Exception as e:
            console.print(f"[bold red]Error saat registrasi akun ke-{i + 1}: {e}[/bold red]")
            status["loop"] += 1
            time.sleep(3)


# ============================================================
# MANUAL REGISTRATION
# ============================================================

def register_manual():
    clear_screen()
    show_header_once()
    console.print(Panel(
        "[bold cyan]Registrasi Manual Akun Facebook[/bold cyan]\n\n"
        "Isi data di bawah ini secara manual.\n"
        "Data akan dikirim ke Facebook untuk membuat 1 akun baru.\n"
        "[bold yellow]Tekan Enter kosong untuk menggunakan nilai default (di dalam kurung).[/bold yellow]",
        title="REGISTER MANUAL",
        border_style="cyan"
    ))

    default_fname = faker.first_name().lower()
    first_name = Prompt.ask("[bold cyan]Nama Depan[/bold cyan]", default=default_fname).strip() or default_fname
    default_lname = faker.last_name().lower()
    last_name = Prompt.ask("[bold cyan]Nama Belakang[/bold cyan]", default=default_lname).strip() or default_lname
    fullname = first_name + " " + last_name

    console.print("\n[bold yellow]Format yang didukung:[/bold yellow]")
    console.print("  - Email: contoh@gmail.com")
    console.print("  - Nomor: +6281234567890 atau 081234567890")
    default_contact = "+628" + str(random.randint(10000000, 99999999))
    contact_raw = Prompt.ask("[bold cyan]Email / Nomor Telepon[/bold cyan]", default=default_contact).strip()

    if validate_email(contact_raw):
        final_contact = contact_raw
    elif validate_phone(contact_raw):
        final_contact = normalize_phone_number(contact_raw)
    else:
        console.print("[bold red]\u2717 Format tidak valid! Masukkan email yang benar atau nomor telepon (min 8 digit).[/bold red]")
        return

    default_pw = settings["password"]
    password = Prompt.ask("[bold cyan]Password[/bold cyan]", default=default_pw).strip() or default_pw

    console.print("\n[bold yellow]Tanggal Lahir:[/bold yellow]")
    default_day = str(random.randint(1, 28)).zfill(2)
    default_month = str(random.randint(1, 12)).zfill(2)
    default_year = str(random.randint(1985, 2002))
    birth_day = Prompt.ask("[bold cyan]  Hari (01-31)[/bold cyan]", default=default_day).strip() or default_day
    birth_month = Prompt.ask("[bold cyan]  Bulan (01-12)[/bold cyan]", default=default_month).strip() or default_month
    birth_year = Prompt.ask("[bold cyan]  Tahun (contoh: 1998)[/bold cyan]", default=default_year).strip() or default_year

    try:
        day_int = int(birth_day)
        month_int = int(birth_month)
        year_int = int(birth_year)
    except ValueError:
        console.print("[bold red]Tanggal lahir tidak valid.[/bold red]")
        return

    tgl_lahir = f"{birth_day}-{birth_month}-{birth_year}"

    console.print("\n[bold yellow]Jenis Kelamin:[/bold yellow]")
    console.print("  1. Perempuan")
    console.print("  2. Laki-laki")
    console.print("  3. Random (Acak)")
    gender_choice = Prompt.ask("[bold cyan]Pilih (1/2/3)[/bold cyan]", default="3").strip()
    if gender_choice == "3":
        gender_code, gender_text = resolve_gender()
        console.print(f"  [dim]\u2192 Dipilih random: {gender_text}[/dim]")
    elif gender_choice == "1":
        gender_code, gender_text = "1", "Perempuan"
    else:
        gender_code, gender_text = "2", "Laki-laki"

    console.print(Panel(
        f"[bold white]Nama Lengkap  :[/bold white] [bold green]{fullname}[/bold green]\n"
        f"[bold white]Email / No    :[/bold white] [bold green]{final_contact}[/bold green]\n"
        f"[bold white]Password      :[/bold white] [bold green]{password}[/bold green]\n"
        f"[bold white]Tanggal Lahir :[/bold white] [bold green]{tgl_lahir}[/bold green]\n"
        f"[bold white]Jenis Kelamin :[/bold white] [bold green]{gender_text}[/bold green]",
        title="KONFIRMASI DATA",
        border_style="green"
    ))

    confirm = input("[bold yellow]Lanjutkan registrasi? (y/n)[/bold yellow] ").strip()
    if confirm.lower() != "y":
        console.print("[bold red]Registrasi dibatalkan.[/bold red]")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    console.print("\n[bold cyan]Memulai proses registrasi manual...[/bold cyan]")

    try:
        myurl = random.choice([
            "touch.facebook.com", "d.facebook.com", "m.facebook.com",
            "limited.facebook.com", "x.facebook.com", "mbasic.facebook.com",
        ])
        ses = requests.Session()
        random_token = "".join(random.choices(string.ascii_letters + string.digits, k=random.randint(20, 40)))
        random_hash = "".join(random.choices(string.hexdigits, k=random.randint(20, 40))).upper()
        random_cid = "".join(random.choices(string.digits, k=random.randint(10, 20)))
        random_rwtsid = "".join(random.choices(string.hexdigits, k=random.randint(20, 40))).upper()

        reg_url = (
            f"https://{myurl}/mreg?e_token={random_token}"
            f"&d_hash={random_hash}&cid={random_cid}"
            f"&app_version=310&tg=201&cct=1&src=0&cah=1&rwtsid={random_rwtsid}&soft=hjk"
        )

        accept_lang = get_random_fb_locale() if settings.get("random_locale") == "random" else "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        locale_info = get_current_locale_info()

        headers_get = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "accept-language": accept_lang,
            "user-agent": ugen(),
            "sec-ch-ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "upgrade-insecure-requests": "1",
        }

        res = ses.get(reg_url, headers=headers_get)
        if res.status_code != 200:
            console.print(f"[bold red]Gagal mengakses halaman registrasi: HTTP {res.status_code}[/bold red]")
            input("\nTekan Enter untuk kembali ke menu...")
            return

        extracted_data = extract_all_from_html(res.text)
        fb_dtsg = extracted_data.get("fb_dtsg", "")
        jazoest = extracted_data.get("jazoest", "NAfvUo9HbSAZyVEr3Ze2DkSh1kFr46CUODpUQsIl1E6M6S43_DOC7Zw:0:0")
        lsd = extracted_data.get("lsd", "")
        reg_instance = extracted_data.get("reg_instance", "")
        reg_impression_id = extracted_data.get("reg_impression_id", "")
        app_id = extracted_data.get("app_id", "256002347743983")
        logger_id = extracted_data.get("logger_id", "")
        __dyn = extracted_data.get("__dyn", "1Z3pawlEnwm8_Bg9ppoW5UqxK12wAxu13w9y3q327E39x60zU3ex608ewk9E4W0pKq0FE6S0x81vohw5Owk8aE36wqEd8dE2YwbK0iC1qw8W0k-0n6aw4kwbS1Lw9C0le0ue0QU3yw")
        __req = extracted_data.get("__req", "")
        __user = extracted_data.get("__user", "0")
        __a = extracted_data.get("__a", "AYwkI2qG1sefZTwey-Vm7WRWA3RPT1ZCrNAJRz0MhiehwXf8WPdKD-NK4s28ccnUXcXs-McSqtWPWP-PDYhSzcpsYzu-fGJWOIU")
        __fmt = extracted_data.get("__fmt", "")

        encpass = f"#PWD_BROWSER:0:{int(time.time())}:{password}"

        params = {
            "lsd": lsd,
            "jazoest": jazoest,
            "fb_dtsg": fb_dtsg,
            "__dyn": __dyn,
            "__req": __req,
            "__user": __user,
            "__a": __a,
            "__fmt": __fmt,
            "ccp": "2",
            "submission_request": "true",
            "helper": "",
            "ns": "0",
            "zero_header_af_client": "",
            "field_names[0]": "firstname",
            "firstname": first_name,
            "field_names[1]": "birthday_wrapper",
            "birthday_day": birth_day,
            "birthday_month": birth_month,
            "birthday_year": birth_year,
            "age_step_input": "",
            "did_use_age": "false",
            "field_names[2]": "reg_email__",
            "reg_email__": final_contact,
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
            "submit": "Daftar",
        }

        headers_post = {
            "authority": "m.facebook.com",
            "accept": "*/*",
            "accept-language": accept_lang,
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://m.facebook.com",
            "referer": reg_url,
            "sec-ch-prefers-color-scheme": "dark",
            "sec-ch-ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
            "sec-ch-ua-full-version-list": '"Chromium";v="139.0.7339.0", "Not;A=Brand";v="99.0.0.0"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-model": '"' + random.choice(["Infinix X6881", "SM-G998B", "Redmi Note 11", "Pixel 6"]) + '"',
            "sec-ch-ua-platform": '"Android"',
            "sec-ch-ua-platform-version": '"14.0.0"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": ugen(),
        }

        cookies = ses.cookies.get_dict()
        cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
        headers_post["cookie"] = cookie_str

        console.print("[dim]Mengirim data ke Facebook...[/dim]")
        reg = ses.post(
            f"https://m.facebook.com/reg/submit/",
            params=params,
            data=params,
            headers=headers_post,
            allow_redirects=True,
        )

        uid = reg.cookies.get("c_user", "")

        if uid:
            profile_name = get_facebook_profile_info(uid)
            created_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            account_data = {
                "uid": uid,
                "password": password,
                "email": final_contact,
                "nama": profile_name,
                "gender": gender_text,
                "tgl_lahir": tgl_lahir,
                "timestamp": created_date,
                "cookie": cookie_str,
                "locale": locale_info["locale"] if locale_info else "id_ID",
                "language": locale_info["language"] if locale_info else "Indonesian",
            }
            save_account_to_file(account_data)
            status["live"] += 1

            table = Table(
                title="AKUN BERHASIL DIBUAT",
                show_header=True,
                title_style="bold green",
                border_style="green",
                padding=(0, 1),
            )
            table.add_column("Key", style="bold cyan", no_wrap=True, width=20)
            table.add_column("Value", style="bold white")
            table.add_row("UID|Pass", f"[bold green]{uid}|{password}")
            table.add_row("Nama Lengkap", profile_name)
            table.add_row("Email / Nomor", final_contact)
            table.add_row("Jenis Kelamin", gender_text)
            table.add_row("Tanggal Lahir", tgl_lahir)
            table.add_row("Tanggal Dibuat", created_date)
            if locale_info:
                table.add_row("Locale", f'[bold cyan]{locale_info["locale"]} ({locale_info["language"]})[/bold cyan]')
            if len(cookie_str) > 100:
                table.add_row("Cookie (1/2)", f"[bold purple]{cookie_str[:100]}...[/bold purple]")
                table.add_row("Cookie (2/2)", f"[bold purple]...{cookie_str[100:]}[/bold purple]")
            else:
                table.add_row("Cookie", cookie_str)
            console.print(table)
        elif "checkpoint" in reg.url or "cp" in reg.url:
            status["cp"] += 1
            console.print("[bold yellow]Akun terbuat namun memerlukan checkpoint/verifikasi.[/bold yellow]")
        else:
            console.print("[bold red]Registrasi gagal. Tidak mendapatkan cookie c_user.[/bold red]")

    except requests.ConnectionError as e:
        console.print(f"[bold red]Error koneksi saat registrasi: {e}[/bold red]")
    except requests.Timeout as e:
        console.print(f"[bold red]Timeout saat registrasi: {e}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error saat registrasi: {e}[/bold red]")

    input("\nTekan Enter untuk kembali ke menu...")


# ============================================================
# SETTINGS MENU
# ============================================================

def settings_menu():
    """Menu pengaturan lengkap"""
    while True:
        clear_screen()
        show_header_once()

        gs = settings["gender_setting"]
        if gs == "male":
            gender_display = "LAKI-LAKI \u2642"
        elif gs == "female":
            gender_display = "PEREMPUAN \u2640"
        else:
            gender_display = "RANDOM \U0001f3b2"

        menu_text = (
            f'[bold white]1.[/bold white] Password Akun      : [bold green]{settings["password"]}[/bold green]\n'
            f'[bold white]2.[/bold white] Limit Register      : [bold green]{settings["limit"]}[/bold green]\n'
            f'[bold white]3.[/bold white] Gender Setting      : [bold yellow]{gender_display}[/bold yellow]\n'
            f'[bold white]4.[/bold white] Random Locale       : [bold green]{"AKTIF" if settings["random_locale"] == "random" else "NONAKTIF"}[/bold green]\n'
            f'[bold white]5.[/bold white] Gunakan Temp Email  : [bold green]{"AKTIF" if settings["use_temp_email"] else "NONAKTIF"}[/bold green]\n'
            f'[bold white]6.[/bold white] Gunakan Real Email  : [bold green]{"AKTIF" if settings["use_real_email"] else "NONAKTIF"}[/bold green]\n'
            f'[bold white]7.[/bold white] Gunakan Contact File: [bold green]{"AKTIF (" + str(len(settings["contact_list"])) + " contact)" if settings["use_contact_file"] else "NONAKTIF"}[/bold green]\n'
            f'[bold white]8.[/bold white] Lihat Contact List\n'
            f'[bold white]9.[/bold white] Buat Contoh Contact File\n'
            f'[bold white]10.[/bold white] Lihat Info Contact File\n'
            f'[bold white]11.[/bold white] Lihat Semua Locale ({len(FACEBOOK_LOCALES)})\n'
            f'[bold white]12.[/bold white] Lihat Locale Saat Ini\n'
            f'[bold white]0.[/bold white] Kembali ke Menu Utama'
        )

        console.print(Panel(menu_text, title="\u2699 SETTINGS", border_style="yellow"))
        choice = Prompt.ask("[bold cyan]Pilih opsi[/bold cyan]", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"])

        if choice == "0":
            return
        elif choice == "1":
            new_pass = Prompt.ask("[bold cyan]Password baru[/bold cyan]", default=settings["password"]).strip()
            if new_pass:
                settings["password"] = new_pass
                console.print(f"[bold green]\u2713 Password diubah menjadi: {new_pass}[/bold green]")
        elif choice == "2":
            new_limit = IntPrompt.ask("[bold cyan]Jumlah limit akun[/bold cyan]", default=settings["limit"])
            settings["limit"] = new_limit
            console.print(f"[bold green]\u2713 Limit diubah menjadi: {new_limit}[/bold green]")
        elif choice == "3":
            console.print("\n[bold yellow]Pilih Gender Setting:[/bold yellow]")
            console.print("  1. Laki-laki (\u2642) - Semua akun akan laki-laki")
            console.print("  2. Perempuan (\u2640) - Semua akun akan perempuan")
            console.print("  3. Random (\U0001f3b2) - Gender akan dipilih acak tiap akun")
            gc = Prompt.ask("[bold cyan]Pilih (1/2/3)[/bold cyan]", choices=["1", "2", "3"])
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
            if settings["random_locale"] == "random":
                settings["random_locale"] = "off"
            else:
                settings["random_locale"] = "random"
            status_text = "AKTIF" if settings["random_locale"] == "random" else "NONAKTIF"
            console.print(f"[bold green]\u2713 Random Locale: {status_text}[/bold green]")
        elif choice == "5":
            if settings["use_temp_email"]:
                settings["use_temp_email"] = False
                console.print("[bold yellow]Temp Email dinonaktifkan.[/bold yellow]")
            else:
                settings["use_temp_email"] = True
                settings["use_real_email"] = False
                settings["use_contact_file"] = False
                console.print("[bold green]\u2713 Temp Email diaktifkan. Real Email & Contact File dinonaktifkan.[/bold green]")
        elif choice == "6":
            if settings["use_real_email"]:
                settings["use_real_email"] = False
                console.print("[bold yellow]Real Email dinonaktifkan.[/bold yellow]")
            else:
                settings["use_real_email"] = True
                settings["use_temp_email"] = False
                settings["use_contact_file"] = False
                console.print("[bold green]\u2713 Real Email diaktifkan. Temp Email & Contact File dinonaktifkan.[/bold green]")
        elif choice == "7":
            if settings["use_contact_file"]:
                settings["use_contact_file"] = False
                settings["contact_file"] = ""
                settings["contact_list"] = []
                console.print("[bold yellow]Contact File dinonaktifkan.[/bold yellow]")
            else:
                file_path = Prompt.ask(
                    "[bold cyan]Masukkan path file contact[/bold cyan]",
                    default=str(SAVE_DIR / "contacts.txt")
                ).strip()
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
            input("\nTekan Enter untuk kembali...")
        elif choice == "9":
            create_contact_file_example()
            input("\nTekan Enter untuk kembali...")
        elif choice == "10":
            show_contact_file_info()
            input("\nTekan Enter untuk kembali...")
        elif choice == "11":
            show_all_locales()
        elif choice == "12":
            show_locale_info()
            input("\nTekan Enter untuk kembali...")

        time.sleep(1)


# ============================================================
# HEADER
# ============================================================

_header_shown = False


def show_header_once():
    global _header_shown
    if not _header_shown:
        console.print(Panel(
            "[bold white on blue] FACEBOOK BOT ACCOUNT GENERATOR[/bold white on blue]\n"
            "[bold red on white] AUTHOR : SLLOWLY | VERSION : V4.5[/bold red on white]",
            border_style="bright_blue"
        ))
        _header_shown = True


# ============================================================
# MAIN MENU
# ============================================================

def main_menu():
    global _header_shown
    while True:
        try:
            clear_screen()
            _header_shown = False
            show_header_once()

            saved = count_saved_accounts()

            console.print(Panel(
                f'[bold white]1.[/bold white] \U0001f680Register Otomatis ([bold green]{settings["limit"]}[/bold green] akun)\n'
                f'[bold white]2.[/bold white] \u270d Register Manual (1 akun)\n'
                f'[bold white]3.[/bold white] \u2699 Settings\n'
                f'[bold white]4.[/bold white] \U0001f4caStatistik\n'
                f'[bold white]5.[/bold white] \U0001f50dCek UID Facebook\n'
                f'[bold white]6.[/bold white] \U0001f310Lihat URL Registrasi\n'
                f'[bold white]7.[/bold white] \U0001f4c2Buka Folder Penyimpanan\n'
                f'[bold white]0.[/bold white] \U0001f6aaKeluar',
                title="MENU UTAMA",
                border_style="green"
            ))

            choice = Prompt.ask("[bold cyan]Pilih menu[/bold cyan]")

            if choice == "0":
                console.print("[bold red]Keluar dari program...[/bold red]")
                sys.exit(0)
            elif choice == "1":
                console.print(f"\n[bold cyan]Memulai register otomatis {settings['limit']} akun...[/bold cyan]")
                for _ in range(settings["limit"]):
                    register_account()
                console.print(f'\n[bold green]Selesai! Total akun live: {status["live"]}[/bold green]')
                input("\nTekan Enter untuk kembali ke menu...")
            elif choice == "2":
                register_manual()
            elif choice == "3":
                settings_menu()
            elif choice == "4":
                console.print(Panel(
                    f'[bold white]Total Akun Live    :[/bold white] [bold green]{status["live"]}[/bold green]\n'
                    f'[bold white]Total Checkpoint   :[/bold white] [bold yellow]{status["cp"]}[/bold yellow]\n'
                    f'[bold white]Total Loop         :[/bold white] [bold cyan]{status["loop"]}[/bold cyan]\n'
                    f'[bold white]Akun Tersimpan     :[/bold white] [bold green]{saved}[/bold green]\n'
                    f'[bold white]Gender Setting     :[/bold white] [bold yellow]{settings["gender_setting"]}[/bold yellow]\n'
                    f'[bold white]Random Locale      :[/bold white] [bold green]{"AKTIF" if settings["random_locale"] == "random" else "NONAKTIF"}[/bold green]\n'
                    f'[bold white]Total Locale       :[/bold white] [bold cyan]{len(FACEBOOK_LOCALES)}[/bold cyan]\n'
                    f'[bold white]File Save          :[/bold white] [dim]{SAVE_FILE}[/dim]\n'
                    f'[bold white]File Log           :[/bold white] [dim]{LOG_FILE}[/dim]',
                    title="STATISTIK",
                    border_style="cyan"
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

        except KeyboardInterrupt:
            console.print("\n[bold red]Keluar dari program...[/bold red]")
            sys.exit(0)
        except Exception as e:
            console.print(f"[bold red]Error tidak terduga di menu utama: {e}[/bold red]")
            input("\nTekan Enter untuk kembali ke menu...")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    try:
        approval()
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[bold red]Program dihentikan oleh pengguna.[/bold red]")
        sys.exit(0)
