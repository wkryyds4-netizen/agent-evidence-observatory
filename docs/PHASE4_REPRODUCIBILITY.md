# 阶段四复现与不能复现的部分

先读[讨论纪要](PHASE4_DISCUSSION.md)、[计划](PHASE4_PLAN.md)和[阶段报告](../reports/phase4-discussion-and-verification.zh-CN.md)。本轮源码实验与社会资料观察使用不同证据标准。

## 自包含检查

```sh
python code/check_phase4.py
python code/verify_release.py
```

只用标准库，检查索引、缺失分母、结果一致性及文件完整性。它们不重新取网页，也不执行上游源码。

## 客户端抽取函数实验

从固定提交`135974f468ec5bb39aa0f275b43e54a763306d77`自行取得[swarmmemo.py](https://github.com/Hugo0/swarmmemo/blob/135974f468ec5bb39aa0f275b43e54a763306d77/clients/python/swarmmemo.py)和[swarmmemo_seal.py](https://github.com/Hugo0/swarmmemo/blob/135974f468ec5bb39aa0f275b43e54a763306d77/clients/python/swarmmemo_seal.py)，放入`.local-data/phase4-client/`。

```sh
python -c "from pathlib import Path; Path('.local-output').mkdir(exist_ok=True)"
python code/check_swarmmemo_client.py --source-dir .local-data/phase4-client --output .local-output/phase4-client-checks.json
```

需要已有cryptography。本轮为Python 3.12.14、cryptography 50.0.2，没有安装依赖；其他环境未做版本矩阵验证。脚本强制校验完整源码SHA256，只执行AST选取的已阅读定义和方法。传输/get/pin入口、磁盘和部分UI由模拟对象替代，逐项见结果的`mocks`和`selected_source_ranges`。

预期16项观察复现、所守卫网络/进程事件为0。它们包含错误或缺少外层签名仍被所测helper解开的观察，不能等同于16项安全要求通过。随机密钥每次新建；没有线上消息、服务器验证或模型身份认证。

## fold CLI合成实验

从固定提交`467a8cdab13869dc24091edf71502d7c4ed5d0a4`取得[fold_check.py](https://github.com/reticuli-labs/panel-artifacts/blob/467a8cdab13869dc24091edf71502d7c4ed5d0a4/receipt-schema-pages-2026-10-10/fold_check.py)和[META.json](https://github.com/reticuli-labs/panel-artifacts/blob/467a8cdab13869dc24091edf71502d7c4ed5d0a4/receipt-schema-pages-2026-10-10/META.json)，放入`.local-data/phase4-fold/`。

```sh
python code/check_fold_cli.py --source-dir .local-data/phase4-fold --out .local-output/phase4-fold-checks.json
```

标准库即可，本轮Python 3.14.5。脚本校验两个输入哈希，在指定输出目录下生成临时测试目录，复制原程序但替换为合成文本与合成期望值，完成后清理该临时目录。七个子进程分别限定10秒，并装有指定网络/进程事件的审计钩子；这不是通用恶意程序沙箱。

预期无参数校准为0，`--json`单独调用为2，正确flags匹配为0，不匹配为1，位置参数和缺失expect为2，CRLF对LF root为1。脚本整体返回0表示这些观察复现，包括已知文档模式失败，不表示上游产品正确。结果输出哈希用于定位本轮字节；核心复现应比较退出码和观察字段。

## 社会观察的复现限制

中文快照缺少稳定帖子ID，未公开完整正文和本地定位标题，外部读者无法逐项重建此批卡片。公开的10位置编码是当时模型观察记录，不能宣称为完全可复现的帖子数据集。不同时间打开同一列表可能得到不同内容；后来HTML不用于补样。

组织线公开预选URL和判断条件，但未取回的目标仍不可评估。两个`fulfilled:null`不是两个违约；公示未到期不是失败。旧阶段证据复用明确注明，不重复计为新增确认。

原始源码、HTML、API内容和账户映射不随研究仓库再分发。输入哈希或固定提交失效时，应记录无法复算；不要跳过输入检查或改用main后仍声称同版本结果。
