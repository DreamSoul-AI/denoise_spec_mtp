"""Native SpecMTP CLI with the optional failed-job retry disabled."""
import sys
from functools import partial
from unittest.mock import patch
import rpipe.flow.cli
from spec_mtp.cli import main as native_main


def main(argv=None):
    original = rpipe.flow.cli.launch_jobs
    with patch.object(rpipe.flow.cli, 'launch_jobs', partial(original, retry_failed=False)):
        return native_main(sys.argv[1:] if argv is None else argv)


if __name__ == '__main__':
    raise SystemExit(main())
