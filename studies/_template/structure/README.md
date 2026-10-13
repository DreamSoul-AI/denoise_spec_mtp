# structure/

这里仅放本轮 Study 自己的建构，按 RPipe 的 api/control/data/model/algorithm/system/artifact/make 职责组织；没有职责时不建包或空壳。

现有 SpecMTP Data/Model/Algorithm 在 `src/spec_mtp/structure/`，由 recipe 注册；mask/tree/KV/对齐与指标沿用已有研究实现。Factory、Registry、配置、调度、日志和 result/provenance 复用 `src/rpipe/`。两柱 Python 自动进入 RPipe provenance，额外参考文件按需声明 include；外部 `spec_mtp` 由专项源码锁补齐。见 [Study 指南](../../README.md)。
