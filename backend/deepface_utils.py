from deepface import DeepFace
import os
from scipy.spatial.distance import cosine
from pymongo import MongoClient
from datetime import datetime
import qrcode
import boto3

# -----------------------------
THRESHOLD = 0.35  # ArcFace threshold

# S3 Configuration
S3_BUCKET = "photo-matching-task-puwan-gp"
S3_FOLDER = "qr_codes/"
s3_client = boto3.client("s3", region_name="eu-north-1")  # AWS creds must be configured

# Local folder to temporarily save QR images
LOCAL_QR_FOLDER = "qr_codes"
os.makedirs(LOCAL_QR_FOLDER, exist_ok=True)

# -----------------------------
def build_database(image_root):
    """
    Build embeddings database from known person images.
    """
    database = {}
    for person in os.listdir(image_root):
        person_path = os.path.join(image_root, person)
        if not os.path.isdir(person_path):
            continue


        embeddings = []
        for img in os.listdir(person_path):
            img_path = os.path.join(person_path, img)
            try:
                result = DeepFace.represent(
                    img_path=img_path,
                    model_name="ArcFace",
                    detector_backend="retinaface",
                    enforce_detection=False
                )
                embeddings.append(result[0]["embedding"])
                print(f"✅ Embedded {img_path}")
            except Exception as e:
                print(f"❌ Failed {img_path}: {e}")

        if embeddings:
            database[person] = embeddings
    return database

# -----------------------------
def find_best_match(test_embedding, database):
    """
    Compare a test embedding to the database and return best match.
    """
    best_match = None
    min_distance = float("inf")
    for person, embeddings in database.items():
        for emb in embeddings:
            distance = cosine(test_embedding, emb)
            if distance < min_distance:
                min_distance = distance
                best_match = person

    if min_distance < THRESHOLD:
        return best_match, min_distance
    else:
        return "Couldn't find", min_distance

# -----------------------------
def generate_and_upload_qr(test_image, matched_persons):
    """
    Generate QR code for the test image only if known persons matched,
    upload to S3, and return pre-signed URL.
    """
    if not matched_persons:
        return None  # no QR for unknowns

    # Create dynamic URL with matched persons and image name
    qr_content = f"https://photo-matching-qr-web-tdnn.vercel.app/client?person={','.join(matched_persons)}&image={test_image}"
    qr_filename = f"{test_image.split('.')[0]}.png"
    local_qr_path = os.path.join(LOCAL_QR_FOLDER, qr_filename)

    # Generate QR code
    qr_img = qrcode.make(qr_content)
    qr_img.save(local_qr_path)

    # Upload to S3
    s3_key = f"{S3_FOLDER}{qr_filename}"
    s3_client.upload_file(local_qr_path, S3_BUCKET, s3_key)

    # Generate pre-signed URL (valid 1 hour)
    qr_s3_url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET, "Key": s3_key},
        ExpiresIn=3600
    )
    return qr_s3_url

# -----------------------------
def test_images(test_root, database, matches_col):
    """
    Analyze only new test images, detect faces, match to database,
    store results in MongoDB, and generate QR codes.
    """
    for img_name in os.listdir(test_root):
        img_path = os.path.join(test_root, img_name)

        # Skip if already processed
        if matches_col.find_one({"test_image": img_name}):
            print(f"⏭ Skipping {img_name}, already processed")
            continue

        try:
            results = DeepFace.represent(
                img_path=img_path,
                model_name="ArcFace",
                detector_backend="retinaface",
                enforce_detection=False
            )

            matched_persons = set()
            for result in results:
                embedding = result["embedding"]
                match, distance = find_best_match(embedding, database)
                if match != "Couldn't find":
                    matched_persons.add(match)

            matched_persons_list = list(matched_persons)

            qr_url = None
            if matched_persons_list:
                qr_url = generate_and_upload_qr(img_name, matched_persons_list)

            record = {
                "test_image": img_name,
                "matched_persons": matched_persons_list if matched_persons_list else ["Couldn't find"],
                "qr_url": qr_url,
                "timestamp": datetime.utcnow()
            }
            matches_col.insert_one(record)

            print(f"🔍 {img_name} → {record['matched_persons']} | QR: {qr_url} saved to DB")

        except Exception as e:
            print(f"❌ Failed {img_path}: {e}")

# -----------------------------
if __name__ == "__main__":
    # Step 1: Build database
    db = build_database("purified_images")
    print("\n🎉 Database ready:", list(db.keys()))

    # Step 2: Connect to MongoDB
    client = MongoClient(
        "mongodb+srv://photo_admin:Qwerty(789)@cluster001.sczag4j.mongodb.net/?retryWrites=true&w=majority"
    )
    db_mongo = client["photo_matching"]
    matches_col = db_mongo["matches"]
    print("MongoDB connected successfully")

    # Step 3: Analyze test images and generate QR codes
    test_images("test_images", db, matches_col)
