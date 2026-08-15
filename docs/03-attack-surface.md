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

## 测试边界（未覆盖攻击面）

本次评估聚焦于 Java/HIDL 层的命令执行与服务调用链，以下攻击面**未纳入测试**，上述结论不构成对这些路线的排除：

| 未覆盖面 | 说明 |
|---|---|
| 动态广播接收器注入 | 仅分析了静态组件，未检查动态注册的 BroadcastReceiver 是否存在 caller 校验缺失 |
| ContentProvider 暴露面 | 未审计 emode 内 Provider 的 query/insert/update/delete（SQL 注入、路径遍历）|
| Intent 重定向 | 未验证内部 startActivityForResult 转发外部 Intent 的逻辑（non-exported 组件调起绕过）|
| Native 层内存漏洞 | 未分析 libemode.so 等 vendor 原生库（内存损坏类漏洞）|
| 内核漏洞复验 | 未复验 Dirty Pipe / Dirty COW 等（Android 13 内核大概率已修补，但未实测排除）|

因此"无用户空间 root 路线"的严谨表述为：**在已测试的 10 类攻击面范围内未发现可行路线**。