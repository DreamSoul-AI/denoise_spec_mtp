# Nonofficial ESP Table1 independent repeat

Execution contract: [project plan](<../../docs/研究计划 Denoising Speculative Decoding.md#current-execution-20261016>). Original480,8B BF16/T0,BC10/30/60 single mask,lambda0.1 updating mean,256/EOS; new version/Runs. Source refs pin immutable plan blob. No separate Study plan, author-source claim or timing.

## Git byte preservation and CI

PR43 Linux CI found513 passed/1 failed: the copied helpers were CRLF-identical to their originals in the active Windows working copy, but normal Git text conversion stored new files as LF while old pinned originals retained CRLF. Preserve the two new helpers with -text and store their original Git blob bytes; do not relax the byte-identity regression. Original SHA256: untimed_bf16.py=0cf92c63bf47df15fcca46d61f9404d08b2437ea03c5827c227a0c0dbddbc81f; argmax_audit.py=0ed6687022d7cdb4c161e2810938bc806b0cfca3b126509a0ede44a56e98a958. Native scientific behavior is unchanged. The active execution worktree/files/branch remain untouched; old Run source locks/Git metadata are never re-signed. This separate primary-checkout integration also removes obsolete .gitattributes entries for deleted standalone plans.

## Independent-repeat readout

After native execution/finalization, run `python studies/esp_table1_nonofficial_revalidation/analyze_results.py` in the checkout containing the native Runs and old full480 evidence. CPU only, no model forwards. It reuses the original tau aggregation, verifies each committed choice and audit hash, frozen inputs/model/EOS, three single-mask cells and native gates, and reports each completed cell without inventing a full-matrix result. Formal evidence requires all three cells and native process to pass.

The report includes all three aggregations and differences from both old results and paper targets, per-prompt accepted/calls/tau WTL, output lengths/hashes and independent AR disagreement/first divergence. AR mismatch is diagnostic. Different paths/lengths are not speed or fixed-prefix causal evidence. Historical source locks and Run results are never rewritten. The analyzer is a post-execution readout with its own recorded SHA, not a change to the active Study's declarations or execution source. Six CPU regressions cover diagnostics, audit failures and ratio-based pairing.

The8B prompt manifest has no EOS field; EOS and the resolved eval settings (including framework-derived device) are checked against the old Run's actual decode_inputs.json after validating its formal recorded SHA. If old Runs are in another checkout, pass --baseline-runs pointing to that Run directory; do not copy/re-sign old evidence or substitute4B manifest fields. The new cfg/old/new resolved eval and spec must agree exactly.

## BC60放行后的CPU验收

原队列持续保留：BC60仅在实测峰值加2GiB主机RAM及实际GPU非抢占门同时满足后载模；量化PPL插队期间同样等待，不重开、不杀、不改门。进度480不是终验，必须等原Run result=succeeded及Study process/spec_mtp_study_check均complete/passed。8B源码、声明、数据和冻结身份保留到原生队列自然退出及读出完成，不make重签。

读出必须使用**原执行副本的src及其CWD**，因为原生declared_inputs保存了解析后的绝对文件身份；主仓后续集成不能替代此来源。以下PowerShell只读执行副本，报告写主仓.tmp，恢复环境后才可另做GPU操作：

```powershell
$sdRepo = 'D:\GitHub\DreamSoul\denoising-speculative-decoding'
$sdExecution = 'D:\360安全浏览器下载\Agent\DreamSoul\tmp\4b-bf16-five-methods-20261015'
$sdPreviousCuda = $env:CUDA_VISIBLE_DEVICES
$sdPreviousPath = $env:PYTHONPATH
Push-Location $sdExecution
try {
    $env:PYTHONUTF8 = '1'
    $env:CUDA_VISIBLE_DEVICES = ''
    $env:PYTHONPATH = "$sdExecution\src"
    & D:\anaconda3\python.exe "$sdRepo\studies\esp_table1_nonofficial_revalidation\analyze_results.py" --study-dir "$sdExecution\studies\esp_table1_nonofficial_revalidation" --baseline-runs "$sdRepo\studies\esp_table1_bf16_full_argmax\runs" --output-dir "$sdRepo\.tmp\cpu-acceptance-20261016\table1"
    if ($LASTEXITCODE -ne 0) { throw 'CPU evidence verification failed; preserve original Runs' }
} finally {
    $env:CUDA_VISIBLE_DEVICES = $sdPreviousCuda
    $env:PYTHONPATH = $sdPreviousPath
    Pop-Location
}
```

当前实际演练得到complete=false/cells_complete=2：BC10/30有效，BC60保持pending，未生成正式全矩阵JSON；[CPU检查点](docs/cpu_acceptance_checkpoint_v1.json)保存汇总、原始SHA和配对结果。演练没有在活动执行树写报告。曾从主仓CWD运行被原生绝对输入身份门拒绝，改用原执行CWD后通过；未放宽或重签来源。

三格及native process全过才生成repeat_evidence_v1.json；逐项核对三种τ、相对旧值与论文的有符号差（BC30=1.63、BC60=1.74）、全部提交token的argmax、AR一致率及逐条首分叉、输出长度和逐prompt接受/calls/τ赢平输。数学门失败则保留失败，不以AR失配判失败；不得只选最接近目标的聚合。完整报告进入既有主题工作分支，更新中英文项目计划，按PR/CI合dev后清已合普通分支，原始Run/缓存/权重不入Git。

BC60及整条8B队列自然退出、正式证据保存后，才保留旧未提交范数源码并同步已合准备，make/串行launch4B八个新格；0/1×继续复用已有完整480，不重复跑。资源仍未准入时只做CPU准备，不启动旁路队列或完整训练。

## 本轮收尾结果

三主格全480、Run/Study及CPU来源审计全部成功；pooled τ依次1.399047031/1.563377504/1.647301264，BC30/60相对论文1.63/1.74仍低0.066622496/0.092698736，未复现论文数值。239,137个提交token的验证argmax自检全过，AR一致率仅诊断。完整三聚合、逐条首分叉及来源/输出SHA见[repeat_evidence_v1.json](docs/repeat_evidence_v1.json)。此为非作者官方实现；后续实验已暂停，中文通俗总结在项目主研究计划，不提出下一阶段方案。
