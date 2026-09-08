"""Allow `python -m radhanite`."""

import sys

from radhanite.cli import main

sys.exit(main(sys.argv[1:]))
