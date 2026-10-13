"""SpecMTP collect extension."""


def run(ctx):
    from spec_mtp.structure.algorithm.eval import collect

    collect(ctx)
