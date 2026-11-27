# -*- coding: utf-8 -*-
"""Rebase the Korean tl data onto the 11-20 update (buildid 26801865).

The update added an official localisation system (english/japanese/tchinese,
separate text/UI/voice languages).  Dialogue did not change, but the string
set did, so the tl template and work/units.json are rebuilt and the existing
Korean is carried over:

  dialogue  by (file, translate id, slot)
  strings   by source text

Inputs (made beforehand):
  v1120/proj/game/tl/korean       dialogue template (tlgen from the shipped .rpyc)
  v1120/proj_src/game/tl/korean   strings template (translate --strings-only on decompiled .rpy)
  v1120/decompiled/tl/english/localization_strings.rpy   strings the game looks up via l10n_text()

Outputs:
  tl_korean/                         new template (old one kept as tl_korean_1012/)
  work/units.json                    new unit list (old work/ kept as work_1012/)
  work/chunks/chunk_000_old.out.json carried-over Korean
"""
import os, sys, re, json, shutil

sys.stdout.reconfigure(encoding="utf-8")
W = os.environ.get("OBE_WORKSPACE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(W, "tools"))
import units as U
from extra_strings import EXTRA

V = os.path.join(W, "v1120")
DIALOGUE = os.path.join(V, "proj", "game", "tl", "korean")
STRINGS = os.path.join(V, "proj_src", "game", "tl", "korean")
L10N_EN = os.path.join(V, "decompiled", "tl", "english", "localization_strings.rpy")
OUT = os.path.join(W, "tl_korean")
WORK = os.path.join(W, "work")

STR_HDR = re.compile(r"^translate korean strings:\s*$", re.M)
OLD_LINE = re.compile(r'^    old "(.*)"$', re.M)


def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def strings_block(path):
    text = open(path, encoding="utf-8-sig").read()
    m = STR_HDR.search(text)
    return text[m.start():].rstrip() + "\n" if m else ""


def write_strings(path, olds, note):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\ufeff# " + note + "\n\ntranslate korean strings:\n")
        for o in olds:
            f.write(f'\n    old "{o}"\n    new "{o}"\n')


def backup():
    for src, dst in ((OUT, OUT + "_1012"), (WORK, WORK + "_1012")):
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copytree(src, dst)
            print(f"backup {src} -> {dst}")


def build_template():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    shutil.copytree(DIALOGUE, OUT)
    for root, _, files in os.walk(OUT):
        for fn in files:
            if fn.endswith(".rpyc"):
                os.remove(os.path.join(root, fn))

    seen = set()
    for root, _, files in os.walk(STRINGS):
        for fn in sorted(files):
            if not fn.endswith(".rpy"):
                continue
            src = os.path.join(root, fn)
            rel = os.path.relpath(src, STRINGS)
            block = strings_block(src)
            if not block:
                continue
            seen.update(OLD_LINE.findall(block))
            dst = os.path.join(OUT, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.exists(dst):
                with open(dst, "a", encoding="utf-8") as o:
                    o.write("\n" + block)
            else:
                with open(dst, "w", encoding="utf-8") as o:
                    o.write("\ufeff# strings\n\n" + block)

    # strings the game translates through l10n_text() (speaker names, choices, ...)
    l10n = [o for o in OLD_LINE.findall(open(L10N_EN, encoding="utf-8-sig").read()) if o not in seen]
    seen.update(l10n)
    write_strings(os.path.join(OUT, "localization_strings.rpy"), l10n,
                  "Strings the 11-20 build looks up with l10n_text() (same list as tl/english).")

    extra = [o for o in (esc(x) for x in EXTRA) if o not in seen]
    seen.update(extra)
    write_strings(os.path.join(OUT, "zz_extra_strings.rpy"), extra,
                  "Displayed strings not wrapped in _() (kept from the 10-12 build).")
    print(f"template: {len(l10n)} localization strings, {len(extra)} extra strings")


def carry_over(units):
    old = json.load(open(os.path.join(WORK + "_1012", "units_translated.json"), encoding="utf-8"))
    dlg = {(u["file"], u["id"], u.get("slot", 0)): u["dst"] for u in old
           if u["kind"] == "dialogue" and u.get("dst")}
    strs = {}
    for u in old:
        if u["kind"] == "string" and u.get("dst"):
            strs.setdefault(u["src"], u["dst"])
    rows, n_dlg, n_str = [], 0, 0
    for i, u in enumerate(units):
        if u["kind"] == "dialogue":
            k = (u["file"], u["id"], u.get("slot", 0))
            if k in dlg:
                rows.append({"i": i, "dst": dlg[k]}); n_dlg += 1
        elif u["src"] in strs:
            rows.append({"i": i, "dst": strs[u["src"]]}); n_str += 1
    return rows, n_dlg, n_str


def main():
    backup()
    build_template()
    units = U.extract(OUT)
    os.makedirs(os.path.join(WORK, "chunks"), exist_ok=True)
    for fn in os.listdir(os.path.join(WORK, "chunks")):
        os.remove(os.path.join(WORK, "chunks", fn))      # old indices are invalid now
    json.dump(units, open(os.path.join(WORK, "units.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    rows, n_dlg, n_str = carry_over(units)
    json.dump(rows, open(os.path.join(WORK, "chunks", "chunk_000_old.out.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    need = [u for i, u in enumerate(units) if U.needs_translation(u)]
    done = {r["i"] for r in rows}
    todo = [i for i, u in enumerate(units) if U.needs_translation(u) and i not in done]
    by_kind = {}
    for i in todo:
        k = (units[i]["file"], units[i]["kind"])
        by_kind[k] = by_kind.get(k, 0) + 1
    print(f"units {len(units)} (need translation {len(need)}), carried dialogue {n_dlg}, strings {n_str}")
    print(f"still untranslated: {len(todo)}")
    for k, v in sorted(by_kind.items()):
        print("  ", k, v)


if __name__ == "__main__":
    main()
