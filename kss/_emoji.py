import emoji
import regex

_emojis = {}
for lang in ["pt", "it", "es", "en"]:
    emoji_unicode = emoji.unicode_codes.get_emoji_unicode_dict(lang)
    unicode_emoji = {v: k for k, v in emoji_unicode.items()}
    _emojis.update(unicode_emoji)


def get_emoji(text):
    emoji_list = []
    flags = regex.findall("[\U0001F1E6-\U0001F1FF]", text)

    for grapheme in regex.findall(r"\X", text):
        if any(char in _emojis for char in grapheme):
            emoji_list.append(grapheme)

    return emoji_list + flags
