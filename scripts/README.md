# Scripts — 研究工具集

EMode 指令链研究过程中使用的辅助脚本（Python 3，仅研究用途）。

## 暗码爆破

| 脚本 | 用途 |
|---|---|
| `brute_emode.py` | 主爆破：目标 ENABLEEMODE/MAIN_MENU/MANUFACTURE_MENU/DISABLEEMODE（MD5 中间 16 位匹配）。策略：常见口令 → 4-6 位全爆 → 7-8 位前缀模式 |
| `brute_short.py` | 补爆：1-6 位无前导 0 × 3 格式（bare / star / fullstar），目标 ENABLEEMODE + SAVERANDOM |
| `extract_md5.py` | 从 `Command.smali` 提取所有 16hex MD5 字符串及其上下文 name/desc（爆破目标来源）|
| `map_runs.py` | 映射 `Command` 字段 → hash → 运行类 → 策略（指令链结构分析）|

### 暗码格式说明

- 指令暗码：`*#XXXXXX#`
- SECRET_CODE：`*#*#XXXXXX#*#*`
- 校验方式：`md5(输入).hexdigest()[8:24].upper()` 与 smali 内常量比对

### 爆破结论（未命中）

- 8 位 × 3 格式全爆约 3e7 次：无命中
- 1-6 位无前导 0 × 3 格式约 3.3e6 次：无命中
- `ENABLEEMODE(4701DA9372B93D18)` / `SAVERANDOM(6049B7CBFC70BC5A)` 非纯数字拨号码（可能由菜单按钮触发，不走指令链）

## HIDL 调用器

| 脚本 | 用途 |
|---|---|
| `Main.java` | ILogControl HIDL 全反射调用器（`vendor.sprd.hardware.log.V1_0.ILogControl`）：`java Main <socket> <cmd>` |

> 该调用器在目标设备上因 engineermode 域无法落地 dex 而未能执行（见 docs/02、docs/03），保留作为 HIDL 反射调用参考实现。