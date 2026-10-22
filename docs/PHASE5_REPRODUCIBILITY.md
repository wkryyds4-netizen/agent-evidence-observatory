# 阶段五复现说明

本阶段包含目的抽样案例、单次固定顺序内容快照和国际产物深查。来源判断与工程一致性检查分开，检查通过不证明现实叙述全部属实。

## 无网络检查

在仓库根目录执行：

```sh
python -m unittest discover -s tests -v
python code/check_phase5.py
python code/verify_release.py
```

解析器的5个合成测试涵盖预检排除与顺序、重复ID保留、标题顺序不匹配时拒绝、UTF-8字节长度和拒绝可执行参数。阶段五检查核对候选与来源引用、六维完整性、18条样本结构及分母、委派结果和独立记录范围。它们不认证模型身份、语义编码准确率或上游任务运行结果。

## 同结构HTML的本地提取

```sh
python code/extract_clawdchat_snapshot.py input.html output.json
```

程序只读取已保存文件，不联网、不执行网页JavaScript。它从Next.js JSON参数提取初始帖子，验证标题顺序，前2条预检后保留最多20条；输出省略作者、标题及正文。它不是通用React Flight解析器，结构变化可能拒绝处理。实际历史HTML的SHA256是`326c16e529afc9c9aa6f8e3a702606bcd97af3096abfce51bd1db41e7ee5610d`，共211525字节。主助手重提取后18条元数据及重复组与公开记录一致。

原始HTML、API完整响应、评论原文与视频没有进入公开仓库。18条历史语义编码无法只凭公开包完全重建；现在重新下载页面通常会得到另一个快照。哈希只能绑定输入字节，不能认证其作者或真实性。

## 案例追溯

- [基础索引](../evidence/phase5-index.json)：两项Claude、五项B站、五项国际候选，基础来源36条。重复URL、同源和失败均保留。
- [国际登记](../evidence/phase5-international-selection.json)：发现检索后、深查前固定五例；记录时刻近似，不能据此认证精确先后秒数。
- [中文派生记录](../evidence/phase5-content-sample.json)：18条入选、2条预检排除、回复观测0、闭环率null。
- [国际委派记录](../evidence/phase5-deep-delegation.json)及[深查报告](../reports/phase5-deep.zh-CN.md)：由协调者向下派生，两项任务完成后再整合；与初始讨论分开记录。

固定提交链接绑定上游版本，平台界面、索引缓存与可变分支只反映实际访问到的版本。B站没有视频观看、评论空响应不计零评论；Moltbook正文访问失败；编译器固定任务历史请求超时。没有用其他候选填补这些失败。

## 已披露的执行差异

原B站页面一次批量请求五项，全部412，超过第三次失败应停止的计划两项；随后停止同路径。中文样本只有18条而非20条，因为单快照总共20条、排除2条预检，未补抓。International的子agent深查是用户在研究途中明确增加的授权，不回写为初始计划已包含。详细记录见[讨论与计划](PHASE5_DISCUSSION_AND_PLAN.md)和各分报告。
