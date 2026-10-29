#!/usr/bin/env python3
"""Current Model 06 entrypoint. Rev01 was rejected; run Rev02 instead.

Rev01 source for audit: make_side_walls_rev01_rejected.py.
Rev02 writes candidate QA to .cache by default; use --release only after review.
"""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('make_side_walls_rev02.py')),run_name='__main__')
