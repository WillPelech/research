#!/usr/bin/env python3
"""CLI entrypoint: python -m run_digest [--dry-run]"""

from src.digest import main

if __name__ == "__main__":
    raise SystemExit(main())
