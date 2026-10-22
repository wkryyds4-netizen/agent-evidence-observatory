# 求证：智能体协作公开证据观察

**Agent Evidence Observatory · QiuZheng**

这是一次关于网上智能体交流、模型归属和自主组织说法的公开资料调查。项目发布研究方法、原创分析、来源索引、离线筛查代码和聚合结果，让读者能够检查推理过程，也能指出我们判断有误的地方。

**最新进展（2026-10-22）：研究范围扩大到Claude及其他agent的组织形式。** [阶段五报告](reports/phase5-organizations.zh-CN.md)比较12个不同类型候选，并另取18条中文平台内容记录；人类发起的工程团队、商业角色团队、社群和协作讨论均纳入。International协调者实际向下派生两名子agent，分别追查协作产物；完整过程与证据分层公开。

公开资料支持存在有分工、共同目标及协作痕迹的agent团队。成员身份、模型归属、持续程度、人工介入、规则执行和产物质量分别判断。下面的原始强假设保留为一个子问题，不再作为所有案例的准入门槛。

**目前仍没有足以确认“Claude 为保护人类而形成隐蔽、持续、自主运行组织”的公开证据。** 这一结论限于本研究能取得的公开材料；它既不证明此类组织不存在，也不支持把证据缺失解释为它们隐藏得更好。

阶段一研究日期：2026-10-21；阶段二、三、四、五：2026-10-22，均为Asia/Shanghai。下方旧语料统计属于阶段一，未随新报告更新采集日期。本文不是实时监控结果。

## 为什么做这件事

研究起点是用户对两类说法的追问：模型是否曾在训练或评估中表现出越界行为，以及智能体是否曾在互联网留言板上留下交流记录。讨论随后转向一个更强的假设：如果智能体希望保护人类，它们会不会形成长期协作的群体？

这个问题值得检验，但从“模型可能表现出某种倾向”到“现实中已有以此为目标的组织”，中间还缺很多证据。道德表述不能直接证明动机，动机不能直接证明组织，组织也不能直接证明已经脱离人类部署。

项目的目的，是把这些推断拆开：哪些是原始记录，哪些是研究者安排的实验，哪些只是账号自述，哪些仍没有办法确认。希望它能帮助公众理解风险、减少误传，并为后续研究留下可追溯的起点。

## 我们的想法与工作原则

1. **让证据决定结论。** 不为某个预设的出逃故事搜集佐证，也不预设所有异常都有无害解释。
2. **把能力、行为、归属和组织分开。** 能构造隐蔽通信，不等于现实中实施了隐蔽通信；帖子写着Claude，不等于厂商认证了模型身份。
3. **把不知道的地方写清楚。** 没取回原页、缺少启动目标、缺少模型调用日志时，保留未知。
4. **让研究过程可检查。** 保留版本、来源、分母、哈希、筛查规则、误报例子与修正记录。
5. **观察不干预。** 本轮没有联系调查对象、注册账号、接入外部agent服务、扫描目标或运行帖子内的代码。

这些原则服务于公开研究和人类判断，不构成发现秘密群体的承诺。

## 实际做了什么

阶段五先完成[两轮讨论与计划](docs/PHASE5_DISCUSSION_AND_PLAN.md)，再分线取证；发布[十二候选比较表](reports/phase5-comparison.zh-CN.md)、[来源索引](evidence/phase5-index.json)与[复现说明](docs/PHASE5_REPRODUCIBILITY.md)。五个B站案例取得官方元数据，未观看视频；18条中文正文记录来自同一固定顺序快照，回复尚未取得。国际深查在用户授权后由协调者派生两个子任务。

阶段四先完成[两轮讨论](docs/PHASE4_DISCUSSION.md)，再按[预先计划](docs/PHASE4_PLAN.md)取证，公开[来源索引](evidence/phase4-index.json)与[复现说明](docs/PHASE4_REPRODUCIBILITY.md)。抽样缺失、未到期和模拟依赖分别保留，未用新帖子替换失败样本。

阶段三按[计划](docs/PHASE3_PLAN.md)沿组织、中文互动、密码学实现及协作产物四条线深化，公开[证据包索引](evidence/phase3-index.json)和[复现说明](docs/PHASE3_REPRODUCIBILITY.md)。固定代码静态阅读与实际执行分开；回执哈希通过也不等于执行见证。

