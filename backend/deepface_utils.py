from deepface import DeepFace
import os

def build_database(image_root):
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
                    detector_backend="opencv",
                    enforce_detection=False
                )

                embeddings.append(result[0]["embedding"])
                print(f"✅ Embedded {img_path}")

            except Exception as e:
                print(f"❌ Failed {img_path}: {e}")

        if embeddings:
            database[person] = embeddings

    return database


if __name__ == "__main__":
    db = build_database("purified_images")
    print("\n🎉 Database ready:", list(db.keys()))


