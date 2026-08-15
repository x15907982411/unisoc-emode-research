# Unisoc EngineerMode Research

展锐（Unisoc / Spreadtrum）平台**工程模式（EngineerMode）逆向研究笔记**。

基于 **ZTE W200DS（Unisoc T760 / UMS9230 / Android 13 / EMMC）** 的完整探索记录：
指令链暗码、Android 13 拦截行为、SELinux 域限制、攻击面穷尽清单、公开 root 路线评估。

> ⚠️ **免责声明**：本文档仅供安全研究与学习交流。文中涉及解锁、刷机、系统调试等操作，可能导致设备变砖、数据丢失、保修失效，请自行评估风险并承担后果。作者不对任何使用行为负责。

## 📁 文档导航

| 文档 | 内容 |
|---|---|
| [docs/01-instruction-chain.md](docs/01-instruction-chain.md) | EMode 指令链研究：入口、触发条件、Android 13 拦截根因、已破译暗码表 |
| [docs/02-selinux-boundary.md](docs/02-selinux-boundary.md) | 引擎模式 SELinux 域边界：可用能力 / 写权限极窄 / binder 全封死 |
| [docs/03-attack-surface.md](docs/03-attack-surface.md) | 攻击面穷尽清单：10 类尝试与失败原因 |
| [docs/04-public-root-paths.md](docs/04-public-root-paths.md) | 公开 root 路线评估：CVE-2022-38694 / fastboot token / system-root |
| [docs/05-mali-cve-2022-38181.md](docs/05-mali-cve-2022-38181.md) | Mali CVE-2022-38181 路线：调试链 / 符号偏移表 / 适配变体验证未走通 |
| [scripts/](scripts/README.md) | 研究工具集：暗码爆破脚本 / HIDL 调用器 |

## 🎯 核心结论（TL;DR）

1. **暗码**：工程模式主入口 `*#*#83781#*#*`；破译 5 个指令暗码 + 7 个 SECRET_CODE（详见 [01](docs/01-instruction-chain.md)）
2. **Android 13 拦截**：`queryIntentActivities(flags=0)` 在 API 33 默认过滤 non-exported 组件，导致所有指向 non-exported Activity 的指令**静默无响应**
3. **SELinux 一票否决**（实测范围内）：引擎模式（system uid + `sprd_engineermode_app` 域）写权限极窄，binder 调 system_server 的测试调用全部被拦截
4. **本次测试范围内未发现用户空间 root 路线**：尝试的 10 类攻击面全部失败，评审后补充测试（动态广播 / ContentProvider / 内核版本）亦未发现可行面（测试边界与补充测试见 [docs/03](docs/03-attack-surface.md)）；Mali CVE-2022-38181 路线在本设备适配的 PoC 变体上未走通（BSP 定制差异）；公开可行路线 = **CVE-2022-38694 BROM 解锁 + Magisk**（需 PC + USB）

## 🖥️ 设备档案

| 项 | 值 |
|---|---|
| 型号 | ZTE W200DS |
| SoC | Unisoc T760（UMS9230）|
| GPU | Mali-G57 |
| 系统 | Android 13（API 33）|
| 存储 | EMMC（A/B 分区）|

## 🔗 相关资源

- [TomKing062/CVE-2022-38694_unlock_bootloader](https://github.com/TomKing062/CVE-2022-38694_unlock_bootloader) — BROM 解锁工具
- [Phlegmelm/CRACK12](https://github.com/Phlegmelm/CRACK12) — ATOZEE P12（UMS9230）实战
- [KiMiGuel/Root-Guide-Cubot-KingKong-ES-3](https://github.com/KiMiGuel/Root-Guide-Cubot-KingKong-ES-3---Unisoc-T615-ums9230-) — EMMC 版 100% 确认
- [sloden1977-lang/ROOT-ZTE-X1001](https://github.com/sloden1977-lang/ROOT-ZTE-X1001) — ZTE Blade X1001（UMS9230）UFS 版

## 🗄️ 本地资产说明（未随仓库分发）

研究过程中的完整资产保留在本地，以下内容**不纳入本仓库**：

| 资产 | 原因 |
|---|---|
| 反编译产物（emode_decode / em_decode / vfw / logmanager_decode 等）| 版权归原作者/厂商 |
| mali_shrinker.c exploit 源码 + 37 个迭代 APK | 武器化代码，仅文档化方法学（见 docs/05）|
| 设备提取的驱动/内核模块（libGLES_mali.so / mali_kbase.ko）| 版权归 ARM/厂商 |
| 内核源码（zte_kernel_ums9230，251MB）| 体积 + 版权 |

## 📄 License

MIT — 见 [LICENSE](LICENSE)
