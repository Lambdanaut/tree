import os

import pyASCIIgenerator

import tree.backend.constants as constants
import tree.backend.faces as faces


def run(f: "faces.Faces"):
    print("Tree initialized")

    while True:
        print("Now detecting faces...")
        try:
            face = f.snap_face()
        except faces.FaceNotFoundException:
            print("Error: No face found")
            continue
        except faces.PreExistingFaceFoundException as exc:
            # Preexisting face found in the database. Use that instead
            print("\n We recognize your face! Welcome back! ")
            face = exc.preexisting_face
        else:
            print("\n Welcome new face! We will remember you! ")
            face.show_cropped_image()

        if face.messages:
            print(" Would you like to read your `{}` messages? Y/N".format(len(face.messages)))
            i = input(" > ").lower()

            if i == 'y':
                print("\nHere are your messages:")
                for i in range(len(face.messages)):
                    print(" * \"{}\"".format(face.consume_message()))
        else:
            print(" You have `0` new messages.")

        while True:
            print("\nWould you like to send a new message? Y/N")
            i = input(" > ").lower()

            if i == 'y':
                for other_face in f:

                    # Commented out code to show the cropped photo as a popup
                    # other_face.show_full_image()

                    # Show an ASCII image of the person's cropped photo
                    pyASCIIgenerator.asciify(os.path.join(
                        constants.cropped_faces_filepath,
                        other_face.cropped_image_filename))

                    print("\nWould you like to message this person? Y/N")
                    i = input(" > ").lower()
                    if i == 'y':
                        print("\nWhat message would you like to send this person?")
                        message = input(" > ")
                        f.add_message(other_face, message)
                        print("\nMessage successfully added!")
            else:
                break

        print("\n\n\nThank you for talking to A Tree")
        print("===============================\n")
