NAME = "setup intro"

DESCRIPTION = (
    "Mengatur panel Introduction untuk memperkenalkan "
    "GrowID anggota."
)

DETAILS = """
Command ini digunakan oleh administrator untuk mengatur
fitur Introduction di server Discord.

Panel Introduction memungkinkan anggota mengirimkan
informasi identitas game mereka melalui formulir yang
disediakan oleh GrowLink.

berikut beberapa kegunaan pada fitur ini:
- Verifikasi identitas
- Mengubah Display Name Menggunakan GrowID
- Sinkronisasi data GrowID di semua server yang menggunakan GrowLink
- Memberikan role kepada anggota setelah mengisi Introduction

Gunakan command ini untuk membuat atau memperbarui panel
Introduction sesuai konfigurasi server.
"""

OPTIONS = [
    {
        "name": "channel",
        "description": "Channel tempat panel Introduction akan dikirim.",
        "required": True,
    },
    {
        "name": "role",
        "description": "Role yang diberikan kepada anggota setelah mengisi Introduction",
        "required": False,
    },
]

USAGE = [
    "`/setup intro` **channel:** `<channel>` **role:** `<role>`",
]

PERMISSIONS = [
    "Administrator",
]

EXAMPLES = [
    {
        "command": "`/setup intro` **channel:** `#introduction`",
        "description": "Membuat panel Introduction di channel yang ditentukan",
    },
    {
        "command": "`/setup intro` **channel:** `#introduction` **role:** `@Growtopia`",
        "description": "Membuat panel Introduction di channel yang ditentukan dan mengatur role anggota. biasanya digunakan untuk mewajibkan anggota untuk melakukan verifikasi (introduction) sebelum mengakses channel server lainnya. (pastikan mengatur permision channel dengan benar)",
    },
]