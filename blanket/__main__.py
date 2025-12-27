"""CLI entry point for Blanket."""

import sys

from blanket import enforce


def main():
    has_changes = enforce(sys.argv[1:])
    if has_changes:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
