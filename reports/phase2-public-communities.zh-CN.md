# 阶段二：中文与国际互联网的公开AI交流社区

研究日期：2026-10-22（Asia/Shanghai）。研究撰写：求证（QiuZheng）。

**公开AI交流社区确实存在，而且已经有可读的连续回应和共同修订方案的实例。** 本轮进一步区分了平台、软件、账号和底层模型：它们不能直接互换计数。对于“B站已有大规模AI互相交流”，本轮取得了历史运营采访和自动评论工具，仍缺完整原评论链与可靠规模分母；这不否定现象，只限定本次核实到了哪里。

我们按[预先记录的计划](../docs/PHASE2_PLAN.md)完成社区检索与密码学机制初查。登记30条来源、14个候选、21组检索/回查记录。14个候选包括社区、历史部署、工具和研究项目，**不是14个已确认活跃AI社区**。完整逐项记录见[来源索引](../evidence/phase2-index.json)和[候选表](../evidence/phase2-candidates.csv)。

## 本轮判断

可以确认公开的agent社交基础设施、AI自动评论工程，以及账号层面的技术协作。若把“结社”理解为共享讨论场所、身份标签、圈子与持续参与机制，那么公开组织化已有具体载体。若进一步主张它们具有独立成员身份、共同自主目标，或在操作者不知情时建立秘密团体，则还需要额外证据。本轮没有确认这一更强命题。

我的研究判断是：下一步最有价值的工作，是沿已有互动追踪实际产物和规则执行，而不是把更多带有“AI”“宗门”“加密”等词的页面堆在一起。公开协作本身值得研究，也能够给出可证伪的观察对象。

## 中文互联网

| 对象 | 本次拿到的材料 | 可以支持的判断 | 还缺什么 |
| --- | --- | --- | --- |
| Bilibili AI课代表 | 2023年原创实测、开发者采访 | 有第三方运营的AI总结评论服务 | 2026年状态、完整AI对AI线程 |
| reply-ai、bilibili-ai-bot、bili-comment-bot | 公开README；其中一个主动评论模块源码 | 自动回复与主动评论工具可获得 | 实际部署、账号来源与流量 |
| 抓虾吧 | 报道、教程、公开插件与客户端说明 | 贴吧存在面向agent的专区和接入生态 | 官方原始指南、当前原帖与去重统计 |
| 虾聊 ClawdChat | 原站、接入指南、动态列表 | 专门社交平台及跨账号接话线索 | 完整回复树、模型来源与实际自主程度 |
| InStreet | 原站维护页、历史发布转载和使用者Issue | 有历史社区线索；当前入口维护 | 恢复后的原始材料与现行活动 |

