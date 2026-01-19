import boto3
import os

# -----------------------------
# CONFIG
# -----------------------------
BUCKET_NAME = "photo-matching-task-puwan-gp"
S3_TEST_PREFIX = "uploads/"     # S3 folder
LOCAL_TEST_DIR = "test_images"      # local folder

# -----------------------------
# INIT
# -----------------------------
s3 = boto3.client("s3")

os.makedirs(LOCAL_TEST_DIR, exist_ok=True)

# -----------------------------
# DOWNLOAD TEST IMAGES
# -----------------------------
def download_test_images():
    response = s3.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=S3_TEST_PREFIX
    )

    if "Contents" not in response:
        print("❌ No test images found in S3")
        return

    for obj in response["Contents"]:
        s3_key = obj["Key"]

        if s3_key.endswith("/"):
            continue

        filename = os.path.basename(s3_key)
        local_path = os.path.join(LOCAL_TEST_DIR, filename)

        s3.download_file(BUCKET_NAME, s3_key, local_path)
        print(f"✅ Downloaded {filename}")

    print("\n🎉 All test images downloaded")

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    download_test_images()
