import face_recognition
import os

import tree.backend.constants as constants

filepath1 = os.path.join(constants.test_img_dir, "yash1.jpg")
filepath2 = os.path.join(constants.test_img_dir, "yash2.jpg")

yash1_face = face_recognition.load_image_file(filepath1)
yash2_face = face_recognition.load_image_file(filepath2)

yash1_encoding = face_recognition.face_encodings(yash1_face)[0]
yash2_encoding = face_recognition.face_encodings(yash2_face)[0]

results = face_recognition.compare_faces([yash1_encoding], yash2_encoding)



def main():
    pass


if __name__ == '__main__':
    main()