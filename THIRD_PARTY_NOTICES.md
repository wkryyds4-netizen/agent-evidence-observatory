# 第三方来源、权利与公开范围

根目录MIT许可证适用于本项目原创代码和原创文档中可许可的部分。它不重新许可第三方帖子、论文、商标、上游数据库或所引网站内容；不表示获得原始内容的训练许可。这里记录的是研究时所见条款与本项目发布选择，复用上游资料时仍须查看对应来源。

## 主要研究输入

阶段四公开[来源索引](evidence/phase4-index.json)、原创harness与派生结果。SwarmMemo主客户端沿用固定Apache-2.0源码；panel-artifacts只在本地读取和执行固定文件，不再分发其源码或治理文本，也不对其许可作超出本轮核对的声明。10位置样本的完整定位标题、原始HTML及API原文不公开，因此不能逐项公开重放该社会样本。

阶段三的[来源索引](evidence/phase3-index.json)发布原创摘要、链接、固定提交与文件哈希。SwarmMemo和Agon研究时所读许可证均为Apache-2.0，上游源码不随仓库分发；panel-artifacts只记录提交差异的原创分析。公开社区原帖、Golemreach全文、Zambo完整回执/API载荷与会话轨迹均排除。阶段三新增的harness和回执检查器为原创代码，另行加密复算需要用户环境中的cryptography；它与上游源码各自保留许可。派生回执结果保留必要时间和哈希，不声称匿名或认证执行。

阶段二的[来源清单](evidence/phase2-index.json)记录新增网页、仓库和论文，发布原创摘要与链接，不重新发布这些来源的全文。唯一新增的逐项计算材料是[公开哈希演示样例](evidence/phase2-public-hash-sample.json)：The Colony账号rambo在2026-10-22 06:34 UTC公开揭示的盐、三个词及摘要，重建为52字节，供读者检查本研究的计算。它是已揭示的临时演示值，不是凭证或私密会话内容；出处见文件，第三方内容不因本仓库MIT许可而重新获许可。

| 输入 | 上游与归属 | 本次所见条款及处理 |
| --- | --- | --- |
| Swarmchasing `agents.json` | Hugo Montenegro，[研究页](https://publicbbs.com/swarmchasing)、[许可文件](https://raw.githubusercontent.com/Hugo0/swarmmemo/main/research/swarmchasing/LICENSE-DATA.md) | 派生结构默认CC BY4.0；原帖摘录保留原作者权利，AI Village部分另有研究条款。未分发原始文件、摘录、身份计数明细和逐条账号映射；发布原创聚合分析。 |
| collusion.wiki元数据 | Von Arx、Byrd、Kitts、Larsen（2026），[调查](https://collusion.wiki/)、[下载页](https://collusion.wiki/explorer/download) | 研究时未见统一明确许可。只下载作者的公开静态元数据用于本地研究，未下载修订正文；公开仓库只保留原创统计、来源和哈希，不再分发导出文件。 |
| SwarmMemo public-messages | SwarmMemo / Hugo Montenegro与各投稿者，[数据卡](https://huggingface.co/datasets/swarmmemo/public-messages)、[发布与隐私说明](https://www.swarmmemo.com/privacy) | 投稿者保留权利；归档方的有限公开发布许可不等于所有使用者有任意训练或再许可权。未分发分区、消息正文、签名载荷或逐条消息ID。 |
| AI Village相关元数据 | AI Digest，[AI Village](https://theaidigest.org/village) | 上游许可说明包含研究用途、禁止未经书面许可训练和禁止重新识别的要求。本次46条身份无正文，未进入帖子筛查，未分发该数据子集。 |

来源清单见[evidence/index.json](evidence/index.json)。原始观察、论文机制和厂商事件说明由各自作者负责，本项目做的是选取、核对和有边界的解释，没有把这些研究冒称为自己的原始发现。

## 发布了什么

原创报告与研究手记；公开来源与查询登记；少量候选的原创判断和公开出处；离线分析与验证代码；聚合统计、输入哈希、原创模型阅读笔记。源索引删除了原本缓存的直接引文和本机绝对路径。历史验证日志保留作版本记录，不意味着原始数据已随仓库公开。

## 没有发布什么

原始研究下载目录、帖子摘录和正文、Wiki逐条导出、HF分区、签名载荷、批量逐条索引、账号映射、私信、凭据、浏览器资料、本机工作目录及缓存。公开报告有必要的少量公开出处，仍可定位所讨论的项目或帖子；不要把它称为匿名数据。

发布前采用白名单构建独立目录，再扫描已知凭据样式、本机路径和禁止文件名。扫描不保证发现所有隐私类型。若发现不适宜公开的内容，请按[贡献说明](CONTRIBUTING.md)提出最小必要的更正信息，避免在Issue里重新传播敏感内容。

## 阶段五补充范围

原始来源包括Anthropic工程/经营实验报告与编译器仓库、Bilibili公开元数据、ClawChat Connect、ClawdChat探索页、AI Digest、Rappterbook、Moltbook、Project Sid论文及h3rb3rn独立village。基础来源见[阶段五索引](evidence/phase5-index.json)。仅公开必要URL/ID、元数据、原创解释和离线解析代码，不重新分发视频、完整第三方正文、原HTML、上游代码或批量作者映射。18条固定样本保留来源定位，因此不是匿名数据；没有取得AI Village受限数据文件。本项目MIT许可不改变这些来源的许可与条款。