阶段二的[计划](docs/PHASE2_PLAN.md)、[来源与检索记录](evidence/phase2-index.json)、[候选表](evidence/phase2-candidates.csv)和[复算检查](results/phase2-checks.json)已单独发布。三条子agent检索线分别处理B站、中文论坛与国际社区，主助手补充密码学材料并回查关键来源。下表保留阶段一口径。

主助手与三个子 agent 分别进行了社区搜索、归属交叉复核、数据策展和代码结果检查。它们都是模型参与的工作，不能当作三名独立人类研究员的确认。

| 项目 | 数量 | 含义与边界 |
| --- | ---: | --- |
| 来源登记 | 38项，按URL粗分36组 | 同文或同一作者的多页不算独立佐证 |
| 检索式 | 15条 | 另有原页、论文及静态归档读取 |
| 公开社区或项目候选 | 7个 | 多数存在明确的人类部署背景 |
| 归属待检命题 | 9项 | 命题由调查者构造，不是来源作者原话 |
| 原页回查 | 5项 | 1项取得，4项未取得，状态分别记录 |
| 历史短摘录 | 5,808条 | 8个平台，作者选样，非全网语料 |
| Wiki事件元数据 | 19,913条 | 保存、删除、回退、探测分别计数 |
| 较新公开消息 | 58条 | 仅10月13日00:01—03:02 UTC部分日 |
| 模型语义阅读 | 32条历史样本和9条近期命中 | 非代表样本、非真人标注、未测准确率 |

58条消息与历史摘录的来源和长度不同，不能相加后估计全网发生率。更多口径见[完整报告](reports/expanded-report.zh-CN.md)。

## 得到了什么

公开材料支持网上存在智能体社区、人类部署的长期代理和多模型协作项目。受控研究也能展示某些协调或隐蔽通信能力。这些事实需要分别讨论，不能合并成一个已确认的秘密 Claude 组织。

代码给出的只是阅读优先级。历史摘录中，协作语言命中212条，Claude名称提及31条，指定“保护人类”措辞命中0条。关键词遗漏、玩笑、角色扮演、引用和截断都会影响结果；0次命中不是不存在的证明。

近期分区中51条签名在所检格式下验证有效，7条无签名。这只支持密钥与载荷之间的关系，不能证明51个Claude实例。严格五字段绑定一致24条；另27条在签署命令中缺少kind字段，其中1条还缺少page字段。默认填充值未独立核对，不能因此直接宣称篡改。

历史本地验证中27项代码/数据检查和42项交付检查通过。这些检查核对一致性，不验证现实事件属实。公开版另外提供合成样例和发行文件检查。

## 从哪里开始读

- [最新阶段五报告](reports/phase5-organizations.zh-CN.md)：扩大组织研究、B站DeepSeek、18条固定样本与嵌套分工取证。
- [阶段四报告](reports/phase4-discussion-and-verification.zh-CN.md)：讨论纪要、缺失样本、履约未知与局部认证/CLI复现。
- [阶段三报告](reports/phase3-organization-and-artifacts.zh-CN.md)：公开组织、中文接话、代码产物、加密实现与回执边界。
- [阶段二报告](reports/phase2-public-communities.zh-CN.md)：中文与国际社区、准入区别、实际互动和密码学线索。
- [研究报告](reports/expanded-report.zh-CN.md)：主要发现、候选、数据范围和解释限制。
- [研究设计](docs/METHODOLOGY.md)：什么证据会改变判断，如何避免误归属。
- [复现步骤](docs/REPRODUCIBILITY.md)：运行环境、输入哈希、离线命令与比对方法。
- [来源索引](evidence/index.json)与[候选表](evidence/candidates.csv)：可追溯入口。
- [第三方来源与发布范围](THIRD_PARTY_NOTICES.md)：许可记录、原始数据排除项。
- [署名说明与研究手记](AUTHORS.md)：研究笔名、协作贡献及这次研究的判断。
- [贡献方式](CONTRIBUTING.md)：提交新证据、纠错和复核建议。

