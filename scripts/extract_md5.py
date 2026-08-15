#!/usr/bin/env python3
"""提取所有16hex字符串及其上下文的name"""
import re

with open("/sdcard/Download/Operit/emode_decode/smali/com/zte/emode/base/command/Command.smali", "r", encoding="utf-8") as f:
    lines = f.readlines()

# 找 16hex 字符串所在行，向前找最近的 const-string "NAME"（name在md5前10行内）
for i, line in enumerate(lines):
    m = re.search(r'const-string v\d+, "([0-9A-F]{16})"', line)
    if m:
        md5 = m.group(1)
        name = "?"
        for j in range(max(0, i-10), i):
            m2 = re.search(r'const-string v\d+, "([A-Z_][A-Z_0-9]*)"', lines[j])
            if m2:
                name = m2.group(1)
        desc = ""
        for j in range(i+1, min(len(lines), i+5)):
            m3 = re.search(r'const-string v\d+, "([^"]+)"', lines[j])
            if m3 and len(m3.group(1)) < 40 and not re.fullmatch(r'[0-9A-F]{16}', m3.group(1)):
                desc = m3.group(1)
                break
        print(f"{name:28s} {md5}  desc={desc}")