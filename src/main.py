# main.py

import os
os.system("sudo chmod 777 /dev/ttyAMA0")  # 赋予串口读写权限

from recognizer import Recognizer

def main():
    # initialize `rmyc_bridge`
    # if failed 2 initlize, it throws an error.
    import rmyc_bridge

    # initialize recognizer
    recognizer = Recognizer()


if __name__ == "__main__":
    main()
