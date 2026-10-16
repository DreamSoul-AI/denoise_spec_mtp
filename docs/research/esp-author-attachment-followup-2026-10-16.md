# ESP作者仓库、commit与OpenReview附件追踪

当前状态：本轮只读追踪仍未取得可运行的作者repo/commit/原生入口，官方GPU步骤未启动。
新证据：作者`index.html`固定commit仍为`039d875e79ee55a032f2f7ba6c58651825cdc0f0`；三个作者/组织论文号代码查询各0项，论坛ID全局6个命中逐项仅识别为元数据/索引/第三方记录。
出处：[15个响应与SHA审计](esp-author-attachment-followup-2026-10-16.json)，本轮完成时间`2026-10-16T00:13:18.240486+00:00`。
执行：候选OpenReview附件均403，未下载到ZIP/PDF；没有加载模型、改prompt、占GPU或另造方法。
下一步：取得可核验作者代码/附件后依[官方启动清单](esp-official-launch-readiness-2026-10-16.md)核来源及实时准入；不需要重复授权。

## 本轮具体追踪

| 路径 | 实际结果 | 可确认与不能确认 |
| --- | --- | --- |
| 作者/Qualcomm/Qualcomm-AI-research中精确论文号代码搜索 | 各0项；查询与返回文件列表固定于审计 | 不是全库逐文件或所有命名方案搜索，不证明作者未发布 |
| 作者主页`index.html`最新commit API | `039d875e79ee55a032f2f7ba6c58651825cdc0f0`，与此前固定主页版本一致 | 这是主页版本，不是ESP实现commit |
| [出版元数据固定版本](https://github.com/mlresearch/v306/blob/ab6608542944f3f67f87c13385f959d442abc920/_posts/2026-09-29-goel26a.md) | 正式OpenReview ID与PDF；`extras: []` | 该文件未给代码下载；不扩大成整个出版仓库没有其他文件 |
| 论坛ID全局代码搜索6项 | 出版条目、两个论文索引、一个第三方会议缓存及两个第三方复现元数据/记录；逐项读取相关文件或引用上下文 | 不能因命中含论文ID就认定为作者实现 |
| 第三方会议缓存 | project字段null；只链ICML/OpenReview/PDF | 不是作者承诺、实时附件清单或官方代码仓库 |
| ICML OpenReview note API |403 | 无法读取真实补充字段 |
| ICML两个常规附件候选URL | `supplementary_material`和`code`均403，未返回ZIP/PDF | 字段名是候选探测，不是已确认附件名；403不证明存在或不存在 |
| 早期稿常规补充候选URL |403，未返回ZIP/PDF | 不冒称已取得早期实现或已穷尽附件 |

实际URL、每次完成时间、状态/类型、字节数、SHA和本机快照路径在JSON。15个实际响应哈希逐项核对；Git不上传整页第三方全文或快照。OpenReview未绕过验证/登录或访问控制；本轮ICML poster的web工具访问为cache miss，不充作成功请求。

## 当前结论与启动状态

官方实现repo/commit/entrypoint继续为null；不能把主页commit、PMLR出版commit、第三方复现commit或通用Qwen checkpoint当作ESP作者实现。未建立空壳官方src或伪造原字节manifest。官方来源未核验是当前启动前置缺口，不是缺少用户许可；此前GPU空闲快照不构成长期预约，入口到位时重新读取实际nvidia-smi。

已有8B自实现、非官方失败预检、4B完整配对和CPU差距账本均不重跑、不改签。目标仍是官方路径下BC30/60对照1.63/1.74，数据/prompt固定，数学门与AR诊断分开，不测速。作者公开检索、访问受限与真实未执行状态均保留，不把本轮来源工作写成Table1数值复原完成。
