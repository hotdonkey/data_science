#!/usr/bin/env python3
import sys
import json
import ast

def parse_attrs(attrs):
    out = []
    for k, v in attrs.items():
        if not isinstance(v, str):
            continue
        # Обрабатываем ТОЛЬКО строки, похожие на словари
        if v.startswith("{") and v.endswith("}"):
            try:
                parsed = ast.literal_eval(v)
                if isinstance(parsed, dict):
                    for sk, sv in parsed.items():
                        out.append(f"{k}:{sk}:{sv}")
                else:
                    out.append(f"{k}:{v}")
            except Exception:
                out.append(f"{k}:{v}")
        else:
            out.append(f"{k}:{v}")
    return out

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        data = json.loads(line)
        attrs = data.get("attributes", {})
        if isinstance(attrs, dict):
            for tag in parse_attrs(attrs):
                print(tag)
    except Exception:
        continue