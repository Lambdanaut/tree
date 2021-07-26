import sys

sys.path.append('.')

import tree.backend.demos.prompt_demo as prompt_demo
import tree.backend.demos.sound_demo as sound_demo
from tree.backend.storage.pickle_storage import pickle_storage


def main():
    # Load the record of seen faces and messages
    f = pickle_storage.load()

    # Run the demo
    sound_demo.run(f)


if __name__ == '__main__':
    main()
