import os
import sys

sys.path.append(r"../../src")
from lisa import App

def main():
    app = App()
    client_path = "file://" +  os.getcwd() + "/client/index.html"
    app.init(client_path)
    app.run()

if __name__ == '__main__':
    main()

