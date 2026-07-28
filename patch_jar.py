#!/usr/bin/env python3
"""
Заменяет natives/EffekseerNativeForJava.so внутри hc-1.19.2-1.6.3.jar на собранный
arm64-v8a бинарник, не трогая остальные записи jar-а (важно: jar это zip, простое
"zip -j" может задублировать запись или сломать индекс — поэтому пересобираем архив
через zipfile целиком).

Использование:
    python3 patch_jar.py <original.jar> <new_EffekseerNativeForJava.so> <output.jar>
"""
import sys
import zipfile
import shutil

TARGET_ENTRY = "natives/EffekseerNativeForJava.so"


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)

    src_jar, new_so, out_jar = sys.argv[1:4]

    with open(new_so, "rb") as f:
        new_so_bytes = f.read()

    if len(new_so_bytes) < 1000:
        print(f"ВНИМАНИЕ: {new_so} подозрительно маленький ({len(new_so_bytes)} байт) — "
              f"это, вероятно, не настоящая собранная библиотека. Прерываю.")
        sys.exit(2)

    with zipfile.ZipFile(src_jar, "r") as zin:
        names = zin.namelist()
        if TARGET_ENTRY not in names:
            print(f"ВНИМАНИЕ: {TARGET_ENTRY} не найден в {src_jar}. "
                  f"Найденные natives/*: {[n for n in names if n.startswith('natives/')]}")
            sys.exit(3)

        with zipfile.ZipFile(out_jar, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == TARGET_ENTRY:
                    data = new_so_bytes
                    print(f"Заменяю {item.filename}: {len(zin.read(item.filename))} -> {len(data)} байт")
                zout.writestr(item, data)

    print(f"Готово: {out_jar}")


if __name__ == "__main__":
    main()
