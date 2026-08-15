#!/usr/bin/env python3
import re
src = open('/sdcard/Download/Operit/emode_decode/smali/com/zte/emode/base/command/Command.smali', encoding='utf-8').read()
blocks = re.split(r'sput-object v\d+, Lcom/zte/emode/base/command/Command;->([A-Z_0-9]+):', src)
for i in range(1, len(blocks), 2):
    name = blocks[i]
    body = blocks[i+1][:3000]
    m_hash = re.search(r'"([0-9A-F]{16})"', body)
    m_run = re.search(r'Lcom/zte/emode/base/command/(\w+);-><init>', body)
    m_strat = re.search(r'Command\$Strategy;->(\w+)', body)
    if m_hash and m_run:
        print(f'{name:28s} {m_hash.group(1)}  run={m_run.group(1):30s} strat={m_strat.group(1) if m_strat else "?"}')