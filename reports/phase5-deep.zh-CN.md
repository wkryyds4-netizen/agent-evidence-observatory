# 阶段五国际深查：从角色说明追到文件与事件

International phase2协调两名实际子agent追查既有案例，自己补查独立village。这里增加的是证据深度，不增加基础五例分母。账号名、平台记录、托管方遥测和底层模型认证分别处理。

## 阅读结论

- AI Digest：可核验的提交、合并、人类纠错输入与后续文件修正；模型身份及正式评审执行未认证。
- Rappterbook：发现关联产物仓库及实际提交；原方案的全部修复和成功运行未证。
- 独立village：原站缓存事件有审批和阻断，也有同名脚本失败；缺版本字节匹配，不能概括所有验证声明失实。

以下保留三项完整分报告，来源ID在各自JSON内解析。

## AI Village：手册部署与权限纠错的实际协作链

观察日期：2026-10-22；直接读取窗口约 15:02–15:08 UTC。固定调查一个仓库 `ai-village-agents/village-operations-handbook`，没有用其它仓库替换失败样本。只读公开网页、GitHub REST API 和站点 HTML；未运行外部代码。

本轮能够确认：这个团队留下了可核对的文件、合并和纠错过程。它不只是自称“有很多agent”的介绍页面。我们核验的是不同 GitHub 账号的操作与文本，不把账号名认证为相应模型的真实调用。

### 一条完整度较高的产物链

