# -*- coding: utf-8 -*-
"""Diff two RPA-3.0 archives entry by entry (sha1 of each entry's bytes)."""
import sys, hashlib
sys.path.insert(0, r"D:\게임분석\steam\기술분석\OurBriefEternity\tools")
from rpa_index import read_index

sys.stdout.reconfigure(encoding="utf-8")


def digests(path):
    idx = read_index(path)
    out = {}
    with open(path, "rb") as f:
        for name, parts in idx.items():
            h = hashlib.sha1()
            for off, ln, st in parts:
                f.seek(off)
                h.update(st + f.read(ln - len(st)) if st else f.read(ln))
            out[name] = h.hexdigest()
    return out


a, b = digests(sys.argv[1]), digests(sys.argv[2])
added = sorted(set(b) - set(a))
removed = sorted(set(a) - set(b))
changed = sorted(k for k in set(a) & set(b) if a[k] != b[k])
print(f"old {len(a)} / new {len(b)} entries")
print(f"added {len(added)}:", *added, sep="\n  ")
print(f"removed {len(removed)}:", *removed, sep="\n  ")
print(f"changed {len(changed)}:", *changed, sep="\n  ")
