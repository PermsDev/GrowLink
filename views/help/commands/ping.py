
NAME = "ping"

DESCRIPTION = (
    "Memeriksa apakah GrowLink sedang online "
    "dan menampilkan latency bot."
)

DETAILS = """
Command ini digunakan untuk memeriksa status koneksi GrowLink
ke Discord Gateway melalui nilai latency bot.

Latency ditampilkan dalam milidetik (ms). Nilai yang lebih
rendah umumnya menunjukkan respons koneksi yang lebih cepat.

Command ini tidak melakukan pengujian kecepatan internet
secara keseluruhan.
"""

OPTIONS = []

USAGE = [
    "/ping",
]

PERMISSIONS = [
    "Public",
]

EXAMPLES = [
    {
        "command": "/ping",
        "description": (
            "Memeriksa apakah GrowLink sedang online "
            "dan melihat latency bot."
        ),
    },
]
