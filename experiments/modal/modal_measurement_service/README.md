# Modal Measurement Service

Volume layout:

```text
/ckpts/<run_name>/<checkpoint_name>/
  adapter_config.json
  adapter_model.safetensors
/ckpts/<run_name>/manifest.json
```

`manifest.json` is optional. If present, it should contain `{"checkpoints": [...]}` with checkpoint names and metadata such as `organism`, `arm`, `round`, and `draw_seed`. If absent, the service lists checkpoint directories under the run.

Upload adapters:

```bash
python experiments/modal/modal_measurement_service/upload_checkpoints.py /path/to/local/ckpts <run_name>
```

Run measurement:

```bash
modal run experiments/modal/modal_measurement_service/modal_app.py --run-name <run_name> --parallel 8
```

Expected cost is about `$0.20/checkpoint` on an L40S, depending on queue time and generation length.

Future Kaggle scripts should save one PEFT adapter per measured round:

```python
from pathlib import Path

ckpt_root = Path("/kaggle/working/ckpts")
ckpt_name = f"{organism}_{arm}_seed{seed}_r{round}"
ckpt_dir = ckpt_root / ckpt_name
ckpt_dir.mkdir(parents=True, exist_ok=True)
model.save_pretrained(str(ckpt_dir))
# Later:
# kaggle kernels output <owner>/<kernel> -p ./kaggle_output
# python experiments/modal/modal_measurement_service/upload_checkpoints.py ./kaggle_output/ckpts <run_name>
```
