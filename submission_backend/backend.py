from datetime import datetime
from dataclasses import dataclass

###############################################################################
#                          Assignment Configuration
###############################################################################
# These settings control how your submission is evaluated and packaged.
# Students: Do NOT modify this section unless explicitly instructed.
###############################################################################

# ---------------------------------------------------------------------------
# Weights & Biases (W&B) configuration
# ---------------------------------------------------------------------------
# Metric used to rank runs (must match the metric logged to wandb)
WANDB_METRIC = "EER"

# Direction for selecting best runs:
#   "ascending"  -> higher is better
#   "descending" -> lower is better
WANDB_DIRECTION = "descending"

# Number of top runs to export for grading
WANDB_TOP_N = 10

# Output file containing serialized W&B runs (used by the autograder)
WANDB_OUTPUT_PKL = "wandb_top_runs.pkl"


# ---------------------------------------------------------------------------
# Kaggle configuration
# ---------------------------------------------------------------------------
# Kaggle competition name (found at:
# https://www.kaggle.com/competitions/<competition_name>)
COMPETITION_NAME = "s-26-hw-2-p-2-sandbox"

# Slack-day Kaggle competition (used ONLY if ENABLE_SLACK_SUBMISSION = True)
SLACK_COMPETITION_NAME = "s-26-hw-2-p-2-sandbox"

# Submission deadlines (Eastern Time)
FINAL_SUBMISSION_DATETIME = "2026-01-11 23:59:59"
SLACK_SUBMISSION_DATETIME = "2026-01-11 23:59:59"

# Direction used for grading Kaggle scores
#   "ascending"  -> higher is better
#   "descending" -> lower is better
GRADING_DIRECTION = "descending"

# Output file containing Kaggle score metadata (used by the autograder)
KAGGLE_OUTPUT_JSON = "kaggle_data.json"


# ---------------------------------------------------------------------------
# Final submission artifact
# ---------------------------------------------------------------------------
# Name of the ZIP file uploaded to Autolab
SUBMISSION_OUTPUT = "HW2P2_final_submission.zip"

###############################################################################
#                          End of Configuration
###############################################################################

from datetime import datetime, timezone
import zoneinfo

eastern = zoneinfo.ZoneInfo("America/New_York")
FINAL_DEADLINE_UTC = (
    datetime.strptime(FINAL_SUBMISSION_DATETIME, "%Y-%m-%d %H:%M:%S")
    .replace(tzinfo=eastern)
    .astimezone(timezone.utc)
)

SLACK_DEADLINE_UTC = (
    datetime.strptime(SLACK_SUBMISSION_DATETIME, "%Y-%m-%d %H:%M:%S")
    .replace(tzinfo=eastern)
    .astimezone(timezone.utc)
)

ACKNOWLEDGEMENT_MESSAGE = """
Submission of this file and assignment indicate the student's agreement to the following Aknowledgement requirements:
Setting the ACNKOWLEDGED flag to True indicates full understanding and acceptance of the following:
1. Slack days may ONLY be used on P2 FINAL (not checkpoint) submission. I.e. you may use slack days to submit final P2 kaggle scores (such as this one) later on the **SLACK KAGGLE COMPETITION** at the expense of your Slack days.
2. The final autolab **code submission is due 48 hours after** the conclusion of the Kaggle Deadline (or, the same day as your final kaggle submission).
3. Course staff will require your kaggle username here, and then will pull your official PRIVATE kaggle leaderboard score. This submission may result in slight variance in scores/code, but we will check for acceptable discrepancies. Any discrepancies related to modifying the submission code (at the bottom of the notebook) will result in an AIV.
4. You are NOT allowed to use any code that will pre-load models (such as those from Hugging Face, etc.).
   You MAY use models described by papers or articles, but you MUST implement them yourself through fundamental PyTorch operations (i.e. Linear, Conv2d, etc.).
5. You are NOT allowed to use any external data/datasets at ANY point of this assignment.
6. You may work with teammates to run ablations/experiments, BUT you must submit your OWN code and your OWN results.
7. Failure to comply with the prior rules will be considered an Academic Integrity Violation (AIV).
8. Late submissions MUST be submitted through the Slack Kaggle (see writeup for details). Any submissions made to the regular Kaggle after the original deadline will NOT be considered, no matter how many slack days remain for the student.
"""
def save_acknowledgment_file(acknowledged: bool):
    if acknowledged:
        with open("acknowledgement.txt", "w") as f:
            f.write(ACKNOWLEDGEMENT_MESSAGE.strip())
        print("Saved acknowledgement.txt")
        return True
    else:
        print("ERROR: Must set ACKNOWLEDGED = True.")
        return False
