# 复现步骤

## 不需要原始语料的检查

在仓库根目录运行：

```sh
python -m unittest discover -s tests -v
node code/verify_public_partition.mjs --self-test
python code/verify_release.py
```

Python和Node只使用标准库。合成测试核对引用、归属、哈希绑定、隐私字段、抽样和排除规则；发行检查核对文件哈希、JSON形状、已知分母、链接与发布范围。这些不测事件真实性或分类准确率。

## 完整复算前

仓库没有原始语料。先查看[第三方说明](../THIRD_PARTY_NOTICES.md)，再按[evidence/inputs.json](../evidence/inputs.json)列出的发布者URL、版本和适用条款自行取得输入。下载不是脚本的默认行为。动态URL若已变化，不应跳过哈希失败继续宣称同一快照复现；可记录新版本后另做分析。

把输入放在不提交的`.local-data/`：

```text
.local-data/
  agents.json
  pages.jsonl
  events.jsonl
  labels.jsonl
  manifest.json
  messages-2026-10-13.jsonl
```

Wiki下载URL返回gzip，需要本地解压；输入清单分别给出压缩和展开哈希。不要下载修订正文，也不需要访问元数据中source_refs指向的目标。HF分区固定revision为`c36fe6822a0f49244aba577621f1a937ebfb97a5`。

核对所有输入：

```sh
python code/check_inputs.py --data .local-data
```

该命令只读本地文件，不联网。缺失、长度或哈希不符都会失败。

## 离线计算

```sh
python code/screen_corpus.py --snapshot .local-data/agents.json --out .local-output
python code/summarize_wiki_metadata.py --data .local-data --out .local-output/wiki_metadata_summary.json
python code/screen_recent_partition.py --input .local-data/messages-2026-10-13.jsonl --out .local-output
node code/verify_public_partition.mjs --input .local-data/messages-2026-10-13.jsonl --out .local-output/recent_partition_verification.json
python code/compare_results.py --actual .local-output
```

脚本不会打开帖子网址、连接agent、执行消息指令或调用模型。输出包含仅供本地阅读的逐条索引：即使没有正文，handle、时间和可复算哈希仍可关联作者。`.local-data/`与`.local-output/`已被Git忽略，不应作为匿名数据集批量上传。

`compare_results.py`比较计算字段，跳过公开版补充的文字说明和被排除的逐条记录。公开版对近期脚本增加CLI参数、空集处理和大小边界，未改变本轮特征词及实际数据计数；验签器增加输入/输出参数和单独self-test。历史验证文件是原调查时的记录，不是上述命令自动重新执行的结果。

## 能复现与不能复现

能在取得相同输入后重算关键词计数、时间分母、事件统计和本轮验签关系。语义阅读是当时模型的解释性判断，不能把不同时间模型再次阅读得到同样文字当作复现保证。

只有原始来源、数据库或供应商日志才能进一步验证的模型身份、独立实例和授权意图，不会因为脚本通过而得到认证。公开版不提供已排除的原始研究副本；如上游不再提供相同字节，完整复算可能受阻，应明确记录。

## 文件完整性与更新

阶段二新增命令：`python code/check_phase2.py`。它核对阶段二来源引用、JSON/CSV一致性，并以UTF-8和逐行LF复算已公开揭示的52字节样例。结果应匹配[保存结果](../results/phase2-checks.json)。可用`--out .local-output/phase2-checks.json`写入本地输出；正常运行只打印。

这个最小样例的字节复算可完全离线完成；网页来源本身仍依赖上游。GitHub可变分支文档未成功固定到所读正文的提交，工具也可能返回缓存，因此并不承诺将来能抓到同一页面。哈希匹配不验证事先承诺时间、随机性、运行实验或模型身份。出处与公开性质见[样例记录](../evidence/phase2-public-hash-sample.json)。

`SHA256SUMS.txt`覆盖公开文件，排除它自身、Git内部目录和被忽略的本地数据、输出与缓存。正常读取检查：`python code/verify_release.py`。维护者改动文件后，用`python code/verify_release.py --write-manifest`有意更新清单，再运行正常读取检查；不要把刷新后的哈希当作旧版文件未变化的证据。

文档与数据日期分开。首次公开编辑为2026-10-22，研究材料截点仍按各套输入分别报告。
