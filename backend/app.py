import argparse
import pickle

from insightface_utils import load_images as if_load_images, encode_faces as if_encode_faces, IMAGE_DIR as IF_IMAGE_DIR, OUTPUT_FILE as IF_OUTPUT
try:
	from face_recognition_utils import load_images as fr_load_images, encode_faces as fr_encode_faces, IMAGE_DIR as FR_IMAGE_DIR, OUTPUT_FILE as FR_OUTPUT
	HAS_FR = True
except Exception:
	HAS_FR = False


def main():
	parser = argparse.ArgumentParser(description="Photo Matching Embedding Generator")
	parser.add_argument("--engine", choices=["insightface", "face_recognition"], default="insightface",
						help="Embedding backend to use")
	args = parser.parse_args()

	if args.engine == "face_recognition":
		if not HAS_FR:
			print("face_recognition backend not available; falling back to insightface")
			args.engine = "insightface"

	if args.engine == "insightface":
		image_paths, labels = if_load_images(IF_IMAGE_DIR)
		embeddings = if_encode_faces(image_paths, labels)
		with open(IF_OUTPUT, "wb") as f:
			pickle.dump(embeddings, f)
		print(f"✅ Saved {len(embeddings)} embeddings to {IF_OUTPUT} using InsightFace")
	else:
		image_paths, labels = fr_load_images(FR_IMAGE_DIR)
		embeddings = fr_encode_faces(image_paths, labels)
		with open(FR_OUTPUT, "wb") as f:
			pickle.dump(embeddings, f)
		print(f"✅ Saved {len(embeddings)} embeddings to {FR_OUTPUT} using face_recognition")


if __name__ == "__main__":
	main()