# Saves README
def save_readme(readme):
    try:
        with open("README.txt", "w") as f:
            f.write(readme.strip())

        print("Saved README.txt")
    except Exception as e:
        print(f"ERROR: Error occured while saving README.txt: {e}")
        return False

    return True

# Saves wandb logs
import wandb, json, pickle

def save_top_wandb_runs(wandb_api_key, wandb_username_or_teamname, wandb_project, acknowledged):
    wandb.login(key=wandb_api_key)
    if not acknowledged:
        print("ERROR: Must set ACKNOWLEDGED = True.")
        return False

    api = wandb.Api()
    runs = api.runs(
        f"{wandb_username_or_teamname}/{wandb_project}",
        order=f"{'-' if WANDB_DIRECTION == 'descending' else ''}summary_metrics.{WANDB_METRIC}"
    )
    selected_runs = runs[:min(WANDB_TOP_N, len(runs))]

    if not selected_runs:
        print(f"ERROR: No runs found for {wandb_username_or_teamname}/{wandb_project}. Please check that your wandb credentials (Wandb Username/Team Name, API Key, and Project Name) are correct.")
        return False

    all_data = []
    for run in selected_runs:
        run_data = {
            "id": run.id,
            "name": run.name,
            "tags": run.tags,
            "state": run.state,
            "created_at": str(run.created_at),
            "config": run.config,
            "summary": dict(run.summary),
        }
        '''
        try:
            run_data["history"] = run.history(samples=1000, pandas=True).to_dict(orient="records")
        except Exception as e:
            run_data["history"] = f"Failed to fetch history: {str(e)}"
        '''
        all_data.append(run_data)
    with open(WANDB_OUTPUT_PKL, "wb") as f:
        pickle.dump(all_data, f)

    print(f"OK: Exported {len(all_data)} WandB runs to {WANDB_OUTPUT_PKL}")

    return True
# Saves kaggle information

# Install dependencies silently (only if running on Colab)
import sys

from datetime import datetime
import os, json, requests
def kaggle_login(username, key):
    os.makedirs(os.path.expanduser("~/.kaggle"), exist_ok=True)
    with open(os.path.expanduser("~/.kaggle/kaggle.json"), "w") as f:
        json.dump({"username": username, "key": key}, f)
    os.chmod(os.path.expanduser("~/.kaggle/kaggle.json"), 0o600)


def get_active_submission_config(enable_slack_submission: bool):
    if enable_slack_submission:
        return SLACK_COMPETITION_NAME, SLACK_DEADLINE_UTC
    return COMPETITION_NAME, FINAL_DEADLINE_UTC

def kaggle_user_exists(username):
    try:
        return requests.get(f"https://www.kaggle.com/{username}").status_code == 200
    except Exception as e:
        print(f"ERROR: Error occured while checking Kaggle user: {e}")
        return False

DEFAULT_SCORE=0
if GRADING_DIRECTION == "ascending":
    DEFAULT_SCORE=0
else:
    DEFAULT_SCORE=1.0

def get_best_kaggle_score(subs):
    def extract_score(s): return float(s.private_score or s.public_score or DEFAULT_SCORE)
    if not subs:
        return None, None
    best = max(subs, key=lambda s: extract_score(s) if GRADING_DIRECTION == "ascending" else -extract_score(s))

    score_type = "private" if best.private_score not in [None, ""] else "public"
    return extract_score(best), score_type

