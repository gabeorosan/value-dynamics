---
title: Value Dynamics ZeroGPU Smoke
emoji: microscope
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 6.1.0
app_file: app.py
pinned: false
python_version: 3.12
---

# Value Dynamics ZeroGPU Smoke

Minimal Hugging Face Space for testing whether a Space can receive dynamic GPU
allocation. It runs a tiny PyTorch optimizer loop and reports the visible device.

For ZeroGPU hosting, select ZeroGPU hardware in the Space settings. Existing
ZeroGPU Spaces are usable by free accounts, but hosting a personal ZeroGPU Space
requires HF PRO; organization hosting requires Team or Enterprise.
