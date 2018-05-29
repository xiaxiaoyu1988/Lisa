import os
import sys

sys.path.append(r"../../src")
from lisa import App, route

@route('/')
def index():
    return '{"a":"b"}'


def main():
    app = App()
    client_path = "http://127.0.0.1:8080/"
    app.init(client_path, debug=True)
    app.run()

if __name__ == '__main__':
    main()

