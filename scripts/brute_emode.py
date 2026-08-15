#!/usr/bin/env python3
import hashlib, itertools, sys, time

targets = {
    "4701DA9372B93D18": "ENABLEEMODE",
    "BF1F64B41A16C143": "MAIN_MENU",
    "0336780B8BDF25C4": "MANUFACTURE_MENU",
    "B70BF1A6C322E539": "DISABLEEMODE",
}

def h(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()[8:24].upper()

found = {}
t0 = time.time()

# 1) 常见口令
common = ["0000","1234","5678","931","83781","83782","33284","983","28868378","654987","833",
          "000000","123456","111111","888888","999999","00000000","12345678","88888888",
          "9876","12345","54321","6666","7777","8888","9999","1000","0001","1997","2000","2024","2025","2026"]
for c in common:
    hv = h(c)
    if hv in targets:
        found[targets[hv]] = c
        print(f"[COMMON] {targets[hv]} = {c}")

# 2) 4-6位纯数字全爆
for ln in range(4, 7):
    for tup in itertools.product("0123456789", repeat=ln):
        s = "".join(tup)
        hv = h(s)
        if hv in targets:
            found[targets[hv]] = s
            print(f"[BRUTE{ln}] {targets[hv]} = {s}")
        if len(found) >= 3:
            break
    if len(found) >= 3:
        break
    print(f"  {ln}位完成, 用时{time.time()-t0:.1f}s, 已找到{len(found)}")

# 3) 7-8位常见模式（前3位固定常见前缀）
prefixes = ["000","111","123","666","888","999","100","200","837","983","931","654","288"]
for ln in [7, 8]:
    if len(found) >= 3: break
    for p in prefixes:
        rem = ln - len(p)
        for tup in itertools.product("0123456789", repeat=rem):
            s = p + "".join(tup)
            hv = h(s)
            if hv in targets:
                found[targets[hv]] = s
                print(f"[PREFIX{ln}] {targets[hv]} = {s}")
        if len(found) >= 3: break

print(f"\n结果: {found}")
print(f"总用时: {time.time()-t0:.1f}s")