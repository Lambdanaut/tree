import time

import tree.backend.faces as faces


def run(f: "faces.Faces"):
    print("Tree initialized")
    print("Now detecting faces...")

    while True:
        try:
            face = f.snap_face()
        except faces.FaceNotFoundException:
            print("Error: No face found")
            continue
        except faces.PreExistingFaceFoundException as exc:
            # Preexisting face found in the database. Use that instead
            print("\nWe recognize your face! Welcome back! ")
            face = exc.preexisting_face
        else:
            print("\nWelcome new face! We will remember you! ")

        print("\nWould you like to read your messages? Y/N")
        i = input(" > ").lower()

        if i == 'y':
            print("\nHere are your messages:")
            for message in face.messages:
                print(" * \"{}\"".format(message))

        while True:
            print("\nWould you like to send a new message? Y/N")
            i = input(" > ").lower()

            if i == 'y':
                print("\nWhat message would you like to send this person?")
                message = input(" > ")
                f.add_message(face, message)
                print("\nMessage successfully added!")
            else:
                break

        print("\nThank you for talking to A Tree")
        time.sleep(2)
