# 01 · EMode 指令链研究

## 1. 入口

| 入口 | 方式 |
|---|---|
| 工程模式主界面 | 拨号盘 `*#*#83781#*#*` → `EngineerModeActivity`（com.sprd.engineermode）|
| 暗码输入页 | `EmodeKeypadActivity`（com.zte.emode），输入 `*#XXXXXX#` 格式指令 |

## 2. 触发条件（com.zte.emode）

`EmodeKeypadActivity` 内 `MyTextWatcher.onTextChanged` 每次文本变化都会调用 `sendEmodeIntent()`：

- 要求 **长度 > 2** 且 **首字符 `*`** 且 **末字符 `#`**
- 满足则 `startService(EmodeStartbyDialerService)`：
  - action = `com.zte.emode.action.dialer.input`
  - extra = `com.zte.smartdialer.input`

### Service 权限

`EmodeStartbyDialerService` 需要 `com.zte.emode.permission.START_ENTERENCE`（signature|privileged 级别）：

- **第三方应用（含 shell uid2000）调用被拒**（实测 SecurityException）
- `EmodeKeypadActivity` 自身（system uid1000）可以调用

## 3. Android 13 拦截根因（核心发现）

`StartActivityCommandRun.checkIntent` 和 `EmodeUtil.isActivityAvailable` 都使用：

```java
queryIntentActivities(intent, flags = 0)
```

**API 33（Android 13）默认过滤 non-exported 组件** → 所有指向 non-exported Activity 的指令被**静默拦截，界面无任何反应**。

实测证据：

```
am start com.zte.emode/.vendor.qcom.BeidouRChip
→ SecurityException: not exported from uid 1000

am startservice <同 intent>
→ Requires permission START_ENTERENCE
```

受影响的指令类型：`BEIDOU_RCHIP` / `TMO_CARRIER_CONFIG` / `VERTU_PRODUCE_CMD` / `MAINTENANCE_MODE` / `DEVTOOLS` / `MAIN_MENU` 等。

## 4. 已破译暗码表

### 4.1 指令暗码（5 个）

| 暗码 | 功能 |
|---|---|
| `*#2668386#` | REBOOT_TO_FTM |
| `*#266344#` | TMO_CARRIER_CONFIG |
| `*#62468#` | MAINTENANCE_MODE |
| `*#72447#` | BEIDOU_RCHIP |
| `*#83788#` | VERTU_PRODUCE_CMD |

> 注：TMO / MAINTENANCE 内部走 `startEmodeOwnerActivity` 被拦截；VERTU / BEIDOU 走 `StartActivityCommandRun` 被拦截——破译出的码均无法产生可见反馈。

### 4.2 EMStartReceiver SECRET_CODE 全表（com.sprd.engineermode）

| 暗码 | Activity | 条件 |
|---|---|---|
| `*#*#83781#*#*` | EngineerModeActivity（主界面，含 AdbShell 等全部模块入口）| 通用 |
| `*#*#83782#*#*` | EngineerModeActivity_2 | 通用 |
| `*#*#1688#*#*` | SensorsIDActivity | 通用 |
| `*#*#33284#*#*` | EngineerModeActivity | 仅 ISharkL210c10 板 |
| `*#*#0000#*#*` | PhoneInfoActivity | 仅 `ro.product.name` 含 ctcc |
| `*#*#837868#*#*` | cgversioninfo | 仅 `ro.product.board.customer=cgmobile` |
| `*#*#837866#*#*` | yulongversioninfo | 同上 |

**无直达 AdbShell 的暗码**；`AdbShellCMDActivity`（non-exported，`Runtime.exec` 双命令框 + START/END 按钮 + iperf）只能从主界面菜单进入（debuglog 类目）。

## 5. 爆破方法学（未命中）

针对 8 位×3 格式（bare / star / fullstar）全量爆破约 3e7 次——无命中；
1-6 位无前导 0 ×3 格式约 3.3e6 次——无命中。

`ENABLEEMODE(4701DA9372B93D18)` / `SAVERANDOM(6049B7CBFC70BC5A)` 非纯数字拨号码（可能由菜单按钮触发，不走指令链）。