import os
import sys
import time

from app.core.app import SmartDisplayApp


def main() -> None:
    app = SmartDisplayApp()
    app.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")

