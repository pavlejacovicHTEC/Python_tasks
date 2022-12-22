import threading

def print_custom_message(message):
    print("{} ".format(threading.current_thread().name)+"says "+ message)

def print_hello_message():
    print("{} ".format(threading.current_thread().name)+"says Hello")

#Allows you to execute code when the File Runs as a Script, but Not When It's imported as Module.
if __name__ == "__main__":
    # Create a new daemon thread
    # Deamon means the thread will exit when the main program exits
    t1 = threading.Thread(target=print_custom_message, daemon=True, args=("Hello from a thread!",))
    t2 = threading.Thread(target=print_hello_message, daemon=True)

    # Start thread 1
    t1.start()
    # Start thread 2
    t2.start()

    # Main program will wait until thread 1 is completely executed
    t1.join()
    # Main program will wait until thread 2 is completely executed
    t2.join()

    print("Done!")