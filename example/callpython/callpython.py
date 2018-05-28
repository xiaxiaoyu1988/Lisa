import os
import sys
import threading

sys.path.append(r"../../src")
from lisa import App

def python_function(param):
    print "called from python, js var is " + param
    return "called from python, js var is " + param

def main():
    app = App()
    client_path = "file://" +  os.getcwd() + "/index.html"
    app.init(client_path)
    bindings = app.new_bindings()
    bindings.SetProperty("lisa_var", "This property was set in Python")
    bindings.SetProperty("lisa_version", app.version())
    bindings.SetFunction("python_function", python_function)
    app.bind_python_to_js(bindings)

    app.run()

if __name__ == '__main__':
    main()