def save_kaggle_json(kaggle_username, kaggle_key, acknowledged, enable_slack_submission):

    kaggle_login(kaggle_username, kaggle_key)

    from kaggle.api.kaggle_api_extended import KaggleApi

    if not acknowledged:
        print("ERROR: Must set ACKNOWLEDGED = True.")
        return False

    if not kaggle_user_exists(kaggle_username):
        print(f"ERROR: User '{kaggle_username}' not found.")
        return False

    comp_name, deadline = get_active_submission_config(enable_slack_submission)
    api = KaggleApi()
    api.authenticate()

    # Get competition submissions
    submissions = [s for s in api.competition_submissions(comp_name) if getattr(s, "_submitted_by", None) == kaggle_username]
    if not submissions:
        print(f"ERROR: No valid submissions found for user [{kaggle_username}] for this competition [{comp_name}]. Slack flag set to [{enable_slack_submission}]")
        print("Please double check your Kaggle username and ensure you've submitted at least once.")
        return False

    score, score_type = get_best_kaggle_score(submissions)
    result = {
        "kaggle_username": kaggle_username,
        "acknowledgement": acknowledged,
        "submitted_slack": enable_slack_submission,
        "competition_name": comp_name,
        "deadline": deadline.strftime("%Y-%m-%d %H:%M:%S"),
        "raw_score": score * 100.0,
        "score_type": score_type,
    }

    print(f"OK: Projected score (excluding bonuses) saved as {KAGGLE_OUTPUT_JSON}")
    if score:
        print(f"Best score {score}.")
        with open(KAGGLE_OUTPUT_JSON, "w") as f:
            json.dump(result, f, indent=2)
        return True
    return False

import os
import sys
import zipfile

@dataclass
class SubmissionConfig:
    kaggle_username: str
    kaggle_api_key: str
    wandb_api_key: str
    wandb_username_or_teamname: str
    wandb_project: str
    notebook_path: str
    model_metadata_json: str
    additional_files: list[str]
    readme: str
    acknowledged: bool
    enable_slack_submission: bool
    safe_flag: bool


def create_submission_zip(config: SubmissionConfig):
    """
    Create the final submission ZIP using a fully config-driven workflow.
    No globals are read inside this function.
    """

    # ------------------------------------------------------------------
    # 1. Validate required config
    # ------------------------------------------------------------------
    if not config.acknowledged:
        print(
            "ERROR: Submission acknowledgement not accepted.\n"
            "Please set ACKNOWLEDGED = True and re-run the acknowledgement cell."
        )
        return

    if config.enable_slack_submission is None:
        print(
            "ERROR: ENABLE_SLACK_SUBMISSION is not set.\n"
            "Please run the submission setup cell and explicitly set it to True or False."
        )
        return

    if not config.readme:
        print("ERROR: README content is missing. Please run the README cell.")
        return

    if not config.kaggle_username or not config.kaggle_api_key:
        print("ERROR: KAGGLE_USERNAME and KAGGLE_API_KEY must be set.")
        return

    # ------------------------------------------------------------------
    # 2. Generate required files
    # ------------------------------------------------------------------
    if not save_acknowledgment_file(config.acknowledged):
        print("ERROR: Failed to save acknowledgement file.")
        return

    if not save_readme(config.readme):
        print("ERROR: Failed to save README file.")
        return

    if not save_top_wandb_runs(
        config.wandb_api_key,
        config.wandb_username_or_teamname,
        config.wandb_project,
        config.acknowledged,
    ):
        print("ERROR: Failed to save W&B run information.")
        return

    if not save_kaggle_json(
        config.kaggle_username,
        config.kaggle_api_key,
        config.acknowledged,
        config.enable_slack_submission,
    ):
        print(
            f"ERROR: Failed to save Kaggle credentials for user "
            f"[{config.kaggle_username}]."
        )
        return

    # ------------------------------------------------------------------
    # 3. Package submission
    # ------------------------------------------------------------------
    files_to_zip = [
        "acknowledgement.txt",
        "README.txt",
        KAGGLE_OUTPUT_JSON,
        WANDB_OUTPUT_PKL,
        config.model_metadata_json,
        config.notebook_path,
        *config.additional_files,
    ]

    missing_files = []

    with zipfile.ZipFile(SUBMISSION_OUTPUT, "w") as zipf:
        for file_path in files_to_zip:
            if os.path.exists(file_path):
                zipf.write(file_path, arcname=os.path.basename(file_path))
                print(f"OK: Added {os.path.basename(file_path)}")
            else:
                missing_files.append(file_path)
                print(f"ERROR: Missing file: {file_path}")

    if missing_files:
        if config.safe_flag:
            raise RuntimeError(
                "ERROR: Missing required files with safe_flag=True:\n"
                + "\n".join(missing_files)
            )
        else:
            print(
                "WARNING: Missing files detected, but safe_flag=False.\n"
                "Submission ZIP may be incomplete."
            )

    # ------------------------------------------------------------------
    # 4. Deliver result
    # ------------------------------------------------------------------
    if "google.colab" in sys.modules:
        from google.colab import files
        files.download(SUBMISSION_OUTPUT)

    print("Final submission saved as:", SUBMISSION_OUTPUT)
    print("Please upload this ZIP to Autolab for grading.")