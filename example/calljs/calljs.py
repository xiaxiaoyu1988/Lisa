import os
import sys
import threading

sys.path.append(r"../../src")
from lisa import App

def calljs(app):
    app.execute_js_function("lisa_alert", "calljs")

def main():
    app = App()
    client_path = "file://" +  os.getcwd() + "/index.html"
    app.init(client_path)
    arg = [app]
    # Sleep 10 seconds for wait DOM load completed
    threading.Timer(10, calljs, arg).start()
    app.run()

if __name__ == '__main__':
    main()

