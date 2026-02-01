import pty
import os
import time
import sys
import tkinter
from typing import assert_never

# 1. get a pty 
# 2. fork the process

def main():
    # this opens a pair of file descriptors
    controller, client = pty.openpty()

    # get a new process to run bash
    pid = os.fork()

    if pid == 0:
        # child process

        os.dup2(client, 0) # stdin
        os.dup2(client, 1) # stdout
        os.dup2(client, 2) # stderr
        os.execv("/bin/zsh", ["/bin/zsh"])
        time.sleep(5)
        assert_never()

    # main process



    ...

    time.sleep(5)

if __name__ == "__main__":
    main()


