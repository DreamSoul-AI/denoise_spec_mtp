"""SpecMTP summarize extension."""


def run(ctx):
    from spec_mtp.flow.checks import run_gate

    run_gate(ctx)
