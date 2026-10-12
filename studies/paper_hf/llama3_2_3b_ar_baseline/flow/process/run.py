"""Study scope only: every declared variant x seed must have passed the Run gate."""


def run(ctx):
    if ctx.scope != 'study':
        return
    from spec_mtp.flow.checks import study_gate

    study_gate(ctx)
