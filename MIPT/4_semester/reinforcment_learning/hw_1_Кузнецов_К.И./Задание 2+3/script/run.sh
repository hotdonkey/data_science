#!/bin/bash
mkdir -p logs
python main.py 2>&1 | tee logs/convergence.log