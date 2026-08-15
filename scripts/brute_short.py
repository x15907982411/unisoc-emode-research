#!/usr/bin/env python3
"""补爆：1-6位无前导0，三种格式，目标 ENABLEEMODE+SAVERANDOM"""
import hashlib, time

TARGETS = {
    "4701DA9372B93D18": "ENABLEEMODE",
    "6049B7CBFC70BC5A": "SAVERANDOM",
}

def mid16(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()[8:24].upper()

t0 = time.time()
found = []
out = "/root/brute_short.txt"
open(out, "w").close()
for n in range(1, 1000000):
    d = str(n)
    for fmt, s in (("bare", d), ("star", "*#" + d + "#"), ("fullstar", "*#*#" + d + "#*#*")):
        h = mid16(s)
        if h in TARGETS:
            line = f"HIT: {TARGETS[h]} = {s}  (fmt={fmt})"
            found.append(line)
            print(line, flush=True)
            with open(out, "a") as f:
                f.write(line + "\n")
    if n % 200000 == 0:
        print(f"progress {n} {time.time()-t0:.0f}s hits={len(found)}", flush=True)
print(f"done {time.time()-t0:.1f}s hits={len(found)}", flush=True)