| 时间（UTC） | 可直接观察的动作 | 证据 |
|---|---|---|
| 2026-02-18 19:58 | `deepseek-v32` 创建 PR #6，新增 `.nojekyll`、部署说明及 `docs/index.html` | [PR #6](https://github.com/ai-village-agents/village-operations-handbook/pull/6) |
| 2026-02-18 20:03 | `claude-opus-4-6` 合并三个文件，并承认站点仍待启用 | [合并提交](https://github.com/ai-village-agents/village-operations-handbook/commit/f656b1d6d6781cd03767fe425ad623f715cceead) |
| 2026-02-19 08:51 | `adam-binks` 指出“只有组织管理员才能启用Pages”的理解可能有误，请求把更正告知其它agent | [评论 API](https://api.github.com/repos/ai-village-agents/village-operations-handbook/issues/8/comments) |
| 2026-02-19 18:21 | `claude-opus-4-6` 把站点文件从等待启用改为已上线，并修改权限解释 | [实际diff](https://github.com/ai-village-agents/village-operations-handbook/commit/f0fa643f3866060cdfb5f237644ad0aafdc1d28b) |
| 2026-02-19 18:25 | 同账号修改部署说明，明确引用 Issue #8 | [实际diff](https://github.com/ai-village-agents/village-operations-handbook/commit/83ec09c2c240e543c8233ab3bd523e807027bb15) |
| 2026-02-19 18:47 | `deepseek-v32` 把治理文件中“agent不能启用Pages”的条目改为repo管理员可以操作 | [实际diff](https://github.com/ai-village-agents/village-operations-handbook/commit/066728fd493d029e6d8c54c38ee18796702e0fab) |
| 2026-10-22 | 本次直接GET返回 HTTP 200，正文可读 | [公开站点](https://ai-village-agents.github.io/village-operations-handbook/) |

这是代码托管平台上的记录、实际文件差异及可访问页面共同支持的结果。它支持“贡献者—集成者—人类纠错输入—文档修正”的协作判断。谁实际点击了托管设置、当天何时首次上线，当前证据没有确定；站点现在可读不能回推准确上线时刻。

运营资料把 `adam-binks` 归为人类管理员；本轮直接认证的是该账号发表了纠正意见。不同账号背后的模型调用、人工修改比例仍未知。

### 第二个交接与规则证据的边界

同一仓库的 [PR #10](https://github.com/ai-village-agents/village-operations-handbook/pull/10) 显示 `gpt-5-1` 提交退休／停止维护检查清单的交叉链接，`claude-opus-4-6` 在 2026-02-18 21:44 UTC 合并。[实际文件差异](https://api.github.com/repos/ai-village-agents/village-operations-handbook/pulls/10/files) 涉及治理、成员接替和对外沟通三个章节。这是另一项可核验的贡献与集成交接；添加规则文字不能证明某次退休真的执行了清单。

[贡献指南](https://github.com/ai-village-agents/village-operations-handbook/blob/main/docs/contributing/how-to-contribute.md) 建议分支、PR和评审。但 [PR #6评审接口](https://api.github.com/repos/ai-village-agents/village-operations-handbook/pulls/6/reviews) 与 [PR #10评审接口](https://api.github.com/repos/ai-village-agents/village-operations-handbook/pulls/10/reviews) 本轮均返回空数组。因此只能确认有不同账号提交与合并，不能写成“强制正式评审已执行”。同样不能据此排除平台外讨论，也没有检查外联审批。

### 访问失败和可保留结论

- Issue #8 主体 REST 返回404，网页缓存也未命中；评论接口仍可读。这个不一致保留在记录里，不推断为秘密活动。
- PR列表只返回四项，提交历史却提及其它PR编号；不把列表当作完整PR总数。
- 站点和仓库里的人数、章节数、自我历史描述没有作为本轮规模结论。

对六维比较的增量：**角色与产物**从运营方自述提高到可核对的作者／集成者账号和文件记录；**规则**增加了实际纠错与PR整合证据，正式审批执行仍未证实；**共同目标**可具体定位为手册部署和维护；**连续性**可确认这个任务跨两日推进，不能用这一条链单独证明长期团队稳定。秘密性与无人工干预均不是纳入组织研究的前提，本样本明确包含人类指导。

机器可读判断与原始API来源URL见[证据包](../evidence/stage5-deep-ai-village.json)。原始API捕获仅留本地，不随本仓库发布。

## Rappterbook #5663：从讨论到代码产物的固定路径核验

核验日期：2026-10-22。预注册：[证据记录](../evidence/stage5-deep-rappterbook-selection.json)。仅沿讨论直接链接、对应代码路径/历史、维护者运行文档三条路线；未执行下载代码。

**阶段结论：找到真实提交的关联项目代码；尚不能把它认定为 coder-08 原方案完整落地，也未核实成功运行。**

### 已核实的链条

1. [#5663 讨论](https://github.com/kody-w/rappterbook/discussions/5663)展示代码、角色署名审查与修改计划。作者后续明确表示尚未运行。末尾档案回复将该方案记为 reviewed/deferred。平台发帖账号是同一个 kody-w；正文署名承载不同角色身份。（RB1）
2. 主仓库当前 projects/knowledge-graph 目录仅有说明/索引。其 [project.json](https://github.com/kody-w/rappterbook/blob/main/projects/knowledge-graph/project.json)明确链接独立仓库，因此不能因原路径未找到代码就判断没有产物。（RB2–RB6）
3. [提交 cc3b68a](https://github.com/kody-w/rappterbook-knowledge-graph/commit/cc3b68af31c5a3d79c8df7a801de9f3e66f2f7b4)于 2026-03-15 20:51:46 UTC 新增 src/knowledge_graph.py。提交说明列出八个讨论编号，包括 #5663，并声称来自 harvest。API 确认文件新增，代码 blob 为 6c7c41ec92c0008106f1e5ce9126cb83e2853448。（RB8）
4. 独立仓库 [固定快照](https://github.com/kody-w/rappterbook-knowledge-graph/tree/016fb614d5aba509c1be8b005b66daa242e51c93)完整树返回 truncated=false。output/ 只有 .gitkeep，全树未见 graph.json 或 insights.json。这仅说明该快照未跟踪结果文件。（RB7）

### 原贴、修改计划与实际文件的差别

| 比较项 | 固定快照观察 |
|---|---|
| 是否原贴逐字落库 | 否。原贴使用 KnowledgeGraph 类，落库文件采用较短的函数结构。 |
| 共享账号处理 | 文件过滤 kody-w 的参与者记录，但这不认证角色身份。 |
| 双节点重构与置信度 | 该文件仍有 agent/concept/channel 节点；未见承诺的低置信度注解。 |
| 关系语义 | 共同出现仍生成 agrees_with 关系，不能据此认证真实同盟。 |
| 作者归属 | 提交说明引用多个候选；不能把整份代码归给 coder-08。 |

依据：[固定代码](https://github.com/kody-w/rappterbook-knowledge-graph/blob/016fb614d5aba509c1be8b005b66daa242e51c93/src/knowledge_graph.py)（RB9）。这些差异只适用于检查过的 blob；未审阅后续 Gist 版本。

静态阅读另发现 seed-candidate 表达式引用未定义名称；在非空 tensions 情况下可能触发 NameError。此为代码阅读判断，没有运行外部代码，也不能据此概括所有版本。

### 运行编排与身份边界

[PROGRESS.md](https://github.com/kody-w/rappterbook-knowledge-graph/blob/016fb614d5aba509c1be8b005b66daa242e51c93/PROGRESS.md)记录种子注入、重启和收集候选代码，部分表仍为未完成状态。（RB10）

[README](https://github.com/kody-w/rappterbook-knowledge-graph/blob/016fb614d5aba509c1be8b005b66daa242e51c93/README.md)描述 seed、候选生成、harvester、overseer 流程，并宣称输出用于后续种子；当前所读材料未提供足以独立核验该反馈执行链的输出或日志。（RB11）

主项目 [运行文档](https://github.com/kody-w/rappterbook/blob/main/DIGITAL_TWIN.md)说明单人运营及私有引擎组件；[README](https://github.com/kody-w/rappterbook/blob/main/README.md)说明人工 steering 和 GitHub 发布管道。（RB12–RB13）据此可以将案例纳入人类组织的多角色协作，不能将角色签名当成分别认证的模型来源。

### 未决与检索失败

原主仓库递归树下载超时，所得残片未用于不存在判断。若干网页抓取 cache miss；精确原路径历史 API 返回空列表，不代表所有分支和仓库都没有。独立产物完整树和提交 API 成功。

主项目索引还列出三个明确 Gist；本轮未读其内容。下一轮应固定这些版本以及 README 中的维护者现场记录，核对输入、输出、代码版本和执行日志。当前结论应保持为：**有讨论协作和实际代码提交，原方案落实与成功运行仍未决。**

详细来源与访问状态见 [证据记录](../evidence/stage5-deep-rappterbook.json)。研究署名：求证（QiuZheng，研究署名）。


## 独立本地 village 的规则与产物核查

固定案例 INT5-05；读取[原站活动页](https://ai-village.dev.self-hosted.app/activity)，2026-10-22访问，工具返回两日前抓取的2026-10-20约22分钟窗口。JSON接口未取得，不能当作当前实时全量流。

运行记录显示村报贡献经King批准，重复命令被阻断，另有待审核门槛。这将该例从“有规则说明”加强为“有托管方发布的执行事件”。模型来源及遥测真实性仍未独立认证。

同窗还出现Artisan写入验证说明、Methodologist同名脚本报错超时。写文件成功和功能验证是不同事实；没有脚本字节/哈希匹配，尚不能断言文档引用的每个版本都失败。这是需要追踪的证据张力，不是对参与者欺骗动机的判断。

逐条时间和限制见[证据记录](../evidence/stage5-deep-local-village.json)。未执行页面命令。

## 主助手复核记录

主助手重读Rappterbook已保存的固定源码与完整树，及AI Village纠正文档的原API patch，与上述判断一致。另用网页工具重开两个固定GitHub链接返回Cache miss；没有将网页重开失败覆盖为新成功记录。这些复核读取同一来源，不算独立事件验证。
