# RPipe 职责迁移与验收

## 2026-10-14 接续范围

执行基线保持 RPipe main v0.3.0 `804b3823ab6d2af46cbda1a65688ca8b76c60b22`，研究包为 spec_mtp。继续 refactor/spec-rpipe，原 PR #4/#5 已进入 dev，新增工作不复用历史实测身份。src/rpipe 与原始证据长期保留；不覆盖 D:/GitHub/diaoenmao/RPipe 中其他任务的修改。

## 旧职责到当前职责

| **旧实现 / 接续前状态** | **目标落点与复用** | **迁移边界** |
| --- | --- | --- |
| b1f6191 的 spec_mtp/flow/runner、context、调度和 artifact 副本 | 固定 src/rpipe 的同一执行库 | 前次已迁移，不恢复第二套框架 |
| eval.py 的解码执行 | structure/algorithm/eval.py | 原 mask/EMA/tree/KV/接受/预算实现保持，execute 调用已有 Algorithm |
| eval.py 的 collect、Tracker 与 CSV 写出 | flow/collect/run.py | 移动原函数，不改变汇总与数值口径 |
| flow/checks.py 的纯证据核验 | structure/artifact/validation.py | artifact 位于两柱内；读取 Run 证据，不解码 |
| flow/checks.py 的 Run 成功门 / Study 聚合门 | flow/summarize/run.py、flow/write/run.py、flow/process/run.py | summarize 和 write 复用相同门；process 区分 scope，只验当前 index |
| 根 cli.py 的薄入口实现 | flow/cli.py；根 cli.py 为兼容导出 | 模块入口与 console script 均调用同一 RPipe，无第二套状态/恢复 |
| 根 recipe.py 的注册/构造检查 | structure/api/recipe.py；根 recipe.py 为兼容导出 | 注册不下载或执行计算，各层注册经 API 组装 |
| data/__init__.py 的业务函数 | data/datasets.py；__init__ 仅导出 | dataset、tokenization/EOS 和旧 get_prompts 接口保持 |
| Algorithm 直接调用 Data/Model 输入桥 | structure/api/data_api.py | 原 resolve_prompts/resolve_eos 移入 API；data/prompts 为兼容导出 |
| artifact 核验调用 Algorithm 设置 | structure/api/algorithm_api.py | 经 API 访问原 task/spec/config 合同，不复制解析 |

prepare 与 execute 使用 RPipe 默认阶段，不填空 hook。专项 make 复用 RPipe 的展开、脚本、调度和 provenance，未增加无职责的 make 包。Study 的阶段包只导入 src 中的实现，__init__ 不放业务。兼容 facade 保留已有实际调用，不恢复旧 runner。

## 阶段输入、输出与成功门

prepare 读 make 产生的完整 config、来源锁和输入，recipe 构造 Data/Model/Algorithm，并按原约定落 shared/data、shared/model。execute 写 decode_inputs 与 decode_observations；collect 原样计算 CSV/Tracker；summarize 检查 exact_match=1、token/轨迹及输入/权重/runtime；write 再验后由 RPipe 定稿。process 的 Run scope 用默认处理，Study scope 验当前因素×seed、来源与证据，失败同步 complete=false。配置不在 Flow 中改写。

旧根 CLI / recipe / flow.checks / data.prompts 仅保留导出以兼容已有入口；新 Study 使用阶段入口。新源码和文件移动进入专项 manifest，make/remake 与新 version 先于实测。历史 root smoke 不运行，不重新签收其锁或成功产物。

## 验证与研究边界

先导入与 AST/调用方核对，再做隔离 pytest 的真实 CLI/失败边界和固定 36 格 token/接受/cache 对照。配置、精度、TF32、backend、RNG 与原配方保持。再执行真实预训练模型的最小 baseline Study，Toy/Stub、随机 tiny 和真实模型的质量门分别报告。GPU 并发和大矩阵仍不执行。

宏观问题来自 research/research-plan-v6.md §5.11 / E1–E2：先确认已有输入空间基线和 AR 的可比较原始证据，再进入未实现的输出空间方法。真实最小 Study 不检验 H1–H13，不把输入空间 EMA 冒称 Kalman。计划、数字和报告只放对应 Study。
