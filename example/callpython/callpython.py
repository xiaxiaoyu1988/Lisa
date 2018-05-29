import os
import sys
import threading

sys.path.append(r"../../src")
from lisa import App

def python_function(param):
    print "called from python, js var is " + param
    return "called from python, js var is " + param

class demo(object):
    def __init__(self, app):
        self.app = app
    
    def test_demo(self, js_callback):
        self.app.execute_js_function("js_log", "demo.test_demo", "called from python")
        if js_callback:
            js_callback.Call("demo.test_demo", "string send from python")

def main():
    app = App()
    client_path = "file://" +  os.getcwd() + "/index.html"
    app.init(client_path)

    demo_obj = demo(app)
    app.bindings.SetProperty("lisa_var", "This property was set in Python")
    app.bindings.SetProperty("lisa_version", app.version())
    app.bindings.SetFunction("python_function", python_function)
    app.bindings.SetObject("demo_obj", demo_obj)

    app.run()

if __name__ == '__main__':
    main()

