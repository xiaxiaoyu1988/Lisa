'''
File: platform.py
Project: lisa
File Created: Friday, 25th May 2018 4:17:43 pm
Author: xiaxiaoyu (<<xyyvsxh@gmail.com>>)
-----
Copyright All Rights Reserved - 2018
'''
import os
import math

from _platform_exception import PlatformException


class Window(object):
    def __init__(self, cef=None, window_info=None, settings={}, multi_threaded=False):
        if not cef:
            raise PlatformException("cef is NULL")
        else:
            self.cef = cef

        if not window_info:
            raise PlatformException("window_info is NULL")
        else:
            self.window_info = window_info

        self.settings = settings

        self.WindowUtils = cef.WindowUtils()

        self.window_handle = None
        self.multi_threaded = multi_threaded

    def platform_create_browser(self, title="lisa", class_name="lisa", width=800, height=600, icon="", frameless=False):

        pass

    def platform_message_loop(self, url):
        print("client url:", url)
        self.create_browser(url=url)
        self.cef.MessageLoop()

    def create_browser(self, url):
        assert(self.cef.IsThread(self.cef.TID_UI))
        self.cef.CreateBrowserSync(window_info=self.window_info,
                                   settings={},
                                   url=url)

    def create_window(self, title, class_name, width, height, icon):
        pass

    def close_window(self, window_handle, message, wparam, lparam):
        browser = self.cef.GetBrowserByWindowHandle(window_handle)
        browser.CloseBrowser(True)
        # OFF: win32gui.DestroyWindow(window_handle)
        # return win32gui.DefWindowProc(window_handle, message, wparam, lparam)

    def exit_app(self, *_):
        # win32gui.PostQuitMessage(0)
        return 0
