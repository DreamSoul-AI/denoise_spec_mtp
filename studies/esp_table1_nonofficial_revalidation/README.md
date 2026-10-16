# Nonofficial ESP Table1 independent repeat

Execution contract: [project plan](<../../docs/研究计划 Denoising Speculative Decoding.md#current-execution-20261016>). Original480,8B BF16/T0,BC10/30/60 single mask,lambda0.1 updating mean,256/EOS; new version/Runs. Source refs pin immutable plan blob. No separate Study plan, author-source claim or timing.

## Git byte preservation and CI

PR43 Linux CI found513 passed/1 failed: the copied helpers were CRLF-identical to their originals in the active Windows working copy, but normal Git text conversion stored new files as LF while old pinned originals retained CRLF. Preserve the two new helpers with -text and store their original Git blob bytes; do not relax the byte-identity regression. Original SHA256: untimed_bf16.py=0cf92c63bf47df15fcca46d61f9404d08b2437ea03c5827c227a0c0dbddbc81f; argmax_audit.py=0ed6687022d7cdb4c161e2810938bc806b0cfca3b126509a0ede44a56e98a958. Native scientific behavior is unchanged. The active execution worktree/files/branch remain untouched; old Run source locks/Git metadata are never re-signed. This separate primary-checkout integration also removes obsolete .gitattributes entries for deleted standalone plans.
