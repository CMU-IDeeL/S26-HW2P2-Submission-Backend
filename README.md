# HW2P2 Autolab Submission Backend

This repository contains the **submission framework** used to
standardize student submissions for Autolab grading for **S26'S HW2P2**.

It is designed to:

- Collect WandB experiment logs
- Retrieve official Kaggle leaderboard scores
- Enforce submission acknowledgements and deadlines
- Package all required artifacts into a single ZIP file for Autolab

This README is intended **for future TAs and instructors** maintaining or
reusing this infrastructure.

---

## Repository Overview

```

.
├── backend.py                 # Core submission logic (TA-maintained)
├── submission_notebook.ipynb  # Student-facing notebook template
└── README.md                  # This file

```

---

## File 1: `backend.py`

### Purpose

`backend.py` contains **all non-student-editable logic** required to:

- Validate submissions
- Export WandB runs
- Query Kaggle for official scores
- Enforce deadlines and Slack-day rules
- Generate the final Autolab ZIP artifact

Students should **never modify this file**.

---

### High-Level Flow

The backend performs the following steps in order:

1. **Acknowledgement Enforcement**

   - Students must explicitly set `ACKNOWLEDGED = True`
   - An `acknowledgement.txt` file is generated and included in the ZIP

2. **README Generation**

   - Saves a student-completed `README.txt` describing:
     - Model architecture
     - Training strategy
     - Augmentations
     - Notebook execution notes

3. **WandB Export**

   - Logs into WandB using the student's API key
   - Pulls the top `N` runs based on a configured metric/direction
   - Serializes run metadata + limited history into:
     ```
     wandb_top_runs.pkl
     ```

4. **Kaggle Score Retrieval**

   - Authenticates using Kaggle API credentials
   - Selects the correct competition (regular or Slack)
   - Extracts the best valid submission score
   - Saves structured metadata to:
     ```
     kaggle_data.json
     ```

5. **Submission Packaging**
   - Validates existence of all required files
   - Flattens paths and zips artifacts into:
     ```
     HW2P2_final_submission.zip
     ```

---

### Key Configuration (TA-Controlled)

These variables are intentionally centralized near the top of the file:

```python
WANDB_METRIC
WANDB_DIRECTION
WANDB_TOP_N

COMPETITION_NAME
SLACK_COMPETITION_NAME
FINAL_SUBMISSION_DATETIME
SLACK_SUBMISSION_DATETIME

SUBMISSION_OUTPUT
```

**TA Guidance:**

- Keep these values consistent with the course writeup
- Do NOT allow students to override them
- If reused next semester, update only this section

---

### Deadline Handling

Deadlines are:

- Defined in **Eastern Time**
- Converted internally to **UTC** for robustness
- Compared against Kaggle submission timestamps

Slack submissions are handled by switching competitions, **not by extending deadlines**.

---

### Safety Features

- Explicit checks for:

  - Missing globals
  - Missing files
  - Invalid credentials

- Optional `SAFE_SUBMISSION` flag:

  - `True` → hard fail on missing files
  - `False` → allow incomplete ZIP (for debugging only)

---

## File 2: `submission_notebook.ipynb`

### Purpose

This notebook is the **only file students directly interact with**.

It serves as:

- A guided configuration interface
- A controlled execution environment
- A wrapper around `backend.py`

---

### Student Responsibilities

Students are expected to:

1. Fill out metadata:

   - Kaggle username
   - WandB project
   - README contents

2. Generate `model_metadata_*.json`
3. Provide correct file paths for:

   - Notebook
   - Model metadata
   - Optional additional files

4. Explicitly accept the acknowledgement
5. Run the final submission cell

---

### TA Design Notes

- Students **do not import arbitrary code**
- All sensitive logic lives in `backend.py`
- Notebook cells are ordered to enforce correct execution
- Errors are verbose and actionable to reduce Piazza load

---

## Common TA Tasks

### Updating for a New Semester

- Update competition names
- Update deadlines
- Verify WandB metric name
- Regenerate starter notebook (no backend changes usually needed)

### Debugging Student Issues

Most failures fall into:

- Missing API keys
- Incorrect file paths
- Forgotten acknowledgement flag
- No valid Kaggle submissions

Backend error messages are intentionally explicit.

---

## Recommended Future Improvements

- Convert global configuration to a dataclass
- Move WandB/Kaggle adapters into isolated modules
- Add dry-run mode for TA testing
- Add unit tests for deadline logic

---

## Contact / Ownership

Maintained by:
**Course Staff / TA Team**

If you inherit this codebase:

- Read this README first
- Avoid modifying backend logic mid-semester
- Prefer additive changes over refactors

---
