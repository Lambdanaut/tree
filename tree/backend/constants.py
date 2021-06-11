import os

static_filepath = os.path.join("tree", "backend", "static")
tests_filepath = os.path.join("tree", "backend", "tests")

backup_filepath = os.path.join(static_filepath, "backups")
cropped_faces_filepath = os.path.join(static_filepath, "cropped_faces")
fresh_photos_filepath = os.path.join(static_filepath, "fresh_photos")
test_images_filepath = os.path.join(tests_filepath, "images")

pickle_storage_filename = "backup"

cropped_face_extension = ".jpg"
fresh_photos_extension = ".jpg"
