"""
Shared constants used across registration flows.
"""

# Facebook registration domains
FB_REG_DOMAINS = [
    "m.facebook.com",
    "mbasic.facebook.com",
]

# Hardcoded Facebook API tokens
FB_APP_ID = "256002347743983"
FB_DTSG_DEFAULT = "NAfvUo9HbSAZyVEr3Ze2DkSh1kFr46CUODpUQsIl1E6M6S43_DOC7Zw:0:0"
FB_DYN = (
    "1Z3pawlEnwm8_Bg9ppoW5UqxK12wAxu13w9y3q327E39x60zU3ex608ewk9E4W0pKq0FE6S0"
    "x81vohw5Owk8aE36wqEd8dE2YwbK0iC1qw8W0k-0n6aw4kwbS1Lw9C0le0ue0QU3yw"
)
FB_A_TOKEN = (
    "AYwkI2qG1sefZTwey-Vm7WRWA3RPT1ZCrNAJRz0MhiehwXf8WPdKD-NK4s28ccnU"
    "XcXs-McSqtWPWP-PDYhSzcpsYzu-fGJWOIU"
)
FB_ENCPASS_HEADER = (
    "eyJ0eXBlIjowLCJjcmVhdGlvbl90aW1lIjoxNzgxMDI3MDQ1LCJjYWxsc2l0ZV9pZCI6OTA3OTI0NDAyOTQ4MDU4fQ=="
)

# Browser identification
SEC_CH_UA = '"Chromium";v="139", "Not;A=Brand";v="99"'
SEC_CH_UA_FULL = '"Chromium";v="139.0.7339.0", "Not;A=Brand";v="99.0.0.0"'

# File paths
DEFAULT_SAVE_DIR_ANDROID = "/sdcard/FACEBOOKME"
DEFAULT_SAVE_DIR_FALLBACK = "FACEBOOKME"
SAVE_FILENAME = "fbfreshmu.txt"
LOG_FILENAME = "fb_accounts_log.txt"

# Regex for cleaning phone numbers
PHONE_CLEAN_REGEX = r"[\s\-\(\)]"
