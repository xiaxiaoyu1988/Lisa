'''
File: platform.py
Project: lisa
File Created: Friday, 25th May 2018 4:17:43 pm
Author: xiaxiaoyu (<<xyyvsxh@gmail.com>>)
-----
Copyright All Rights Reserved - 2018
'''
from cefpython3 import cefpython as cef

import distutils.sysconfig
import os
import platform
import _platform
import sys
import threading
import time

current_platform = platform.system()
if current_platform == "Windows":
    import _platform.windows as _pw
elif current_platform == "Darwin":
    import _platform.macosx as _pw

from webserver import *

wserver = Webserver()
route = make_app_wrapper("route", wserver)
class App(object):
    def __init__(self):
        self.client_window = None
        self.client_file_path = ""
        self.wserver = wserver
        self.wserver.set_app(self)
        self.wserver.setDaemon(True)

    def init(self, client_file_path = "file://client/index.html", debug=False):
        # command_line_args()
        check_versions()
        if not debug:
            sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
        self.client_file_path = client_file_path
        settings = {
            "multi_threaded_message_loop": False,
        }
        cef.Initialize(settings=settings)

        window_info = cef.WindowInfo()
        self.client_window = _pw.Window(
            cef=cef, window_info=window_info, settings=settings)
        window_handle = self.client_window.platform_create_window()

        if current_platform != "Darwin":
            window_info.SetAsChild(window_handle)
        
        self.client_window.platform_create_browser(self.client_file_path)
        
    
    def new_bindings(self, bindToFrames=False, bindToPopups=False):
        return cef.JavascriptBindings(
            bindToFrames=bindToFrames, bindToPopups=bindToPopups)
    
    def bind_python_to_js(self, bindings):
        self.client_window.browser.SetJavascriptBindings(bindings)
    
    def execute_js_function(self, function_name, *params):
        self.client_window.browser.ExecuteFunction(function_name, *params)
    
    def run(self):
        self.wserver.start()
        self.client_window.platform_message_loop()
        cef.Shutdown()

    def version(self):
        return "1.0"

def command_line_args():
    global g_multi_threaded
    if "--multi-threaded" in sys.argv:
        sys.argv.remove("--multi-threaded")
        print("[pywin32.py] Message loop mode: CEF multi-threaded"
              " (best performance)")
        g_multi_threaded = True
    else:
        print("[pywin32.py] Message loop mode: CEF single-threaded")
    if len(sys.argv) > 1:
        print("ERROR: Invalid args passed."
              " For usage see top comments in pywin32.py.")
        sys.exit(1)


def check_versions():
    assert cef.__version__ >= "57.0", "CEF Python v57.0 required to run this"


if __name__ == '__main__':
    app = App()
    app.init()
    app.run()
