import boto3
import os

# --------------------------
# CONFIGURATION
# --------------------------
BUCKET_NAME = 'photo-matching-task-puwan-gp'  # S3 bucket
PREFIX = 'known/'                              # top-level folder in bucket
LOCAL_BASE_FOLDER = 'downloaded_images'       # local folder to save images

# Initialize S3 client (make sure AWS CLI is configured or provide credentials)
s3 = boto3.client('s3')


# --------------------------
# FUNCTIONS
# --------------------------

def download_images(bucket_name=BUCKET_NAME, prefix=PREFIX, local_base=LOCAL_BASE_FOLDER):
    
    os.makedirs(local_base, exist_ok=True)
    
    # List all objects in the prefix
    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    
    if 'Contents' not in objects:
        print(f"No objects found in bucket '{bucket_name}' with prefix '{prefix}'")
        return

    for obj in objects['Contents']:
        key = obj['Key']
        
        # Skip if the object is a "folder" (S3 folders end with '/')
        if key.endswith('/'):
            continue
        
        # Extract subfolder (person name) from key
        relative_path = key[len(prefix):]  # remove 'known/' from key
        local_path = os.path.join(local_base, relative_path)
        
        # Create local subfolder if needed
        local_folder = os.path.dirname(local_path)
        os.makedirs(local_folder, exist_ok=True)
        
        # Download file
        s3.download_file(bucket_name, key, local_path)
        print(f"Downloaded {key} → {local_path}")


def upload_file(bucket_name, local_file, s3_path):
    """
    Upload a local file to S3.
    """
    s3.upload_file(local_file, bucket_name, s3_path)
    print(f"Uploaded {local_file} → s3://{bucket_name}/{s3_path}")


# --------------------------
# MAIN
# --------------------------
if __name__ == "__main__":
    download_images()
