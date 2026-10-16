# Nonofficial ESP Table1 independent repeat

Execution contract: [project plan](<../../docs/研究计划 Denoising Speculative Decoding.md#current-execution-20261016>). Original480,8B BF16/T0,BC10/30/60 single mask,lambda0.1 updating mean,256/EOS; new version/Runs. Source refs pin immutable plan blob. No separate Study plan, author-source claim or timing.

## Git byte preservation and CI

PR43 Linux CI found513 passed/1 failed: the copied helpers were CRLF-identical to their originals in the active Windows working copy, but normal Git text conversion stored new files as LF while old pinned originals retained CRLF. Preserve the two new helpers with -text and store their original Git blob bytes; do not relax the byte-identity regression. Original SHA256: untimed_bf16.py=0cf92c63bf47df15fcca46d61f9404d08b2437ea03c5827c227a0c0dbddbc81f; argmax_audit.py=0ed6687022d7cdb4c161e2810938bc806b0cfca3b126509a0ede44a56e98a958. Native scientific behavior is unchanged. The active execution worktree/files/branch remain untouched; old Run source locks/Git metadata are never re-signed. This separate primary-checkout integration also removes obsolete .gitattributes entries for deleted standalone plans.

## Independent-repeat readout

After native execution/finalization, run `python studies/esp_table1_nonofficial_revalidation/analyze_results.py` in the checkout containing the native Runs and old full480 evidence. CPU only, no model forwards. It reuses the original tau aggregation, verifies each committed choice and audit hash, frozen inputs/model/EOS, three single-mask cells and native gates, and reports each completed cell without inventing a full-matrix result. Formal evidence requires all three cells and native process to pass.

The report includes all three aggregations and differences from both old results and paper targets, per-prompt accepted/calls/tau WTL, output lengths/hashes and independent AR disagreement/first divergence. AR mismatch is diagnostic. Different paths/lengths are not speed or fixed-prefix causal evidence. Historical source locks and Run results are never rewritten. The analyzer is a post-execution readout with its own recorded SHA, not a change to the active Study's declarations or execution source. Six CPU regressions cover diagnostics, audit failures and ratio-based pairing.

The8B prompt manifest has no EOS field; EOS and the resolved eval settings (including framework-derived device) are checked against the old Run's actual decode_inputs.json after validating its formal recorded SHA. If old Runs are in another checkout, pass --baseline-runs pointing to that Run directory; do not copy/re-sign old evidence or substitute4B manifest fields. The new cfg/old/new resolved eval and spec must agree exactly.
