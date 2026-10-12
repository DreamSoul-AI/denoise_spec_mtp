"""Gate the Run before RPipe writes result.json: exact_match_rate must be 1."""


def run(ctx):
    from spec_mtp.flow.checks import run_gate

    run_gate(ctx)
