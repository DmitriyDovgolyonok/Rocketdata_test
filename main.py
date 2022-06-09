import json
from settings import Parser

MONOMAH_URL = "http://monomax.by/map"
ZIKO_URL = "https://www.ziko.pl/lokalizator/"
KFC_URL = "https://api.kfc.com/api/store/v2/store.get_restaurants?showClosed=true"


def main():
    monomah_result = Parser.monomah_parse(MONOMAH_URL)
    ziko_result = Parser.ziko_parse(ZIKO_URL)
    kfc_result = Parser.kfc_parse(KFC_URL)

    files = {
        "kfc.json":  kfc_result,
        "ziko.json": ziko_result,
        "monomah.json": monomah_result
    }

    for key, value in files.items():
        with open(key, 'w', encoding='utf-8') as f:
            json.dump(value, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