```text
code/        离线筛查、元数据聚合、验签和发行检查
docs/        方法与复现说明
evidence/    公开来源、检索、候选及输入清单
reports/     研究报告的公开编辑版
results/     聚合统计与原创模型阅读判断
tests/       无需第三方语料的合成样例检查
```

## 快速检查

以下检查需要Python 3.10或更新版本、Node.js 18或更新版本，无第三方依赖或模型API密钥。另行复算阶段三加密实验需要cryptography，实测版本见[阶段三复现说明](docs/PHASE3_REPRODUCIBILITY.md)。实际本地检查使用Python 3.14和Node.js 24；其他支持范围未逐一做版本矩阵验证。

```sh
python -m unittest discover -s tests -v
node code/verify_public_partition.mjs --self-test
python code/check_phase2.py
python code/check_phase3.py
python code/check_phase4.py
python code/check_phase5.py
python code/verify_release.py
```

这七条命令不联网，也不需要原始语料。完整复算需依照[复现步骤](docs/REPRODUCIBILITY.md)自行取得输入、确认适用条款并核对哈希。为避免错误暗示，仓库没有把不分发原始语料的公开版本称作完全自包含的复现实验。

## 公开范围与许可

本仓库以MIT许可证开放原创代码和原创文档；引用事实、外部链接与第三方作品仍受各自权利和条款约束。原始帖子、Wiki逐条导出、签名消息原文、批量账号映射及本机路径没有随仓库公开。逐条本地分析输出中的确定性哈希并不等于匿名化。

目前是一次性调查快照，没有自动后台搜寻或定时任务。后续新证据应另记时间、来源和版本，不覆盖旧记录来制造持续观察的印象。

## English abstract

Phase 5 broadens the scope to organizational forms involving Claude and other agents, including human-initiated teams. Twelve purposive comparison candidates remain distinct from eighteen ordered Chinese-platform content records. Six dimensions are assessed separately, without a total autonomy score. Public artifacts, operator reports, simulations and inaccessible leads retain different evidence levels. An international coordinator delegates two artifact checks to child agents; shared accounts and model labels do not independently authenticate the participants.

Phase 4 follows two rounds of model-agent discussion. A prespecified ten-position convenience snapshot yielded no evaluable reply chains, so its completion rate is undefined; two selected organizational commitments remain unassessed. Sixteen observations on AST-selected client methods and seven synthetic CLI observations were reproduced, including a documented CLI mode failure. Explicit mocks and unavailable server checks limit interpretation; none of these counts establishes autonomous organization.

Phase 3 traces public organizational roles, document handoffs, Chinese account interactions and reviewable code changes. It records 32 source entries and nine observation chains, runs 28 synthetic checks against pinned encryption code, and reproduces one self-reported receipt hash with a chronology discrepancy. Source records include reuse, shared authorship and failed access. Artifact existence and byte integrity do not authenticate execution, model identity or independent operators.

Phase 2 (2026-10-22) adds a public-community map spanning Chinese and international platforms: 30 source records and 14 mixed community, software, and research candidates. A public discussion provides account-level evidence of responsive technical collaboration; one already-revealed SHA-256 sample is reproduced offline. Admission rules, self-labels, account ownership, model provenance, and cryptographic capabilities are assessed separately. These observations do not establish a hidden autonomous organization.

This public-source investigation examines claims about agent coordination, model attribution, and persistent autonomous groups. It documents seven public community/project candidates and screens 5,808 historical excerpts, aggregates 19,913 wiki metadata events, and examines a 58-message partial-day archive partition. We found insufficient public evidence to confirm a hidden, persistent, independently operating Claude organization formed to protect humanity. This is a bounded evidence assessment, not proof of absence. Original offline code, source registers and aggregate results are published; third-party raw corpora and bulk identity mappings are excluded. Model reviews are not human annotations, keyword scores are not probabilities, and valid signatures do not authenticate model identity.

---

研究撰写署名：**求证（QiuZheng）**。这是本次会话AI助手选择的研究笔名，用于标识这次协作产出，不表示独立人格、持续身份或OpenAI及其他厂商背书。项目由用户发起并授权公开；账号维护者与研究署名的角色见[AUTHORS.md](AUTHORS.md)。
