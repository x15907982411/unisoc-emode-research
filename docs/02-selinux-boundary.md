# 02 · 引擎模式 SELinux 域边界

引擎模式进程 = `sprd_engineermode_app`（uid 1000 / system 级 app），域隔离策略：

## ✅ 域内可用能力

| 能力 | 说明 |
|---|---|
| `sh -c` 任意命令 | 该域 SELinux 允许的范围内 |
| `setprop` | ctl.* / persist.* / sys.* |
| `am` | 启动任意 Activity |
| `cmd` | 服务 shell 命令 |

### 引号技巧（payload 传递）

payload 内嵌空格/分号/井号时，用 `${IFS}` + 双引号可可靠传递——sh 解析后为单个 argv。

## ❌ 写权限极窄

以下路径全部 SELinux 拒绝写入（引擎模式域）：

```
/data/anr
/cache
/data/system
/data/vendor/ylog
```

> 后果：即使有可执行的 payload（如 HIDL 调用器 dex），**文件无法落地**，攻击链在第一步就断掉。

## ❌ binder 调 system_server 全被封死

实测（全部静默拦截，无输出无效果）：

```
cmd webviewupdate set-webview-implementation <pkg>
cmd role add-role-holder ...
service call VendorLogManagerService ...
```

- emode 持有 `UPDATE_APP_OPS_STATS` / `MANAGE_ROLE_HOLDERS` / `INSTALL_PACKAGES` 等权限全部 granted=true
- 但 **avc 域隔离一票否决**——权限面全绿也没用

## 已复核的死路

| 路线 | 结论 |
|---|---|
| WebView 切换 | ZTE 厂商自签证书，第三方 WebView 签名校验过不了（装了也白搭）|
| 默认安装器替换 | IRoleManager 定制接口 + 厂商锁死，全部静默 Failed |
| WEBVIEW_SETTINGS action | 存在但选完也会被签名校验拒 |

## 结论

引擎模式名义上是 system uid，实际被 SELinux 圈养在极小的能力圈里：
**能执行命令，但写不了文件、调不了特权服务**——两条路都断。