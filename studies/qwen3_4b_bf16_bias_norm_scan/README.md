# 4B BF16 bias magnitude scan

Plan: [Chinese](<../../docs/研究计划 Denoising Speculative Decoding.md#current-execution-20261016>) / [English](<../../docs/Research Plan Denoising Speculative Decoding.md#current-execution-20261016>). Immutable preregistration commit085722e and blob identity are in docs/source_refs.json; no standalone plan.

Eight new full480 cells, BC30/two masks/nine drafts: template/random0/random1/random2, each .5 and2 times native step_scale. Original zero and four1x cells are reused by their formal evidence SHA, not rerun. Direction construction reuses the existing control(), mean/update uses the native provider. Same480 token IDs, BF16/eager/T0/256/EOS/seed123, no prompt/template changes, content direction, Kalman or timing. Shared old AR is diagnostic; every new committed token must pass native verifier-argmax audit.

No concurrent GPU queue: after the8B independent-repeat queue exits naturally and frees the GPU, one native launch chain runs all eight in declaration order. Actual GPU nonpreemption and measured-host-peak+2GiB admission; first4B cell conservatively borrows the larger8B measured RSS/workset budget (explicitly not a4B measurement). Capacity sampling records real4B RSS. No automatic execution-failure retry, oldRun re-signing, weights/cache publication or data deletion.

Native prepare/execute/collect/summarize/write/process are retained. Readout reports three tau aggregations, paired accepted/calls/tau WTL versus own1x andzero, each random seed and their mean, lengths, acceptance by depth, first same-prefix block and actual initial bias/mean norms. Later path divergence does not establish fixed-prefix causality. No new numerical-operator chain.

## CPU preparation status

The initial nine CPU checks cover unchanged mean/fixed direction across0/.5/1/2, declared eight-cell order and immutable references, native tiny BF16 verifier-argmax at .5/2, refusal to claim an unmade scan complete, and first-block pairing that excludes changed prefill tokens or absent blocks. The readout verifies all reused raw files against their formal hashes; first-block comparisons include only equal original-input-plus-prefill prefixes and report exclusions. New curves are written only after all eight native cells and process pass.

This source preparation does not make/launch a Study. Auto-review rejected an early make during the live8B queue, so wait for that queue to exit naturally. Do not retry via another checkout or indirect runner. The active execution worktree retains its original prepared-copy snapshot until it is idle; any later source synchronization must preserve those local files before replacing them.

Linux CI initially reported521passed/2failed because Git normalized the imported resource_admission.py to LF while this Study pinned the active Windows CRLF hash. Preserve that helper's actual bytes with -text, leaving the recorded hash and code unchanged. Active8B files are read only and untouched; no native make or model forward is needed for this correction.

A second CI exposed the same conversion on question.jsonl (521passed/2failed). Keep the already-frozen working dataset byte-for-byte (SHA7dd26882...,480 CRLF records), rather than changing its expected SHA. Its former Git LF blob SHA4b6d33e7... has exactly the same480 parsed records/order. Add -text to preserve the frozen data bytes; the current dataset and prompt manifest are unchanged, so no model inputs are altered. Windows git archive applied checkout-style line conversion and was not a valid Linux-byte simulation; subsequent verification materializes raw git cat-file blobs instead.

Mask-displacement observations convert the already-stored BF16 mask and mean to FP32 before subtraction/norm, avoiding an extra BF16 subtraction rounding in the reported metric. This is read-only measurement, with no FP32 model forward or change to native masks/EMA/tree. Existing scale-control tests check that definition explicitly.

## 只读端点准备与后续验收

等待8B期间，在主仓根目录的CPU终端执行以下只读命令；所有新输出在主仓.tmp，实际执行副本只读。该模式核对旧端点/共享AR、正式SHA、原输入/计数及已存argmax/owner，不调用make、原生新格验收或绘图。

```powershell
$sdOldCuda = $env:CUDA_VISIBLE_DEVICES
$sdOldPath = $env:PYTHONPATH
try {
    $env:PYTHONUTF8 = '1'
    $env:CUDA_VISIBLE_DEVICES = ''
    $env:PYTHONPATH = 'src'
    & D:\anaconda3\python.exe studies/qwen3_4b_bf16_bias_norm_scan/analyze_results.py --check-reused --data-root 'D:/360安全浏览器下载/Agent/DreamSoul/tmp/4b-bf16-five-methods-20261015' --output-dir .tmp/norm-readiness-20261016
    if ($LASTEXITCODE -ne 0) { throw 'Reused endpoint evidence missing or inconsistent' }
} finally {
    $env:CUDA_VISIBLE_DEVICES = $sdOldCuda
    $env:PYTHONPATH = $sdOldPath
}
```

[实际准备报告](docs/STUDY_REPORT.md)和[CPU检查点](docs/reused_readiness_v1.json)覆盖5个旧端点、30份Spec源文件、405083个原始argmax/owner记录。输出明确complete=false、reused_only=true、new_cells_inspected=false；0.5×/2×八格仍未执行，不能由端点推算曲线。

后续正常读出支持--data-root（旧Run根副本）、--study-dir（完成后的冻结范数Study）、--output-dir（独立CPU报告目录）；须从冻结Study所属执行根目录、使用该副本src调用，保留原生相对输入和来源检查。正常读出会严格比较索引与原八格声明和顺序、每格一个Run、实际cfg完整spec、逐token门、480条progress与原生Study process；正式JSON和曲线只在全13端点通过后生成。新输出先写独立目录，验收后按主题合dev，不重签或覆盖旧结果。

## 19:15授权后的排班更新

旧“先等8B自然退出”和借用8B预算的排班仅为历史状态；Enmao19:15明确授权RAM不足时空卡执行本八格。已完成固定q295/1500输入、256上界token的BF16容量标定（EOS关闭仅用于容量），全256 token数学门通过，非正式τ结果。实测进程树峰值8808693760 bytes，正式4B门加2GiB为10956177408 bytes；显存门为实测peak reserved加1024MiB。见docs/capacity_calibration_v1.json和norm_admission.py。探针结束已恢复BC60。

主仓独立make version v2-capacity，不修改活动8B工作树；单一父队列逐格调用原生run-one，完整格结束即恢复BC60并检查8B优先权，满足原8B门时先让BC60。进程只可逆suspend/resume，保留创建时间核验，异常finally恢复；不终止其他会话。已有0/1倍和科学/数据合同不变。
