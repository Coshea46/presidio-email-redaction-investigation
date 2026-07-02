import hashlib
import json
import mailbox
import os
import random
import sys

def main():
    # Ensure both MBOX_PATH and TARGET_DIR arguments are provided
    if len(sys.argv) < 3:
        print(f"Usage: python {os.path.basename(__file__)} <MBOX_PATH> <TARGET_DIR>")
        sys.exit(1)

    MBOX_PATH = sys.argv[1]
    TARGET_DIR = sys.argv[2]
    SEED = 20260623          # set seed value
    CANDIDATE_SAMPLE_SIZE = 120

    # Save the manifest inside the target directory as well
    MANIFEST_PATH = os.path.join(TARGET_DIR, "candidates_manifest.json")

    # Create the target directory if it doesn't already exist
    os.makedirs(TARGET_DIR, exist_ok=True)

    # Parse the mbox into individual messages
    mbox = mailbox.mbox(MBOX_PATH)
    messages = list(mbox)
    n_total = len(messages)
    print(f"Total messages in mbox: {n_total}")

    if n_total < CANDIDATE_SAMPLE_SIZE:
        print(f"ERROR: only {n_total} messages, need {CANDIDATE_SAMPLE_SIZE}")
        sys.exit(1)

    # Deterministic sample: seed, sample INDICES, sort them
    random.seed(SEED)
    sample_indices = sorted(random.sample(range(n_total), CANDIDATE_SAMPLE_SIZE))

    manifest = []
    for rank, idx in enumerate(sample_indices):
        msg = messages[idx]
        message_id = str(msg.get("Message-ID", "MISSING")).strip()
        subject = str(msg.get("Subject", "")).replace("\n", " ").replace("\r", "")
        date = str(msg.get("Date", ""))

        out_name = f"msg_{rank:03d}.eml"
        out_path = os.path.join(TARGET_DIR, out_name)
        with open(out_path, "wb") as f:
            f.write(bytes(msg))

        manifest.append({
            "sample_rank": rank,
            "source_index": idx,
            "message_id": message_id,
            "subject": subject,
            "date": date,
            "saved_as": out_name,
        })

    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Wrote {len(manifest)} candidate .eml files to {TARGET_DIR}/")
    print(f"Manifest -> {MANIFEST_PATH}")
    print(f"Seed used: {SEED}")

if __name__ == "__main__":
    main()