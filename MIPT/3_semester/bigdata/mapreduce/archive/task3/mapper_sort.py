#!/usr/bin/env python3

import sys
import json
from datetime import datetime
import io

input_stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
output_stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
stderr_stream = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


for line in input_stream:
    print(line.strip(), file=output_stream)