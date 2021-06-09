import os

static_filepath = os.path.join("tree", "backend", "static")
tests_filepath = os.path.join("tree", "backend", "tests")

backup_filepath = os.path.join(static_filepath, "backups")
cropped_faces_filepath = os.path.join(static_filepath, "cropped_faces")
test_images_filepath = os.path.join(tests_filepath, "images")

pickle_storage_filename = "backup"

cropped_face_extension = ".jpg"
