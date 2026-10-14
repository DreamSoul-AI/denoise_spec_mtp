# q173 matched-window diagnostic plan

## Purpose and predeclaration (2026-10-14)

The fixed three-prompt matrix is retained. Diagnose q173 at root83 (input-chain advantage) and root94/97 (order1 versus order0 advantage), selected from the saved paired-prefix analysis before examining hidden/logit values. No other windows, gain search or replacement prompt. Version output-space-q173-window-20261014-v1 identifies an instrumented diagnostic replay, linked to the original four native Run IDs; it is not counted as new acceptance evidence or used to re-sign them.

Existing tools/profile_cpu.py measures the unchanged SpecDecoder directly; follow the same tool pattern, with read-only hooks around the existing forward/provider. No new decoder, sampler, cache routine, Run scheduler or scientific src edit. Tool source hash, this PLAN hash, original execution JSON/raw hashes, source670c744e0535dcad and ModelScope11-file hashes bind the measurement. Temporary tensors/logs go to a new .tmp/output-windows-20261014 directory; formal scalar evidence/report stays in this Study. No push, merge or data cleanup.

## Fixed replay and budget

Same Qwen3-0.6B ModelScope snapshot, FP32/eager/CUDA, unpruned[1,1]/k2/BC9, order0/order1 gains, T0, EOS, budget100. Replay q173 for input/order0/order1 serially once per case, using the saved rendered input and original per-prompt generator seed124. No warmup or timing comparison; hooks may synchronize and distort wall time. Existing runtime flags must match. Full output and semantic verification/commit/KV trace must reproduce the corresponding saved matrix case exactly; otherwise preserve failure and do not interpret the measurements.

At most300 decoded new tokens across three replays (the saved outputs have33 each). One teacher-forced causal forward over the saved AR sequence supplies exact normalized hidden references; it is not a new AR generation. For each of3cases*3windows, at most1 additional causal prefix+actual first seed-mask forward checks that recorded seed logits have the same top1 as an isolated correct-prefix replay. Max10 auxiliary forwards, max103 positions per forward, singleGPU/threads1, no concurrent experiment. Capacity uses the prior same-model serial calibration and fresh device/RAM check, recording new sampled resources separately.

## Observation timing and quantities

Current-block masks seed the NEXT tree. Acceptance at root p uses mask logits from the preceding block's deepest accepted owner's masks (first mask input at position p), not the masks being constructed at root p. Record seed source block root/owner, absolute mask positions and input vectors, normalized hidden/logits, as well as current root exact hidden and output-provider committed anchor/velocity/proxies. The original root verifier and cache keep logic remain untouched.

At each selected window, compute first-slot target token versus best alternative logit margin, top1/top2 IDs/probabilities and target probability; the target is the independently saved AR token at p+1. Compare seed-mask norm, proxy-versus-exact root hidden cosine and relative L2 error. Record second-slot candidate too, but label its AR comparison valid only if the first draft token matches the AR next token; an invalid draft prefix is not an exact hidden observation. Save full selected tensors locally to make scalar calculations reproducible, without publishing weights or full vocabulary logits.

The auxiliary prefix+mask input is AR[:p] followed by the actual stored seed mask at position p. It has the same true prefix as the preceding accepted owner, which is independently checked from the original block layout. Record differences in original versus isolated target margins; require equal top1 IDs and normalized-hidden cosine>=.99999. Root exact hidden versus teacher-forced AR hidden also requires cosine>=.99999. These are diagnostic consistency gates, not acceptance-improvement thresholds.

## Interpretation and stop

All three replay/token/trace/source/runtime/input and window-completeness gates must pass. Verify hook removal and provider method restoration, forward counts (1+decode_calls per replay; no observer-induced target calls), and model digest unchanged. Stop on any mismatch, OOM, missing capture, source/file drift or consistency gate failure; no silent correction or retry on an old diagnostic output directory.

A seed margin crossing0 at the same verified prefix explains a greedy candidate/acceptance difference under these fixed observations. It does not by itself establish that EMA velocity is optimal, that proxy-error magnitude causes the gain, or that output-space masks outperform input masks. Keep both advantage and disadvantage windows and all failures. Do not retune, expand the matrix, change src or declare Kalman supported.
