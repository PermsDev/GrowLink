
NAME = "setup promote"

DESCRIPTION = (
    "Mengatur panel promosi item atau world."
)

USAGE = [
    "/setup promote channel:<channel>",
]

DETAILS = """
Command ini digunakan oleh administrator untuk mengatur
panel Promote di server Discord.

Panel Promote dirancang agar member dapat mengajukan
promosi item, world, atau service. Fitur ini ditujukan untuk membantu
promosi menjangkau komunitas di berbagai server yang menggunakan GrowLink.

Fitur Promote saat ini masih dalam tahap beta. Ketersediaan
proses pengajuan dan distribusi mengikuti implementasi
fitur yang sedang aktif.
"""

OPTIONS = [
    {
        "name": "channel",
        "description": "Channel tempat panel Promote akan dikirim.",
        "required": True,
    }
]

USAGE = [
    "`/setup promote` **channel:** `<channel>`",
]

PERMISSIONS = [
    "Administrator",
]

EXAMPLES = [
    {
        "command": "`/setup promote` **channel:** `#promotion`",
        "description": "Membuat atau memperbarui panel Promote.",
    },
]
