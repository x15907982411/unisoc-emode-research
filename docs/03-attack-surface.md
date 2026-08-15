# 03 · 攻击面穷尽清单

引擎模式（system uid + sprd_engineermode_app 域）下**本次尝试**的 10 类攻击面，**全部失败**。

## 攻击面总表

| # | 攻击面 | 尝试方式 | 结果 |
|---|---|---|---|
| 1 | VendorLogManagerService 广播链 | CLEAN_VENDOR_TARGET_LOG，logPath 注入 | 广播投递成功，但 subsys 进程为空壳实现（cleanTargetVendorLog 只有日志），无文件生成 |
| 2 | VendorLogManagerService binder 直调 | code 4-10 暴力扫描 | 服务端 = subsys 空壳实例（VLMS 日志证实 pid2394），且方法带 MODEMSERVICE 权限检查 |
| 3 | SprdLogService（system_server）| executeShellCmd = Runtime.exec(cmd) | 命令全固定（ylogctl op/cl hcidump），无注入参数；无外部触发入口 |
| 4 | SubsysService AIDL / ISubsys HIDL | sendLogCommand(socket, cmd) | 内部命令固定（modem 1000-1051），无任意命令转发；HIDL 访问面被 SELinux 限制 |
| 5 | ISysLogControl（cplogserver root 进程 HIDL）| get/set LogSettings | 全是结构化参数，无命令方法 |
| 6 | ILogControl HIDL sendCmd → ylog_cli_cmd → ylog/ylogw(root) | 全反射调用 dex | **工具链已就绪**，但 engineermode 域写不了任何系统目录（/data/anr、/cache、/data/system、/data/vendor/ylog 全被拒），dex 无法落地 |
| 7 | usermodehelper（core_pattern / modprobe / uevent_helper）| 尝试读写 | 全部 SELinux 拒 |
| 8 | socket（engpc_ctl / ylog_cli / cmd_services / miscserver）| 连接尝试 | 被 SELinux 拒（需 system_server / system_app 域）|
| 9 | devmem / insmod / ptrace / /dev/autotest0 | 设备节点操作 | /dev/mem 不存在；ro.vendor.ko.mount.point 为空；域隔离禁止 ptrace；autotest0(root:root 600) 权限不足 |
| 10 | miscdata 写（EModeService 通道）、BCB 修改 | 评估后放弃 | 危险：可能触发恢复出厂 / rec 循环 |

## 关键失败模式

1. **空壳服务**：特权服务（VendorLog / Subsys / cplog / ylog）全部是空壳实现或参数固定——接口存在但无能力
2. **文件无法落地**：即使拥有完整的调用工具链（dex），SELinux 拒绝在所有系统目录写入——payload 进不去
3. **一票否决**：权限面全绿（emode 持有多个特权权限 granted=true）也过不了 avc 域隔离

## 最终结论

**本次测试范围内未发现用户空间 root 路线。** 引擎模式（system uid）受 sprd_engineermode_app 域 SELinux 严格限制：

- 写权限：除自身 app 数据目录外几乎全拒
- 特权服务：全部为空壳或参数固定
- 本次测试的 usermodehelper / socket / devmem 通道均被内核 + 安全策略拒绝

## 测试边界与补充测试

本次评估聚焦于 Java/HIDL 层的命令执行与服务调用链。以下为评审后补充的测试记录与仍未覆盖的边界。

### 已补充测试（2026-08-15）

| 攻击面 | 结果 |
|---|---|
| 动态广播接收器注入（com.zte.emode / com.zte.emodeservice / com.sprd.engineermode 全量静态扫描）| **排除**：emode 14 处动态注册均为测试页 UI 刷新（USB/电池/蓝牙状态）或固定参数反射调用（`SlicManager.incomingCall` 参数不可控，仅可伪造"模拟来电"骚扰）；engineermode 4 处全部监听受保护系统广播（ACTION_SHUTDOWN / BATTERY_CHANGED / AIRPLANE_MODE / SIM_STATE），第三方无法伪造 |
| ContentProvider 暴露面（同上三包 Manifest + 代码审计）| **排除**：三个应用均未声明 ContentProvider |
| Intent 重定向（同上三包全量扫描）| **排除**：全库仅 2 处 startActivityForResult（emode），intent 均为内部构造（指纹测试 challenge）或系统固定 action（MANAGE_OVERLAY_PERMISSION）；无 getParcelableExtra 取 Intent 再 start 的模式；无 EXTRA_INTENT 使用；emodeservice / engineermode 零 startActivityForResult |
| 内核漏洞版本复验 | 内核 **5.4.254**（2024-10-13 构建）：Dirty Pipe（修复线 5.4.180）与 Dirty COW（CVE-2016-5195）均超出受影响版本。注：厂商 BSP 补丁合入完整性未逐一 diff 验证 |

### 仍未覆盖

| 未覆盖面 | 说明 |
|---|---|
| Native 层内存漏洞 | 未分析 libemode.so 等 vendor 原生库（内存损坏类漏洞，需 PC/调试环境）|

因此"无用户空间 root 路线"的严谨表述为：**在已测试的攻击面范围内未发现可行路线**。