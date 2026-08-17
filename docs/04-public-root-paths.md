# 04 · 公开 root 路线评估

在本次用户空间路线测试未发现可行方案后，公开可行的路线全部指向 **硬件/引导层**，需要 **Windows PC + USB 线**。

> ⚠️ **勘误（2026-08-17）**：本文档最初基于「W200DS = UMS9230」的误判评估 38694 适用性。经实测确认本机平台为 **UMS9620**，且 **CVE-2022-38694 的 UMS9230 / UMS9620 两版工具包均已实测失败**（2026-08-16：9230 包刷入后设备重启、数据被清但 BL 未解锁；9620 包同样无效）。以下内容保留作路线记录，**适用性结论均已失效**。

## 路线 A：CVE-2022-38694 BROM 解锁 + Magisk（首选）

**适用**：UMS9230 平台设备（⚠️ **本设备 W200DS 实际为 UMS9620，且 38694 双版工具包实测无效**）。

### 工具

- [TomKing062/CVE-2022-38694_unlock_bootloader](https://github.com/TomKing062/CVE-2022-38694_unlock_bootloader)
- 下载 `releases/download/1.72/ums9230_universal_unlock.zip`（Windows .bat）

### 流程

```
1. PC 安装 SPD U2S 驱动（SPD_Driver_R4.20.4201）
2. 设备关机 → 长按音量下 + 插 USB → 进入 BROM 模式（设备管理器出现 COM/LPT 端口）
3. 运行 unlock_autopatch_9230.bat（自动执行，设备会被 wipe）
4. adb pull boot 分区（脚本自动 dump boot.bin）
5. Magisk 安装 → patch boot.bin → adb pull magisk_patched_*.img
6. fastboot --disable-verity --disable-verification flash boot_a <magisk_patched>.img
   （A/B 分区注意 boot_a / boot_b）
7. fastboot reboot → su -c whoami = root
```

### 实战参考

| 仓库 | 设备 | 备注 |
|---|---|---|
| [Phlegmelm/CRACK12](https://github.com/Phlegmelm/CRACK12) | ATOZEE P12（UMS9230/T615，Android 14）| 全流程 + 踩坑 ⭐ |
| [KiMiGuel/Root-Guide-Cubot-KingKong-ES-3](https://github.com/KiMiGuel/Root-Guide-Cubot-KingKong-ES-3---Unisoc-T615-ums9230-) | Cubot KingKong ES3（EMMC 版）| 100% 确认 |
| [sloden1977-lang/ROOT-ZTE-X1001](https://github.com/sloden1977-lang/ROOT-ZTE-X1001) | ZTE Blade X1001（UMS9230，UFS 版）| UFS 差异 |

> ⚠️ UMS9230 有 **EMMC / UFS** 两种存储版本，工具与流程略有差异。以上参考均为 UMS9230 设备，**不适用于本设备（UMS9620）**。

## 路线 B：fastboot token 解锁（有 PC 后第一验证项）

展锐通用 fastboot 解锁机制，若支持则**无需 BROM 漏洞**：

```
fastboot oem get_identifier_token
# 得到 Identifier token（一行，无空格）

# 方式 A（另一台安卓设备）：装解锁密钥生成 APK，输入序列号 → signature.bin
# 方式 B（纯 Windows）：WSL 中 ./signidentifier.sh <ID> rsa4096_vbmeta.pem signature.bin

fastboot flashing unlock_bootloader signature.bin
# 音量下确认 → 格机 → 解锁完成
```

> ⚠️ **实测结果（2026-08-16）**：本机 fastboot token 路线**无效**——`get_identifier_token` 可执行，但解锁需要对应私钥签名，私钥未知、官方不提供，此路不通。

## 路线 C：展锐 boot 无 ramdisk → system-root 法

展锐 boot 分区通常无 ramdisk，Magisk 改植入 **system 分区**：

```
spd_dump fdl <fdl1> 0x5500 fdl <fdl2> 0x9efffe00 exec partition_list partition.xml
spd_dump fdl <fdl1> 0x5500 fdl <fdl2> 0x9efffe00 exec read_part system 0 <size> system.img
mkdir system && sudo mount -o rw system.img system
# 拷入 magisk / magiskpolicy / magisk.rc / magisk 目录（system/etc/init/ 下）
# 改 bootanim.rc 追加 post-fs-data 钩子（magiskpolicy --live --magisk + magisk64 --auto-selinux）
# build.prop 加 persist.service.adb.enable=1 / persist.sys.usb.config=diag,adb,mtp
sudo umount system.img
spd_dump fdl <fdl1> 0x5500 fdl <fdl2> 0x9efffe00 exec write_part system system.img reset
```

### spd_dump 命令速记

| 命令 | 功能 |
|---|---|
| `partition_list partition.xml` | 读分区表 |
| `read_part <名> 0 <大小> <文件>` | 读分区（或 read_parts partition.xml 批量）|
| `write_part <名> <镜像>` | 写分区 |
| `erase_part <名>` | 擦除分区 |
| `reset` | 重启（放命令末尾）|

多条命令可拼接（exec 后全放一起，reset 在最后）。

## 展锐 SoC 解锁分代

| 芯片 | 方案 |
|---|---|
| UMS9230 及更旧 | CVE-2022-38694 |
| UMS312 / UMS512 / UD710 | CVE-2022-38691_38692 |
| 通用 | Spectrum_UnlockBL_Tool（Unisoc 专用）|

> ⚠️ **勘误**：此前写「W200DS = UMS9230 → 仍属 38694 系」——**错误**。本机实测为 **UMS9620**，且 38694 双版工具包（9230/9620）均已实测失败，root 目标已搁置。

## 总结

```
实测结论（2026-08-16）：
1. fastboot token 解锁（路线 B）——私钥未知，无效
2. CVE-2022-38694 BROM 解锁（路线 A）——9230/9620 双包均无效
3. system-root 法（路线 C）——未实施（依赖 9008/spd_dump 通道，风险高）

后续方向（2026-08-17 新线索）：recovery 模式可挂载系统分区（待验证），
见仓库外研究笔记；root 目标当前处于搁置状态。
```