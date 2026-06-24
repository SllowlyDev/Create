"""
Facebook Account Creator Tools - Premium Edition
Author: Sllowly | Version: V4.5

Refactored from obfuscated single-file into modular structure with shared utilities.
"""

import os
import sys
import time
import random
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
    from rich.table import Table
    from rich.prompt import Prompt, IntPrompt
    from fake_useragent import UserAgent
except ImportError as e:
    print("[ERROR] Library belum terinstall: " + str(e))
    exit()

from utils.constants import (
    DEFAULT_SAVE_DIR_ANDROID,
    DEFAULT_SAVE_DIR_FALLBACK,
    LOG_FILENAME,
    SAVE_FILENAME,
)
from utils.http_helpers import (
    build_encpass,
    build_get_headers,
    build_post_headers,
    build_registration_params,
    build_registration_url,
    display_account_table,
    extract_cookies_string,
    extract_form_tokens,
)
from utils.validation import (
    create_contact_file_example,
    load_contact_file,
    normalize_phone_number,
    remove_contact_from_file,
    show_contact_file_info,
    show_contact_list,
    validate_email,
    validate_phone,
)
from utils.facebook import check, fetch_facebook_profile_name

console = Console()

# =========================================================================
# Locale data
# =========================================================================

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
    {"locale": "es_EC", "language": "Spanish (Ecuador)", "accept_lang": "es-EC,es;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Ecuador"},
    {"locale": "es_UY", "language": "Spanish (Uruguay)", "accept_lang": "es-UY,es;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Uruguay"},
    {"locale": "it_IT", "language": "Italian", "accept_lang": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Italy"},
    {"locale": "pt_PT", "language": "Portuguese", "accept_lang": "pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Portugal"},
    {"locale": "pt_BR", "language": "Portuguese (Brazil)", "accept_lang": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Brazil"},
    {"locale": "nl_NL", "language": "Dutch", "accept_lang": "nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Netherlands"},
    {"locale": "nl_BE", "language": "Dutch (Belgium)", "accept_lang": "nl-BE,nl;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Belgium"},
    {"locale": "sv_SE", "language": "Swedish", "accept_lang": "sv-SE,sv;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Sweden"},
    {"locale": "da_DK", "language": "Danish", "accept_lang": "da-DK,da;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Denmark"},
    {"locale": "no_NO", "language": "Norwegian", "accept_lang": "no-NO,no;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Norway"},
    {"locale": "nb_NO", "language": "Norwegian (Bokm\u00e5l)", "accept_lang": "nb-NO,nb;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Norway"},
    {"locale": "fi_FI", "language": "Finnish", "accept_lang": "fi-FI,fi;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Finland"},
    {"locale": "pl_PL", "language": "Polish", "accept_lang": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Poland"},
    {"locale": "cs_CZ", "language": "Czech", "accept_lang": "cs-CZ,cs;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Czech Republic"},
    {"locale": "hu_HU", "language": "Hungarian", "accept_lang": "hu-HU,hu;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Hungary"},
    {"locale": "ro_RO", "language": "Romanian", "accept_lang": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Romania"},
    {"locale": "tr_TR", "language": "Turkish", "accept_lang": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Turkey"},
    {"locale": "el_GR", "language": "Greek", "accept_lang": "el-GR,el;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Greece"},
    {"locale": "ru_RU", "language": "Russian", "accept_lang": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Russia"},
    {"locale": "uk_UA", "language": "Ukrainian", "accept_lang": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Ukraine"},
    {"locale": "bg_BG", "language": "Bulgarian", "accept_lang": "bg-BG,bg;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Bulgaria"},
    {"locale": "hr_HR", "language": "Croatian", "accept_lang": "hr-HR,hr;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Croatia"},
    {"locale": "sk_SK", "language": "Slovak", "accept_lang": "sk-SK,sk;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Slovakia"},
    {"locale": "sl_SI", "language": "Slovenian", "accept_lang": "sl-SI,sl;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Slovenia"},
    {"locale": "et_EE", "language": "Estonian", "accept_lang": "et-EE,et;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Estonia"},
    {"locale": "lv_LV", "language": "Latvian", "accept_lang": "lv-LV,lv;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Latvia"},
    {"locale": "lt_LT", "language": "Lithuanian", "accept_lang": "lt-LT,lt;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Lithuania"},
    {"locale": "sr_RS", "language": "Serbian", "accept_lang": "sr-RS,sr;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Serbia"},
    {"locale": "sq_AL", "language": "Albanian", "accept_lang": "sq-AL,sq;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Albania"},
    {"locale": "mk_MK", "language": "Macedonian", "accept_lang": "mk-MK,mk;q=0.9,en-US;q=0.8,en;q=0.7", "country": "North Macedonia"},
    {"locale": "bs_BA", "language": "Bosnian", "accept_lang": "bs-BA,bs;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Bosnia and Herzegovina"},
    {"locale": "mt_MT", "language": "Maltese", "accept_lang": "mt-MT,mt;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Malta"},
    {"locale": "is_IS", "language": "Icelandic", "accept_lang": "is-IS,is;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Iceland"},
    {"locale": "ga_IE", "language": "Irish", "accept_lang": "ga-IE,ga;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Ireland"},
    {"locale": "cy_GB", "language": "Welsh", "accept_lang": "cy-GB,cy;q=0.9,en-US;q=0.8,en;q=0.7", "country": "United Kingdom"},
    {"locale": "gd_GB", "language": "Scottish Gaelic", "accept_lang": "gd-GB,gd;q=0.9,en-US;q=0.8,en;q=0.7", "country": "United Kingdom"},
    {"locale": "lb_LU", "language": "Luxembourgish", "accept_lang": "lb-LU,lb;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Luxembourg"},
    {"locale": "zh_CN", "language": "Chinese (Simplified)", "accept_lang": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7", "country": "China"},
    {"locale": "zh_TW", "language": "Chinese (Traditional)", "accept_lang": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Taiwan"},
    {"locale": "zh_HK", "language": "Chinese (Hong Kong)", "accept_lang": "zh-HK,zh;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Hong Kong"},
    {"locale": "ja_JP", "language": "Japanese", "accept_lang": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Japan"},
    {"locale": "ko_KR", "language": "Korean", "accept_lang": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7", "country": "South Korea"},
    {"locale": "th_TH", "language": "Thai", "accept_lang": "th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Thailand"},
    {"locale": "vi_VN", "language": "Vietnamese", "accept_lang": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Vietnam"},
    {"locale": "hi_IN", "language": "Hindi", "accept_lang": "hi-IN,hi;q=0.9,en-US;q=0.8,en;q=0.7", "country": "India"},
    {"locale": "bn_IN", "language": "Bengali", "accept_lang": "bn-IN,bn;q=0.9,en-US;q=0.8,en;q=0.7", "country": "India"},
    {"locale": "ta_IN", "language": "Tamil", "accept_lang": "ta-IN,ta;q=0.9,en-US;q=0.8,en;q=0.7", "country": "India"},
    {"locale": "te_IN", "language": "Telugu", "accept_lang": "te-IN,te;q=0.9,en-US;q=0.8,en;q=0.7", "country": "India"},
    {"locale": "mr_IN", "language": "Marathi", "accept_lang": "mr-IN,mr;q=0.9,en-US;q=0.8,en;q=0.7", "country": "India"},
    {"locale": "gu_IN", "language": "Gujarati", "accept_lang": "gu-IN,gu;q=0.9,en-US;q=0.8,en;q=0.7", "country": "India"},
    {"locale": "kn_IN", "language": "Kannada", "accept_lang": "kn-IN,kn;q=0.9,en-US;q=0.8,en;q=0.7", "country": "India"},
    {"locale": "ml_IN", "language": "Malayalam", "accept_lang": "ml-IN,ml;q=0.9,en-US;q=0.8,en;q=0.7", "country": "India"},
    {"locale": "pa_IN", "language": "Punjabi", "accept_lang": "pa-IN,pa;q=0.9,en-US;q=0.8,en;q=0.7", "country": "India"},
    {"locale": "or_IN", "language": "Odia", "accept_lang": "or-IN,or;q=0.9,en-US;q=0.8,en;q=0.7", "country": "India"},
    {"locale": "as_IN", "language": "Assamese", "accept_lang": "as-IN,as;q=0.9,en-US;q=0.8,en;q=0.7", "country": "India"},
    {"locale": "ur_PK", "language": "Urdu", "accept_lang": "ur-PK,ur;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Pakistan"},
    {"locale": "si_LK", "language": "Sinhala", "accept_lang": "si-LK,si;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Sri Lanka"},
    {"locale": "my_MM", "language": "Burmese", "accept_lang": "my-MM,my;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Myanmar"},
    {"locale": "km_KH", "language": "Khmer", "accept_lang": "km-KH,km;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Cambodia"},
    {"locale": "lo_LA", "language": "Lao", "accept_lang": "lo-LA,lo;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Laos"},
    {"locale": "tl_PH", "language": "Filipino", "accept_lang": "tl-PH,tl;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Philippines"},
    {"locale": "ka_GE", "language": "Georgian", "accept_lang": "ka-GE,ka;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Georgia"},
    {"locale": "hy_AM", "language": "Armenian", "accept_lang": "hy-AM,hy;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Armenia"},
    {"locale": "ne_NP", "language": "Nepali", "accept_lang": "ne-NP,ne;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Nepal"},
    {"locale": "mn_MN", "language": "Mongolian", "accept_lang": "mn-MN,mn;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Mongolia"},
    {"locale": "ku_TR", "language": "Kurdish", "accept_lang": "ku-TR,ku;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Turkey"},
    {"locale": "ar_AR", "language": "Arabic", "accept_lang": "ar-AR,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Saudi Arabia"},
    {"locale": "ar_SA", "language": "Arabic (Saudi)", "accept_lang": "ar-SA,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Saudi Arabia"},
    {"locale": "ar_EG", "language": "Arabic (Egypt)", "accept_lang": "ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Egypt"},
    {"locale": "ar_AE", "language": "Arabic (UAE)", "accept_lang": "ar-AE,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "UAE"},
    {"locale": "ar_MA", "language": "Arabic (Morocco)", "accept_lang": "ar-MA,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Morocco"},
    {"locale": "ar_DZ", "language": "Arabic (Algeria)", "accept_lang": "ar-DZ,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Algeria"},
    {"locale": "ar_TN", "language": "Arabic (Tunisia)", "accept_lang": "ar-TN,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Tunisia"},
    {"locale": "ar_IQ", "language": "Arabic (Iraq)", "accept_lang": "ar-IQ,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Iraq"},
    {"locale": "ar_JO", "language": "Arabic (Jordan)", "accept_lang": "ar-JO,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Jordan"},
    {"locale": "ar_LB", "language": "Arabic (Lebanon)", "accept_lang": "ar-LB,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Lebanon"},
    {"locale": "ar_SY", "language": "Arabic (Syria)", "accept_lang": "ar-SY,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Syria"},
    {"locale": "ar_YE", "language": "Arabic (Yemen)", "accept_lang": "ar-YE,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Yemen"},
    {"locale": "ar_QA", "language": "Arabic (Qatar)", "accept_lang": "ar-QA,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Qatar"},
    {"locale": "ar_KW", "language": "Arabic (Kuwait)", "accept_lang": "ar-KW,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Kuwait"},
    {"locale": "ar_BH", "language": "Arabic (Bahrain)", "accept_lang": "ar-BH,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Bahrain"},
    {"locale": "ar_OM", "language": "Arabic (Oman)", "accept_lang": "ar-OM,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Oman"},
    {"locale": "ar_SD", "language": "Arabic (Sudan)", "accept_lang": "ar-SD,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Sudan"},
    {"locale": "ar_LY", "language": "Arabic (Libya)", "accept_lang": "ar-LY,ar;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Libya"},
    {"locale": "he_IL", "language": "Hebrew", "accept_lang": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Israel"},
    {"locale": "fa_IR", "language": "Persian", "accept_lang": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Iran"},
    {"locale": "ps_AF", "language": "Pashto", "accept_lang": "ps-AF,ps;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Afghanistan"},
    {"locale": "sw_KE", "language": "Swahili", "accept_lang": "sw-KE,sw;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Kenya"},
    {"locale": "sw_TZ", "language": "Swahili (Tanzania)", "accept_lang": "sw-TZ,sw;q=0.9,en-US;q=0.8,en;q=0.7", "country": "Tanzania"},
    {"locale": "af_ZA", "language": "Afrikaans", "accept_lang": "af-ZA,af;q=0.9,en-US;q=0.8,en;q=0.7", "country": "South Africa"},
    {"locale": "zu_ZA", "language": "Zulu", "accept_lang": "zu-ZA,zu;q=0.9,en-US;q=0.8,en;q=0.7", "country": "South Africa"},
    {"locale": "xh_ZA", "language": "Xhosa", "accept_lang": "xh-ZA,xh;q=0.9,en-US;q=0.8,en;q=0.7", "country": "South Africa"},
    {"locale": "st_ZA", "language": "Southern Sotho", "accept_lang": "st-ZA,st;q=0.9,en-US;q=0.8,en;q=0.7", "country": "South Africa"},
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

# =========================================================================
# Locale helpers
# =========================================================================

def get_random_fb_locale():
    global current_locale
    current_locale = random.choice(FACEBOOK_LOCALES)
    return current_locale["accept_lang"]


def get_current_locale_info():
    return current_locale


def show_locale_info():
    locale_info = get_current_locale_info()
    if locale_info:
        text = (
            f"[bold cyan]Locale:[/bold cyan] {locale_info['locale']}"
            f"\n[bold cyan]Language:[/bold cyan] {locale_info['language']}"
            f"\n[bold cyan]Country:[/bold cyan] {locale_info['country']}"
            f"\n[bold cyan]Accept-Language:[/bold cyan] {locale_info['accept_lang']}"
        )
        console.print(Panel(text, title="CURRENT LOCALE"))
    else:
        console.print("[yellow]Belum ada locale yang dipilih[/yellow]")


def show_all_locales():
    console.print(Panel(
        f"[bold cyan]Total: {len(FACEBOOK_LOCALES)} Locale Tersedia[/bold cyan]",
        title="DAFTAR FULL LOCALE",
        style="bold magenta",
    ))
    table = Table(show_lines=True)
    table.add_column("No", style="dim", width=5)
    table.add_column("Locale Code", style="bold cyan", width=12)
    table.add_column("Language", style="bold white", width=30)
    table.add_column("Country", style="bold green", width=25)
    for i, loc in enumerate(FACEBOOK_LOCALES, 1):
        table.add_row(str(i), loc["locale"], loc["language"], loc["country"])
    console.print(table)
    input("\nTekan Enter untuk kembali...")


# =========================================================================
# Country codes and faker setup
# =========================================================================

country_codes = [
    "+62", "+60", "+1", "+44", "+61", "+91", "+81", "+82",
    "+66", "+84", "+55", "+49", "+33", "+34", "+39", "+351",
    "+7", "+86", "+90", "+20", "+27", "+234", "+254",
]
selected_country_code = random.choice(country_codes)

try:
    ua = UserAgent()
except Exception:
    ua = None

faker = Faker()

# =========================================================================
# Status and settings
# =========================================================================

status = {"live": 0, "cp": 0, "loop": 0}

settings = {
    "password": "FOUNDER",
    "limit": 30,
    "gender_setting": "random",
    "random_locale": True,
    "use_temp_email": True,
    "use_real_email": False,
    "use_contact_file": False,
    "contact_file": "",
    "contact_list": [],
}

# =========================================================================
# File paths
# =========================================================================

try:
    SAVE_DIR = Path(DEFAULT_SAVE_DIR_ANDROID)
    SAVE_DIR.mkdir(exist_ok=True)
    console.print(f"[bold green]Folder penyimpanan: {SAVE_DIR}[/bold green]")
except Exception:
    SAVE_DIR = Path.cwd() / DEFAULT_SAVE_DIR_FALLBACK
    SAVE_DIR.mkdir(exist_ok=True)
    console.print(f"[bold yellow]Menggunakan folder alternatif: {SAVE_DIR}[/bold yellow]")

SAVE_FILE = SAVE_DIR / SAVE_FILENAME
LOG_FILE = SAVE_DIR / LOG_FILENAME


# =========================================================================
# Screen and network helpers
# =========================================================================

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def get_public_ip():
    try:
        return requests.get("https://api.ipify.org", timeout=5).text
    except Exception:
        return "Tidak dapat mengambil IP"


# =========================================================================
# User agent generator
# =========================================================================

def ugen():
    """Generate a random Android mobile user agent string."""
    android_devices = [
        "SM-G960F", "SM-G965F", "SM-N960F", "SM-A505F", "SM-A515F",
        "SM-A725F", "SM-S908B", "SM-S901B", "SM-A536B", "SM-A346B",
        "Pixel 6", "Pixel 7", "Pixel 8", "Pixel 6a", "Pixel 7a",
        "POCO X3", "POCO F3", "Redmi Note 10", "Redmi Note 11", "Redmi Note 12",
        "M2101K6G", "M2102J20SG", "22041219G", "23053RN02A",
        "RMX3085", "RMX3363", "CPH2211", "CPH2269",
        "V2111", "V2145", "V2203",
        "IN2023", "LE2115", "NE2215",
    ]
    android_map = {
        9: "PKQ1", 10: "QKQ1", 11: "RKQ1", 12: "SKQ1", 13: "TKQ1", 14: "UKQ1",
    }
    android_version = random.randint(9, 14)
    build_prefix = android_map.get(android_version, "UKQ1")
    build_date = f"{random.randint(200000, 249999):03d}"
    build_number = f".{random.randint(0, 999):03d}"
    build_full = f"{build_prefix}.{build_date}{build_number}"
    chrome_major = random.randint(95, 129)
    chrome_build = f"{random.randint(4600, 6999)}.{random.randint(30, 200)}"
    device = random.choice(android_devices)
    return (
        f"Mozilla/5.0 (Linux; Android {android_version}; {device} Build/{build_full}"
        f"; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/"
        f"{chrome_major}.0.{chrome_build} Mobile Safari/537.36"
    )


# =========================================================================
# HTML form extraction
# =========================================================================

def extract_form(html):
    """Extract all hidden form input values from HTML."""
    soup = bs(html, "html.parser")
    form_data = {}
    for tag in soup.find_all("input"):
        name = tag.get("name")
        value = tag.get("value", "")
        if name:
            form_data[name] = value
    return form_data


def extract_important_tokens(html):
    """Extract important Facebook tokens from HTML using regex patterns."""
    tokens = {}
    token_configs = {
        "fb_dtsg": [r'"fb_dtsg"\s*:\s*\{"token"\s*:\s*"([^"]+)"', r'name="fb_dtsg"\s+value="([^"]+)"'],
        "jazoest": [r'name="jazoest"\s+value="([^"]+)"', r'"jazoest"\s*:\s*"([^"]+)"'],
        "lsd": [r'name="lsd"\s+value="([^"]+)"', r'"lsd"\s*:\s*"([^"]+)"'],
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
    """Extract both form data and important tokens from registration page HTML."""
    result = {}
    form_data = extract_form(html)
    result.update(form_data)
    tokens = extract_important_tokens(html)
    result.update(tokens)
    return result


# =========================================================================
# Email/contact generation
# =========================================================================

def get_email():
    """
    Get an email or phone number for registration based on current settings.
    Returns the contact value from contact file, temp email, or real email mode.
    """
    if settings.get("use_contact_file") and settings.get("contact_list"):
        contact = settings["contact_list"][status["loop"] % len(settings["contact_list"])]
        return contact["value"]

    if settings.get("use_temp_email"):
        temp_domains = [
            "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
            "protonmail.com", "mail.com", "aol.com", "zoho.com",
        ]
        username = faker.first_name().lower() + "." + faker.last_name().lower()
        username += str(random.randint(10, 9999))
        return username + "@" + random.choice(temp_domains)

    if settings.get("use_real_email"):
        domains = ["gmail.com", "yahoo.com", "outlook.com"]
        username = faker.first_name().lower() + faker.last_name().lower()
        username += str(random.randint(10000000, 99999999))
        return username + "@" + random.choice(domains)

    return str(random.randint(10000000, 99999999)) + "@gmail.com"


# =========================================================================
# Account file I/O
# =========================================================================

def save_account_to_file(account_data):
    """Save created account details to both save file and log file."""
    try:
        line = account_data["uid"] + "|" + account_data["password"] + "\n"
        with open(SAVE_FILE, "a", encoding="utf-8") as f:
            f.write(line)

        log_content = "\n".join([
            "=" * 50,
            "UID: " + account_data["uid"],
            "Password: " + account_data["password"],
            "Email/No: " + account_data["email"],
            "Nama Lengkap: " + account_data["nama"],
            "Jenis Kelamin: " + account_data["gender"],
            "Tanggal Lahir: " + account_data["tgl_lahir"],
            "Tanggal Dibuat: " + account_data["timestamp"],
            "Cookie: " + account_data["cookie"],
            "",
        ])
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_content)
    except Exception as e:
        console.print(f"[bold red]Gagal menyimpan akun: {e}[/bold red]")


def count_saved_accounts():
    """Count the number of saved accounts in the save file."""
    try:
        if not SAVE_FILE.exists():
            return 0
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return sum(1 for line in lines if line.strip() and "|" in line.strip())
    except Exception:
        return 0


# =========================================================================
# License validation
# =========================================================================

def approval():
    """Validate the user's license key."""
    clear_screen()
    console.print(Panel("[bold cyan]Validasi Lisensi...[/bold cyan]", title="LICENSE"))
    time.sleep(0.5)

    uid_val = getattr(os, "getuid", lambda: random.randint(1000, 9999))()
    # user_login and device_id used for device fingerprinting in license generation
    _ = getpass.getuser()
    _ = socket.gethostname()
    random.seed(uid_val)

    def rnum():
        return str(random.randint(0, 9))

    def rlet():
        return random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    license_parts = []
    for _ in range(4):
        part = ""
        for _ in range(4):
            part += random.choice([rnum, rlet])()
        license_parts.append(part)

    full_license = "FOUNDER-" + "-".join(license_parts)

    console.print(Panel(
        f"[white]License:[/white]\n[green]{full_license}[/green]",
        title="INFO",
    ))

    license_url = "https://raw.githubusercontent.com/SllowlyDev/license-key-validation/main/licenses.json"
    try:
        res = requests.get(license_url, timeout=10)
        if res.status_code == 200:
            valid_keys = [x.strip() for x in res.text.splitlines() if x.strip()]
            if full_license in valid_keys:
                console.print("[bold green]License Valid![/bold green]")
                console.print(Panel(full_license, title="SUCCESS"))
            else:
                console.print(
                    f"[yellow]License not registered.[/yellow]\n\n[green]{full_license}[/green]"
                )
                console.print(Panel(full_license, title="ACTIVATION"))
    except Exception:
        pass

    return license_parts


# =========================================================================
# Registration URL display
# =========================================================================

def show_registration_url():
    """Display the Facebook registration URL (uses shared URL builder)."""
    reg_url, domain = build_registration_url()
    console.print(Panel(
        f"[bold cyan]URL Registrasi Facebook:[/bold cyan]\n"
        f"[bold green]{reg_url}[/bold green]\n\n"
        f"[dim]Domain yang digunakan: {domain}[/dim]",
        title="REGISTRATION URL",
    ))


# =========================================================================
# Gender resolver
# =========================================================================

def resolve_gender():
    """Resolve gender based on settings. Returns (code, text)."""
    gs = settings.get("gender_setting", "random")
    if gs == "random":
        gender_code, gender_text = random.choice([("1", "Perempuan"), ("2", "Laki-laki")])
    elif gs == "female":
        gender_code, gender_text = "1", "Perempuan"
    else:
        gender_code, gender_text = "2", "Laki-laki"
    return gender_code, gender_text


# =========================================================================
# Registration (automatic) — uses shared helpers from utils.http_helpers
# =========================================================================

def register_account():
    """
    Automatic registration loop. Uses shared utilities for URL building,
    headers, form tokens, params, and result display.
    """
    email = get_email()
    contact_info = None
    if settings.get("use_contact_file") and settings.get("contact_list"):
        contact_info = settings["contact_list"][status["loop"] % len(settings["contact_list"])]

    for i in range(35):
        sys.stdout.write(
            f"\r[grey50]( [bold cyan]{i + 1}[/bold cyan] Akun : "
            f"[grey50]) : ([bold green]Success:[bold green]{status['live']} [grey50])"
        )
        sys.stdout.flush()

    try:
        reg_url, domain = build_registration_url()
        ses = requests.Session()

        accept_lang = get_random_fb_locale()
        locale_info = get_current_locale_info()

        console.print(Panel(
            f"[bold cyan]Menggunakan Locale:[/bold cyan] {locale_info['locale']}"
            f"\n[bold cyan]Language:[/bold cyan] {locale_info['language']}"
            f"\n[bold cyan]Country:[/bold cyan] {locale_info['country']}"
            f"\n[bold cyan]Gender Setting:[/bold cyan] {settings.get('gender_setting', 'random')}",
            title="RANDOM LOCALE & GENDER",
        ))

        user_agent = ugen()
        headers_get = build_get_headers(user_agent, accept_lang)
        res = ses.get(reg_url, headers=headers_get, timeout=30)
        extracted_data = extract_all_from_html(res.text)
        tokens = extract_form_tokens(extracted_data)

        fname = faker.first_name().lower()
        lname = faker.last_name().lower()
        fullname = fname + " " + lname
        password = settings.get("password", "FOUNDER")

        birth_day = random.randint(1, 28)
        birth_month = random.randint(1, 12)
        birth_year = random.randint(1980, 2000)
        gender_code, gender_text = resolve_gender()
        tgl_lahir = f"{birth_day:02d}-{birth_month:02d}-{birth_year}"

        encpass = build_encpass(password)

        params = build_registration_params(
            tokens, fullname, password, birth_day, birth_month,
            birth_year, gender_code, email, encpass,
        )
        data = {**params, **extracted_data}

        device_name = user_agent.split(";")[1].strip() if ";" in user_agent else "Android"
        headers_post = build_post_headers(user_agent, accept_lang, device_name)

        cookie_str = extract_cookies_string(ses)
        if cookie_str:
            headers_post["cookie"] = cookie_str

        reg = ses.post(
            "https://m.facebook.com/reg/submit/",
            data=data, headers=headers_post, timeout=36,
        )

        uid = ses.cookies.get_dict().get("c_user", "")
        if uid:
            profile_name = fetch_facebook_profile_name(uid)
            created_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            account_data = {
                "uid": uid,
                "password": password,
                "email": email,
                "nama": profile_name,
                "gender": gender_text,
                "tgl_lahir": tgl_lahir,
                "timestamp": created_date,
                "cookie": extract_cookies_string(ses),
                "locale": locale_info.get("locale", ""),
                "language": locale_info.get("language", ""),
            }
            save_account_to_file(account_data)
            status["live"] += 1

            if contact_info and settings.get("use_contact_file"):
                remove_contact_from_file(
                    settings["contact_file"],
                    contact_info.get("original", ""),
                )
                if contact_info in settings["contact_list"]:
                    settings["contact_list"].remove(contact_info)
                console.print(
                    f"[bold yellow]\u2713 Contact [{contact_info.get('original', '')}] "
                    f"berhasil dihapus dari file.[/bold yellow]"
                )

            display_account_table(account_data)
        else:
            cookie_str = extract_cookies_string(ses)
            if "checkpoint" in (reg.url or "") or "checkpoint" in cookie_str:
                status["cp"] += 1
                console.print(
                    "[bold yellow]Akun terbuat namun memerlukan checkpoint/verifikasi.[/bold yellow]"
                )
            else:
                console.print(
                    "[bold red]Registrasi gagal. Tidak mendapatkan cookie c_user.[/bold red]"
                )

    except Exception as e:
        console.print(f"[bold red]Error saat registrasi: {e}[/bold red]")


# =========================================================================
# Registration (manual) — uses shared helpers from utils.http_helpers
# =========================================================================

def register_manual():
    """Manual single-account registration with user input."""
    clear_screen()
    show_header_once()
    console.print(Panel(
        "[bold cyan]Registrasi Manual Akun Facebook[/bold cyan]\n\n"
        "Isi data di bawah ini secara manual.\n"
        "Data akan dikirim ke Facebook untuk membuat 1 akun baru.\n"
        "[bold yellow]Tekan Enter kosong untuk menggunakan nilai default.[/bold yellow]",
        title="REGISTER MANUAL",
        style="cyan",
    ))

    default_fname = faker.first_name().lower()
    first_name = Prompt.ask("[bold cyan]Nama Depan[/bold cyan]", default=default_fname).strip()
    default_lname = faker.last_name().lower()
    last_name = Prompt.ask("[bold cyan]Nama Belakang[/bold cyan]", default=default_lname).strip()
    fullname = first_name + " " + last_name

    console.print("\n[bold yellow]Format yang didukung:[/bold yellow]")
    console.print("  - Email: contoh@gmail.com")
    console.print("  - Nomor: +6281234567890 atau 081234567890")

    default_contact = "+628" + str(random.randint(1000000000, 9999999999))
    while True:
        contact_raw = Prompt.ask(
            "[bold cyan]Email / Nomor Telepon[/bold cyan]",
            default=default_contact,
        ).strip()
        if validate_email(contact_raw):
            final_contact = contact_raw
            break
        elif validate_phone(contact_raw):
            final_contact = normalize_phone_number(contact_raw)
            break
        else:
            console.print(
                "[bold red]\u2717 Format tidak valid! Masukkan email yang benar "
                "atau nomor telepon (min 8 digit).[/bold red]"
            )

    default_pw = settings.get("password", "FOUNDER")
    password = Prompt.ask("[bold cyan]Password[/bold cyan]", default=default_pw).strip()

    console.print("\n[bold yellow]Tanggal Lahir:[/bold yellow]")
    default_day = f"{random.randint(1, 28):02d}"
    default_month = f"{random.randint(1, 12):02d}"
    default_year = str(random.randint(1985, 2000))

    birth_day = Prompt.ask("[bold cyan]  Hari (01-31)[/bold cyan]", default=default_day).strip()
    birth_month = Prompt.ask("[bold cyan]  Bulan (01-12)[/bold cyan]", default=default_month).strip()
    birth_year = Prompt.ask("[bold cyan]  Tahun (contoh: 1998)[/bold cyan]", default=default_year).strip()

    try:
        day_int = int(birth_day)
        month_int = int(birth_month)
        year_int = int(birth_year)
    except ValueError:
        day_int = random.randint(1, 28)
        month_int = random.randint(1, 12)
        year_int = random.randint(1985, 2000)

    tgl_lahir = f"{day_int:02d}-{month_int:02d}-{year_int}"

    console.print("\n[bold yellow]Jenis Kelamin:[/bold yellow]")
    console.print("  1. Perempuan")
    console.print("  2. Laki-laki")
    console.print("  3. Random (Acak)")
    gender_choice = Prompt.ask("[bold cyan]Pilih (1/2/3)[/bold cyan]", default="3").strip()

    if gender_choice == "3":
        gender_code, gender_text = random.choice([("1", "Perempuan"), ("2", "Laki-laki")])
        console.print(f"  [dim]\u2192 Dipilih random: {gender_text}[/dim]")
    elif gender_choice == "1":
        gender_code, gender_text = "1", "Perempuan"
    else:
        gender_code, gender_text = "2", "Laki-laki"

    console.print(Panel(
        f"[bold white]Nama Lengkap  :[/bold white] [bold green]{fullname}"
        f"[/bold green]\n[bold white]Email / No    :[/bold white] [bold green]{final_contact}"
        f"[/bold green]\n[bold white]Password      :[/bold white] [bold green]{password}"
        f"[/bold green]\n[bold white]Tanggal Lahir :[/bold white] [bold green]{tgl_lahir}"
        f"[/bold green]\n[bold white]Jenis Kelamin :[/bold white] [bold green]{gender_text}"
        f"[/bold green]",
        title="KONFIRMASI DATA",
        style="green",
    ))

    confirm = input("[bold yellow]Lanjutkan registrasi? (y/n)[/bold yellow] ").strip()
    if confirm.lower() != "y":
        console.print("[bold red]Registrasi dibatalkan.[/bold red]")
        input("\nTekan Enter untuk kembali ke menu...")
        return

    console.print("\n[bold cyan]Memulai proses registrasi manual...[/bold cyan]")
    status["loop"] += 1

    try:
        reg_url, domain = build_registration_url()
        # Manual registration appends &soft=hjk
        reg_url += "&soft=hjk"

        ses = requests.Session()
        accept_lang = get_random_fb_locale()
        locale_info = get_current_locale_info()

        user_agent = ugen()
        headers_get = build_get_headers(user_agent, accept_lang)
        res = ses.get(reg_url, headers=headers_get, timeout=30)
        extracted_data = extract_all_from_html(res.text)
        tokens = extract_form_tokens(extracted_data)

        encpass = build_encpass(password)

        params = build_registration_params(
            tokens, fullname, password, day_int, month_int,
            year_int, gender_code, final_contact, encpass,
        )
        data = {**params, **extracted_data}

        device_name = user_agent.split(";")[1].strip() if ";" in user_agent else "Android"
        headers_post = build_post_headers(user_agent, accept_lang, device_name)

        cookie_str = extract_cookies_string(ses)
        if cookie_str:
            headers_post["cookie"] = cookie_str

        console.print("[dim]Mengirim data ke Facebook...[/dim]")
        reg = ses.post(
            "https://m.facebook.com/reg/submit/",
            data=data, headers=headers_post, timeout=36,
        )

        uid = ses.cookies.get_dict().get("c_user", "")
        if uid:
            profile_name = fetch_facebook_profile_name(uid)
            created_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            status["live"] += 1

            account_data = {
                "uid": uid,
                "password": password,
                "email": final_contact,
                "nama": profile_name,
                "gender": gender_text,
                "tgl_lahir": tgl_lahir,
                "timestamp": created_date,
                "cookie": extract_cookies_string(ses),
                "locale": locale_info.get("locale", ""),
                "language": locale_info.get("language", ""),
            }
            save_account_to_file(account_data)
            display_account_table(account_data)
        else:
            cookie_str = extract_cookies_string(ses)
            if "checkpoint" in (reg.url or ""):
                status["cp"] += 1
                console.print(
                    "[bold yellow]Akun terbuat namun memerlukan checkpoint/verifikasi.[/bold yellow]"
                )
            else:
                console.print(
                    "[bold red]Registrasi gagal. Tidak mendapatkan cookie c_user.[/bold red]"
                )

    except Exception as e:
        console.print(f"[bold red]Error saat registrasi: {e}[/bold red]")


# =========================================================================
# Settings menu
# =========================================================================

def settings_menu():
    """Settings menu for configuring registration parameters."""
    while True:
        clear_screen()
        show_header_once()

        gender_display = {
            "male": "LAKI-LAKI \u2642",
            "female": "PEREMPUAN \u2640",
        }.get(settings["gender_setting"], "RANDOM \U0001f3b2")

        menu_text = (
            f"[bold white]1.[/bold white] Password Akun      : [bold green]{settings['password']}[/bold green]\n"
            f"[bold white]2.[/bold white] Limit Register      : [bold green]{settings['limit']}[/bold green]\n"
            f"[bold white]3.[/bold white] Gender Setting      : [bold yellow]{gender_display}[/bold yellow]\n"
            f"[bold white]4.[/bold white] Random Locale       : [bold green]{'AKTIF' if settings['random_locale'] else 'NONAKTIF'}[/bold green]\n"
            f"[bold white]5.[/bold white] Gunakan Temp Email  : [bold green]{'AKTIF' if settings['use_temp_email'] else 'NONAKTIF'}[/bold green]\n"
            f"[bold white]6.[/bold white] Gunakan Real Email  : [bold green]{'AKTIF' if settings['use_real_email'] else 'NONAKTIF'}[/bold green]\n"
            f"[bold white]7.[/bold white] Gunakan Contact File: [bold green]"
            f"{'AKTIF (' + str(len(settings.get('contact_list', []))) + ' contact)' if settings['use_contact_file'] else 'NONAKTIF'}[/bold green]\n"
            f"[bold white]8.[/bold white] Lihat Contact List\n"
            f"[bold white]9.[/bold white] Buat Contoh Contact File\n"
            f"[bold white]10.[/bold white] Lihat Info Contact File\n"
            f"[bold white]11.[/bold white] Lihat Semua Locale ({len(FACEBOOK_LOCALES)})\n"
            f"[bold white]12.[/bold white] Lihat Locale Saat Ini\n"
            f"[bold white]0.[/bold white] Kembali ke Menu Utama"
        )
        console.print(Panel(menu_text, title="\u2699 SETTINGS", style="yellow"))

        choice = Prompt.ask("[bold cyan]Pilih opsi[/bold cyan]").strip()

        if choice == "0":
            break
        elif choice == "1":
            new_pass = Prompt.ask("[bold cyan]Password baru[/bold cyan]").strip()
            if new_pass:
                settings["password"] = new_pass
                console.print(f"[bold green]\u2713 Password diubah menjadi: {new_pass}[/bold green]")
        elif choice == "2":
            new_limit = IntPrompt.ask("[bold cyan]Jumlah limit akun[/bold cyan]")
            settings["limit"] = new_limit
            console.print(f"[bold green]\u2713 Limit diubah menjadi: {new_limit}[/bold green]")
        elif choice == "3":
            console.print("\n[bold yellow]Pilih Gender Setting:[/bold yellow]")
            console.print("  1. Laki-laki (\u2642) - Semua akun akan laki-laki")
            console.print("  2. Perempuan (\u2640) - Semua akun akan perempuan")
            console.print("  3. Random (\U0001f3b2) - Gender akan dipilih acak tiap akun")
            gc = Prompt.ask("[bold cyan]Pilih (1/2/3)[/bold cyan]").strip()
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
            settings["random_locale"] = not settings["random_locale"]
            status_text = "AKTIF" if settings["random_locale"] else "NONAKTIF"
            console.print(f"[bold green]\u2713 Random Locale: {status_text}[/bold green]")
        elif choice == "5":
            if settings["use_temp_email"]:
                settings["use_temp_email"] = False
                console.print("[bold yellow]Temp Email dinonaktifkan.[/bold yellow]")
            else:
                settings["use_temp_email"] = True
                settings["use_real_email"] = False
                settings["use_contact_file"] = False
                console.print(
                    "[bold green]\u2713 Temp Email diaktifkan. "
                    "Real Email & Contact File dinonaktifkan.[/bold green]"
                )
        elif choice == "6":
            if settings["use_real_email"]:
                settings["use_real_email"] = False
                console.print("[bold yellow]Real Email dinonaktifkan.[/bold yellow]")
            else:
                settings["use_real_email"] = True
                settings["use_temp_email"] = False
                settings["use_contact_file"] = False
                console.print(
                    "[bold green]\u2713 Real Email diaktifkan. "
                    "Temp Email & Contact File dinonaktifkan.[/bold green]"
                )
        elif choice == "7":
            if settings["use_contact_file"]:
                settings["use_contact_file"] = False
                settings["contact_file"] = ""
                settings["contact_list"] = []
                console.print("[bold yellow]Contact File dinonaktifkan.[/bold yellow]")
            else:
                file_path = Prompt.ask(
                    "[bold cyan]Masukkan path file contact[/bold cyan]",
                    default=str(SAVE_DIR / "contacts.txt"),
                ).strip()
                if os.path.exists(file_path):
                    contacts = load_contact_file(file_path)
                    if contacts:
                        settings["use_contact_file"] = True
                        settings["use_temp_email"] = False
                        settings["use_real_email"] = False
                        settings["contact_file"] = file_path
                        settings["contact_list"] = contacts
                        console.print(
                            f"[bold green]\u2713 Contact File diaktifkan: "
                            f"{len(contacts)} contact dimuat.[/bold green]"
                        )
                    else:
                        console.print(
                            "[bold red]Tidak ada contact valid dalam file.[/bold red]"
                        )
                else:
                    console.print(f"[bold red]File tidak ditemukan: {file_path}[/bold red]")
        elif choice == "8":
            show_contact_list(settings)
            input("\nTekan Enter untuk kembali...")
        elif choice == "9":
            create_contact_file_example(str(SAVE_DIR))
        elif choice == "10":
            show_contact_file_info()
        elif choice == "11":
            show_all_locales()
        elif choice == "12":
            show_locale_info()

        time.sleep(0.5)


# =========================================================================
# Header and main menu
# =========================================================================

_header_shown = False


def show_header_once():
    global _header_shown
    if not _header_shown:
        console.print(Panel(
            "[bold white on blue] FACEBOOK BOT ACCOUNT GENERATOR[/bold white on blue]\n"
            "[bold red on white] AUTHOR : SLLOWLY | VERSION : V4.5[/bold red on white]",
            style="bright_blue",
        ))
        _header_shown = True


def main_menu(license_parts):
    """Main application menu loop."""
    global _header_shown

    while True:
        _header_shown = False
        clear_screen()
        show_header_once()

        saved = count_saved_accounts()
        menu_text = (
            f"[bold white]1.[/bold white] \U0001f680 Register Otomatis ([bold green]{settings['limit']}"
            f"[/bold green] akun)\n"
            f"[bold white]2.[/bold white] \u270d Register Manual (1 akun)\n"
            f"[bold white]3.[/bold white] \u2699 Settings\n"
            f"[bold white]4.[/bold white] \U0001f4ca Statistik\n"
            f"[bold white]5.[/bold white] \U0001f50d Cek UID Facebook\n"
            f"[bold white]6.[/bold white] \U0001f310 Lihat URL Registrasi\n"
            f"[bold white]7.[/bold white] \U0001f4c2 Buka Folder Penyimpanan\n"
            f"[bold white]0.[/bold white] Keluar"
        )
        console.print(Panel(menu_text, title="MENU UTAMA", style="green"))

        choice = Prompt.ask("[bold cyan]Pilih menu[/bold cyan]").strip()

        if choice == "0":
            console.print("[bold red]Keluar dari program...[/bold red]")
            sys.exit()
        elif choice == "1":
            console.print(
                f"\n[bold cyan]Memulai register otomatis {settings['limit']} akun...[/bold cyan]"
            )
            for _ in range(settings["limit"]):
                register_account()
                status["loop"] += 1
            console.print(
                f"\n[bold green]Selesai! Total akun live: {status['live']}[/bold green]"
            )
            input("\nTekan Enter untuk kembali ke menu...")
        elif choice == "2":
            register_manual()
        elif choice == "3":
            settings_menu()
        elif choice == "4":
            console.print(Panel(
                f"[bold white]Total Akun Live    :[/bold white] [bold green]{status['live']}"
                f"[/bold green]\n[bold white]Total Checkpoint   :[/bold white] [bold yellow]{status['cp']}"
                f"[/bold yellow]\n[bold white]Total Loop         :[/bold white] [bold cyan]{status['loop']}"
                f"[/bold cyan]\n[bold white]Akun Tersimpan     :[/bold white] [bold green]{saved}"
                f"[/bold green]\n[bold white]Gender Setting     :[/bold white] [bold yellow]{settings['gender_setting'].upper()}"
                f"[/bold yellow]\n[bold white]Random Locale      :[/bold white] [bold green]{'AKTIF' if settings['random_locale'] else 'NONAKTIF'}"
                f"[/bold green]\n[bold white]Total Locale       :[/bold white] [bold cyan]{len(FACEBOOK_LOCALES)}"
                f"[/bold cyan]\n[bold white]File Save          :[/bold white] [dim]{SAVE_FILE}"
                f"[/dim]\n[bold white]File Log           :[/bold white] [dim]{LOG_FILE}[/dim]",
                title="STATISTIK",
                style="cyan",
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
                    os.system(
                        f'xdg-open "{SAVE_DIR}" 2>/dev/null || termux-open "{SAVE_DIR}" 2>/dev/null'
                    )
                console.print(f"[bold green]Membuka folder: {SAVE_DIR}[/bold green]")
            except Exception as e:
                console.print(f"[bold red]Gagal membuka folder: {e}[/bold red]")
                console.print(f"[dim]Path manual: {SAVE_DIR}[/dim]")


# =========================================================================
# Entry point
# =========================================================================

if __name__ == "__main__":
    try:
        full_license = approval()
        license_parts = full_license
        main_menu(license_parts)
    except KeyboardInterrupt:
        console.print("\n[bold red]Program dihentikan oleh user.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
