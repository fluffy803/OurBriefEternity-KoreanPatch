# -*- coding: utf-8 -*-
"""Korean entries for the 11-20 UI catalog (python-packages/obe_localization_catalog.py).

The game draws its own UI text through l10n_ui(source), which looks the source up in
obe_localization_catalog.UI[<ui language>] -- Ren'Py's `translate strings` is not used
there.  So Korean needs UI["korean"].

  python ui_catalog.py todo    -> work/todo_ui.json   keys that still need Korean
  python ui_catalog.py build   -> work/ui_korean.json {key: korean} (used by build_mod.py)

Korean for a key is taken, in order, from
  work/ui_translated.json       translations made for todo_ui.json
  the tl units (work/units_translated.json, else units.json + chunks)  same source text,
                                also via CANONICAL variants and the schinese value
Keys that are source-code comments ("## ...") are never displayed and are skipped.
"""
import os, sys, json, collections, importlib.util

sys.stdout.reconfigure(encoding="utf-8")
W = os.environ.get("OBE_WORKSPACE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(W, "tools"))
import units as U

CATALOG = os.path.join(W, "v1120", "decompiled", "python-packages", "obe_localization_catalog.py")
WORK = os.path.join(W, "work")


def unesc(s):
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            n = s[i + 1]
            out.append({"n": "\n", '"': '"', "\\": "\\"}.get(n, "\\" + n))
            i += 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


def load_catalog():
    spec = importlib.util.spec_from_file_location("obe_cat", CATALOG)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def displayed_keys(m):
    keys = set().union(*[set(v) for v in m.UI.values()])
    return sorted(k for k in keys if not k.startswith("## "))


def unit_korean():
    path = os.path.join(WORK, "units_translated.json")
    us = json.load(open(path, encoding="utf-8"))
    ko = {}
    for u in us:
        if u["kind"] == "string" and u.get("dst"):
            ko.setdefault(unesc(u["src"]), unesc(u["dst"]))
    return ko


def unit_sources():
    us = json.load(open(os.path.join(WORK, "units.json"), encoding="utf-8"))
    return {unesc(u["src"]) for u in us if u["kind"] == "string"}


def candidates(m, inv, k):
    return [k] + inv.get(k, []) + [m.UI["schinese"].get(k, "")]


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "todo"
    m = load_catalog()
    inv = collections.defaultdict(list)
    for a, b in m.CANONICAL.items():
        inv[b].append(a)
    keys = displayed_keys(m)
    ko_units = unit_korean() if os.path.exists(os.path.join(WORK, "units_translated.json")) else {}
    ui_tr_path = os.path.join(WORK, "ui_translated.json")
    ui_tr = json.load(open(ui_tr_path, encoding="utf-8")) if os.path.exists(ui_tr_path) else {}

    if mode == "todo":
        srcs = unit_sources()
        todo = []
        for k in keys:
            if k in ui_tr or any(c in ko_units for c in candidates(m, inv, k)):
                continue
            if any(c in srcs for c in candidates(m, inv, k)):
                continue        # will be translated as a tl string unit
            todo.append({"key": k,
                         "zh": m.UI["schinese"].get(k, ""),
                         "en": m.UI["english"].get(k, ""),
                         "ja": m.UI["japanese"].get(k, "")})
        json.dump(todo, open(os.path.join(WORK, "todo_ui.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print(f"displayed catalog keys {len(keys)}, todo_ui {len(todo)}")
        return

    out, missing = {}, []
    for k in keys:
        if k in ui_tr and ui_tr[k]:
            out[k] = ui_tr[k]
            continue
        for c in candidates(m, inv, k):
            if c in ko_units:
                out[k] = ko_units[c]
                break
        else:
            missing.append(k)
    json.dump(out, open(os.path.join(WORK, "ui_korean.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"ui_korean: {len(out)}/{len(keys)} keys, missing {len(missing)}")
    for k in missing[:20]:
        print("   missing:", repr(k)[:80])


if __name__ == "__main__":
    main()
