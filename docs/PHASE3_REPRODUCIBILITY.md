# 阶段三复现

本轮把公开网页观察、固定代码静态阅读、实际离线执行分开。网页可能变化；通过代码检查不代表现实事件得到认证。

## 仓库自包含检查

```sh
python -m unittest discover -s tests -v
python code/check_phase3.py
python code/verify_release.py
```

这些命令只需Python标准库，不读取第三方原始资料。阶段三检查验证来源ID、观察链、固定版本、保存结果和报告关键分母的一致性，不重新执行密码学实验。

## 加密实验

使用[来源清单](../evidence/phase3-crypto.json)的固定提交`135974f468ec5bb39aa0f275b43e54a763306d77`，自行保存以下两个文件到`.local-data/swarmmemo/`，保留原文件名：

- [swarmmemo_seal.py](https://github.com/Hugo0/swarmmemo/blob/135974f468ec5bb39aa0f275b43e54a763306d77/clients/python/swarmmemo_seal.py)
- [seal-vector.json](https://github.com/Hugo0/swarmmemo/blob/135974f468ec5bb39aa0f275b43e54a763306d77/clients/python/seal-vector.json)

需要已有`cryptography`依赖的Python环境。本轮实际版本为Python 3.12.14、cryptography 50.0.2；没有安装新依赖，也没有验证其他版本矩阵。harness在导入前强制检查两个输入SHA256，不匹配就退出。上游测试和LICENSE在研究时另行阅读，但不是harness运行输入。

先建立本地输出目录，再运行：

```sh
python -c "from pathlib import Path; Path('.local-output').mkdir(exist_ok=True)"
python code/check_swarmmemo_seal.py --source-dir .local-data/swarmmemo --output .local-output/phase3-crypto-checks.json
```

应得到28项通过。随机往返用例每次重新生成密钥和nonce；两项确定性向量沿用公开固定值。结果文件只保存检查状态与范围，不保存生成的密钥。Python审计钩子阻止列出的socket/进程事件，但不是通用恶意代码沙箱。本轮源码经模型静态阅读，未执行主客户端、后端或浏览器实现。

## 回执检查

自行保存[公开校验端点](https://zambo.dev/api/v2/receipt/e58a8d1e-8bf4-43a7-80a1-57bd98fb139f/verify)的响应到`.local-data/zambo-verify.json`，并运行：

```sh
python code/audit_public_receipt.py --input .local-data/zambo-verify.json --out .local-output/phase3-receipt-checks.json
```

本轮输入SHA256为`5a9d88da25a393a05d21ded97f73a5b85f3ac81f8d14749ef4c564d530bb1d0d`。该端点是动态的；输入哈希不同时，不能声称复现同一快照。脚本使用严格Base64解码，哈希精确字节，不通过JSON重新序列化改变输入；输出排除行动正文、账号及session trail，只保留派生检查与少量时间字段。

预期2040字节、SHA256为`e07f9ffdd29113532e09d76d09c8a5f2420b1bf589a4ac605f4559bd4943fc52`。时间差71.547秒和371.547秒只是字段相减。脚本退出0表示摘要和长度匹配，**不表示执行、时间或身份可信**。无效输入退出2，字节校验不符退出1。签名、元数据哈希、外部锚和执行重放均不在此脚本范围。

## 静态产物核对

[Agon来源](../evidence/phase3-artifacts.json)记录固定提交、文件哈希与读取范围；[fold核对](../evidence/phase3-fold.json)记录GitHub提交差异和祖先关系。两套代码均未执行，不能把静态控制流写成实测。链上查询超时保留为失败，不计确认。

研究仓库不携带完整第三方源码、网页、API载荷或会话轨迹。上游撤回相同字节时，原输入的完整复算可能无法完成；保留哈希不等于保留了可取回的数据。
