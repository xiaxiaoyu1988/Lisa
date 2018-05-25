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

current_platform = platform.system()
if current_platform == "Windows":
    import _platform.windows as _pw
elif current_platform == "Darwin":
    import _platform.macosx as _pw


class App(object):
    def __init__(self):
        pass
    
    def init(self, client_file_path = "file://client/index.html"):
        # command_line_args()
        check_versions()
        sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error

        settings = {
            "multi_threaded_message_loop": False,
        }
        cef.Initialize(settings=settings)

        window_info = cef.WindowInfo()
        client_window = _pw.Window(
            cef=cef, window_info=window_info, settings=settings)
        window_handle = client_window.platform_create_browser()

        if current_platform != "Darwin":
            window_info.SetAsChild(window_handle)

        client_window.platform_message_loop(client_file_path)
        cef.Shutdown()

    
    def run(self):
        pass

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
