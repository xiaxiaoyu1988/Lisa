import os
import sys

sys.path.append(r"../../src")
from lisa import App, route

@route('/')
def index():
    return '{"a":"b"}'


def main():
    app = App()
    client_path = "file://" +  os.getcwd() + "/client/login.html"
    app.init(client_path, debug=True)
    app.run()

if __name__ == '__main__':
    main()

