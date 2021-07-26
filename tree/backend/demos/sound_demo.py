import os
import time
import uuid

import pyASCIIgenerator

import tree.backend.constants as constants
import tree.backend.audio as audio
import tree.backend.faces as faces


def run(f: "faces.Faces"):
    wa = audio.WavAudio()
    wa.calibrate(show_demo_text=True, play_demo_audio=True)  # Calibrates the silence threshold

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
            # Show your face as ASCII
            pyASCIIgenerator.asciify(os.path.join(
                constants.cropped_faces_filepath,
                face.cropped_image_filename))

        if face.messages:
            print(" Would you like to hear your `{}` messages? Y/N".format(len(face.messages)))
            i = input(" > ").lower()

            if i == 'y':
                print("\nHere are your messages:")
                for _ in range(len(face.messages)):
                    message = face.consume_message()
                    print(" * \"{}\"".format(message))
                    wa.play(message)
        else:
            print(" You have `0` new messages.")

        while True:
            print("\nWould you like to send a new message? Y/N")
            i = input(" > ").lower()

            if i == 'y':
                for other_face in f:

                    # Show an ASCII image of the person's cropped photo
                    pyASCIIgenerator.asciify(os.path.join(
                        constants.cropped_faces_filepath,
                        other_face.cropped_image_filename))

                    print("\nWould you like to message this person? Y/N")
                    i = input(" > ").lower()
                    if i == 'y':
                        print("\nSpeak your message to this person now.")
                        time.sleep(0.2)  # Shortest of sleeps
                        message_id: str = str(uuid.uuid4())
                        message_filename = "{}.wav".format(message_id)
                        wa.record(message_filename)
                        f.add_message(other_face, message_filename)
                        print("\nMessage successfully added!")
            else:
                break

        print("\n\n\nThank you for talking to A Tree")
        print("===============================\n")
