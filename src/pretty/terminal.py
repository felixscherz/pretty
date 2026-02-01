import pty
import os
import select
import sys
import threading
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
        assert_never()

    # main process


    def read_from_stdin():
        while True:
            r, _, _ = select.select([sys.stdin.fileno()], [], [], 0.1)
            if r:
                data = os.read(sys.stdin.fileno(), 1024)
                os.write(controller, data)


    def write_from_controller():
        while True:
            r, _, _ = select.select([controller], [], [], 0.1)
            if r:
                data = os.read(r[0], 1024)
                # don't print, this would include the ANSI escape sequences
                # print(data)
                sys.stdout.buffer.write(data)
                sys.stdout.buffer.flush()



    read_thread = threading.Thread(target=read_from_stdin, daemon=True)
    write_thread = threading.Thread(target=write_from_controller, daemon=True)

    read_thread.start()
    write_thread.start()


    read_thread.join()
    write_thread.join()



if __name__ == "__main__":
    main()


