# ════════════════════════════════════════
#  Satoru — Utility Functions
# ════════════════════════════════════════
import re
from config import OWNER_ID


def is_owner(event) -> bool:
    """Check if event is from the owner"""
    return event.out or (hasattr(event, "sender_id") and event.sender_id == OWNER_ID)


def get_args(event, prefix_len: int = 1) -> str:
    """Extract arguments from command"""
    text = event.raw_text.strip()
    parts = text.split(maxsplit=prefix_len)
    return parts[prefix_len] if len(parts) > prefix_len else ""


def get_args_split(event, prefix_len: int = 1):
    """Extract arguments split by space"""
    text = event.raw_text.strip()
    parts = text.split()
    return parts[prefix_len:] if len(parts) > prefix_len else []


# ─── Unicode Font Converters ───────────────────────────────────────
_BOLD = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
    "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵"
)
_ITALIC = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻"
)
_SCRIPT = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "𝒜ℬ𝒞𝒟ℰℱ𝒢ℋℐ𝒥𝒦ℒℳ𝒩𝒪𝒫𝒬ℛ𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵𝒶𝒷𝒸𝒹ℯ𝒻ℊ𝒽𝒾𝒿𝓀𝓁𝓂𝓃ℴ𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏"
)
_DOUBLE = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
    "𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡"
)
_MONO = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
    "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿"
)
_SMALL_CAPS = str.maketrans(
    "abcdefghijklmnopqrstuvwxyz",
    "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀꜱᴛᴜᴠᴡxʏᴢ"
)

FONT_MAP = {
    "bold":       lambda t: t.translate(_BOLD),
    "italic":     lambda t: t.translate(_ITALIC),
    "script":     lambda t: t.translate(_SCRIPT),
    "double":     lambda t: t.translate(_DOUBLE),
    "mono":       lambda t: t.translate(_MONO),
    "smallcaps":  lambda t: t.translate(_SMALL_CAPS),
    "strike":     lambda t: "".join(c + "\u0336" for c in t),
    "underline":  lambda t: "".join(c + "\u0332" for c in t),
    "wide":       lambda t: " ".join(t),
    "reverse":    lambda t: t[::-1],
    "bubble": lambda t: "".join(
        chr(0x24B6 + ord(c) - ord("A")) if "A" <= c <= "Z" else
        chr(0x24D0 + ord(c) - ord("a")) if "a" <= c <= "z" else
        chr(0x2460 + ord(c) - ord("1")) if "1" <= c <= "9" else
        "⓪" if c == "0" else c
        for c in t
    ),
}


def convert_font(text: str, font: str) -> str:
    fn = FONT_MAP.get(font.lower())
    return fn(text) if fn else text


def tashkeel(text: str) -> str:
    """Add random tashkeel (Arabic diacritics) for fun"""
    harakat = ["َ", "ُ", "ِ", "ً", "ٌ", "ٍ", "ْ", "ّ"]
    import random
    result = []
    for ch in text:
        result.append(ch)
        if "\u0600" <= ch <= "\u06FF" and random.random() > 0.5:
            result.append(random.choice(harakat))
    return "".join(result)
