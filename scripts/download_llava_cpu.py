import os
from huggingface_hub import snapshot_download

MODEL_ID = "llava-hf/llava-1.5-7b-hf"
TARGET_DIR = r"E:\FYP\final-year-project\models\llava-1.5-7b-hf"


def main():
    os.makedirs(TARGET_DIR, exist_ok=True)
    print(f"Downloading {MODEL_ID} -> {TARGET_DIR}")
    snapshot_download(
        repo_id=MODEL_ID,
        local_dir=TARGET_DIR,
        local_dir_use_symlinks=False,
    )
    total = 0
    for root, _, files in os.walk(TARGET_DIR):
        for f in files:
            total += os.path.getsize(os.path.join(root, f))
    print(f"Done. Size: {total/1024/1024/1024:.2f} GB")


if __name__ == "__main__":
    main()
