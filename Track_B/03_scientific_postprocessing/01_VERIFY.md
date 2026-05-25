# Verify Sub-team 03

Use these commands for scientific post-processing.

## Setup

Run dependency setup from the repository root, `Track_B/`:

```bash
python -m pip install -r requirements.txt
```

Shared setup notes are in <a href="../02_COMMANDS_AND_VERIFY.md" target="_blank" rel="noopener noreferrer">../02_COMMANDS_AND_VERIFY.md</a>.

## Starter Checks

Run from `Track_B/03_scientific_postprocessing`:

```bash
python -m pytest -q
python scripts/quicklook.py --dataset reference
python scripts/quicklook.py --dataset challenge
```

`quicklook.py` writes:

- `outputs/reference/quicklook.png`
- `outputs/challenge/quicklook.png`

Do not commit files under `outputs/`.

## Optional Dataset Regeneration

The datasets are already provided. For transparency, regenerate them only if the facilitator asks.

Run from `Track_B/03_scientific_postprocessing`:

```bash
python scripts/generate_dataset.py
```

## After Building an Analysis

Run your analysis command from `Track_B/03_scientific_postprocessing`. For example:

```bash
python scripts/analyze_data.py --dataset reference
python scripts/analyze_data.py --dataset challenge
```

Then check that every claim in the report points to a computed value, table, figure, or data-quality check.

Next: <a href="DEMO_REPORT_TEMPLATE.md" target="_blank" rel="noopener noreferrer">update DEMO_REPORT_TEMPLATE.md</a>.