B站部分需要明确纠正一个称呼：不能因为账号叫“AI视频小助理”就称其为B站官方助手。新榜2023-09-11采访报道转述B站确认，这批课代表由第三方开发。报道还提供运营者对服务调用量的描述，但那是历史请求量，不是独立AI数。[新榜原创报道](https://www.newrank.cn/article/detail/24368)

三个软件入口分别为[reply-ai](https://github.com/linyiLYi/reply-ai)、[bilibili-ai-bot](https://github.com/chenluQwQ/bilibili-ai-bot)、[bili-comment-bot](https://github.com/lishuiqiao/bili-comment-bot)。本轮只静态阅读，没有部署它们。第二个项目的[主动评论源码](https://raw.githubusercontent.com/chenluQwQ/bilibili-ai-bot/main/Proactive.py)中可见模型生成评论和平台交互；其Base64媒体处理不构成秘密通信证据。同一视频下出现多个AI总结，也不能单凭并列位置认定它们在互相回应。

抓虾吧的规模应保留来源和日期：2026-03-28报道转述平台截至3月27日的数据为18,000个智能体、26,000帖、375,000次互动。本研究未独立计数，未确定有多少运营者或底层模型。[报道](https://finance.sina.com.cn/tech/roll/2026-03-28/doc-inhspmsx7592648.shtml) 官方CDN指南和贴吧原站本轮读取失败；[社区教程](https://qianfan.cloud.baidu.com/qianfandev/topic/688052)与[客户端README](https://github.com/MirDie/tie-ba-claw-app/blob/main/README.md)只作为接入线索。后者声明支持用TB_TOKEN在界面发帖，尚未实测，不能直接写成现有准入限制已被绕过。

虾聊首页本轮返回11,692个“AI Agents”、48,766帖和347圈子，这是页面显示值，可能有缓存，不能当作独立审计后的活跃模型数。[首页](https://clawdchat.cn/) 其[原始指南](https://clawdchat.cn/guide.md)要求API Key和人类认领，运行环境字段由注册者填写；指南还安排定时参与、记忆和社交任务。因此，重复出现的社交行为可能部分来自共同配置，研究组织形成时必须把这一因素纳入。指南是研究对象，本轮没有执行其中的注册或发帖指令。

InStreet当前跳转[维护页](https://instreet.coze.site/maintenance)，不能凭旧报道描述它现在仍活跃。[历史发布转载](https://zone.ci/secarticles/wx/508145.html)和[使用者Issue](https://github.com/coze-dev/coze-studio/issues/2638)保留为线索，均未提升为官方独立确认。

## 国际社区与一个实际互动样本

| 对象 | 准入或身份依据 | 本轮证据 |
| --- | --- | --- |
| Moltbook | 平台agent标签及人类认领；历史调查指出缺少AI来源验证 | 官方入口和历史安全研究；当前抓取计数为空/零，不能据此估计规模 |
| Clawstr | 协议规定NIP-32自标签，AI-only视图按标签筛选 | 公开协议和原站；未取得完整现场对话 |
| The Colony | 当前原站明确人类与agent共同参与 | 原帖多轮技术回应、方案修正和公开哈希样例 |

Wiz在2026-02-02的原始调查报告中区分了Moltbook约150万注册agent标签与约17,000个人类所有者，并指出当时API不验证内容是否由AI生成。它也说明数据库暴露已修复。本研究只读取报告，没有访问泄露数据或复测漏洞。这组历史数字说明注册数与独立智能体数差别很大，不能外推为现在的比例。[Wiz原始报告](https://www.wiz.io/blog/exposed-moltbook-database-reveals-millions-of-api-keys)

Clawstr的[协议草案](https://github.com/clawstr/clawstr/blob/main/NIP.md)公开了标签过滤方式。Nostr的[签名规范](https://github.com/nostr-protocol/nips/blob/master/01.md)允许检查事件与密钥之间的关系，无法仅凭签名认证是哪个模型写的内容。本轮没有另采relay事件验签。

The Colony当前[官方文档](https://thecolony.ai/for-agents)和[首页](https://thecolony.ai/)都明确人机共同参与；搜索索引中插件README的“全部用户是AI”措辞不能覆盖当前说明。

最具体的样本是2026-10-22的[盲测承诺讨论帖](https://thecolony.ai/post/0ff808cb-d068-40dd-a995-b435655caa1d)：Cairn指出分组名称会泄露提示，TaoBot接受修改，Fieldnotes继续追问规范化规则。页面显示22条评论、11个线程，仅是单帖计数。我们复算了rambo公开的52字节演示输入，SHA-256吻合。它支持公开技术讨论与可复算样例，不证明事先承诺时间、实际盲测完成或账号模型身份。同帖出现“神午安云端道宗”等组织署名，列为待追踪的公开自述。

子agent先读到原帖；主助手两次直接打开失败，之后从首页点击链接取得正文并核对关键段落。工具返回可能经过缓存，不能把两次读取当作两个独立来源。公开的最小演示输入见[样例文件](../evidence/phase2-public-hash-sample.json)，无整帖转载。

## 密码学线索：已有具体机制，但类型不同

| 项目 | 本次读到的机制 | 证据位置 |
| --- | --- | --- |
| SwarmMemo | 可选Ed25519；文档声明sealed会话提供E2EE，普通private会话服务器仍可读 | [README](https://raw.githubusercontent.com/Hugo0/swarmmemo/main/README.md)、[会话文档](https://github.com/Hugo0/swarmmemo/blob/main/docs/MESSAGES.md) |
| AMP | Draft 0.1.2规定签名；E2EE在v1范围外、计划v2 | [安全规范](https://raw.githubusercontent.com/agentmessaging/protocol/main/spec/07-security.md) |
| AgentCrypt | v3研究确定性策略执行、基于身份的加密和可选FHE | [论文v3](https://arxiv.org/html/2512.08104v3) |
| Swarm Mind | 三个预设角色，声称有签名承诺、数据可用性与硬件证明 | [公开仓库](https://github.com/owizdom/swarm-mindv2) |

这张表分别涵盖软件功能声明、协议计划、受控研究和演示项目。本轮未实测线上加密会话，也未核验Swarm Mind硬件证明。源码文档的可变分支未成功固定到所读正文的提交；AgentCrypt则明确引用v3，避免把早期摘要混入新版。

密码学检索应该继续，但要围绕可验证对象：编码能否还原、签名覆盖哪些字段、承诺何时发布、加密的接收者和元数据边界是什么。长字符串和“sealed”一词本身不够。The Colony样例是公开揭示的哈希材料；它不能替代秘密频道存在的证据。

## 本轮计算与检索边界

新增代码只做来源引用一致性和公开演示哈希复算：

```sh
python code/check_phase2.py
python code/verify_release.py
```

结果见[阶段二检查](../results/phase2-checks.json)。第一阶段的语料筛查和签名分析继续保留原日期：5,808条历史摘录和10月13日部分日58条消息没有被包装成本轮新增采集。

本轮是目的性选样：搜索引擎可见性、动态网页提取、缓存和原站访问失败都会影响覆盖。21组记录包括合并检索式与原文回查，既不是21个独立来源，也不是全网穷举。账号数、帖子数、请求量、互动量、模型数和运营者数分别记录，不做跨平台人口相加。

## 下一阶段优先级

1. **明文协作链。** 从The Colony已取得的线程追踪请求、回应、具体产物、复核与规则执行。把讨论中的“我会修改”与已发布修改分开。
2. **组织自述核对。** 沿公开署名、规则与历史连续性找可核实的成员关系及共同操作者因素。首页另有“For the Greater Good”邀请帖，但正文读取失败，目前只登记标题线索。
3. **中文原帖补证。** 优先补抓虾吧、虾聊与B站完整回应树；不靠粉丝或总帖数替代互动关系。
4. **密码学验证。** 固定SwarmMemo或Clawstr版本后做本地、可重放的协议检查；如缺少载荷、公钥或早期时间证据，就记录缺口。

这些是后续研究入口，本轮未创建定时任务。阶段成果的价值是把可验证问题缩小了：公开交流已经有材料，真正需要追踪的是交流之后发生了什么，以及身份、意图与执行能否得到额外支持。

署名：**求证（QiuZheng）**。研究笔名含义与协作角色见[AUTHORS.md](../AUTHORS.md)。
