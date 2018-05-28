'''
File: platform.py
Project: lisa
File Created: Friday, 25th May 2018 4:17:43 pm
Author: xiaxiaoyu (<<xyyvsxh@gmail.com>>)
-----
Copyright All Rights Reserved - 2018
'''
import os
import win32api
import win32con
import win32gui
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
        self.browser  = None
            
        self.WindowUtils = cef.WindowUtils()
        
        self.window_proc = {
            win32con.WM_CLOSE: self.close_window,
            win32con.WM_DESTROY: self.exit_app,
            win32con.WM_SIZE: self.WindowUtils.OnSize,
            win32con.WM_SETFOCUS: self.WindowUtils.OnSetFocus,
            win32con.WM_ERASEBKGND: self.WindowUtils.OnEraseBackground
        }

        self.window_handle = None
        self.multi_threaded = multi_threaded

    
    def platform_create_window(self, title="lisa", class_name="lisa", width=800, height=600, icon="", frameless=False):
        
        self.window_handle = self.create_window(title=title,
                                      class_name=class_name,
                                      width=width,
                                      height=height,
                                      window_proc=self.window_proc,
                                      icon=icon)
        return self.window_handle
    
    def platform_create_browser(self, url):
        if self.multi_threaded:
            self.cef.PostTask(self.cef.TID_UI,
                              self.create_browser,
                              url)
        else:
            self.create_browser(url=url)


    def platform_message_loop(self):
        if self.multi_threaded:
            win32gui.PumpMessages()
        else:
            self.cef.MessageLoop()

    def create_browser(self, url):
        assert(self.cef.IsThread(self.cef.TID_UI))
        self.browser = self.cef.CreateBrowserSync(window_info=self.window_info,
                            settings={},
                            url=url)


    def create_window(self, title, class_name, width, height, window_proc, icon):
        # Register window class
        wndclass = win32gui.WNDCLASS()
        wndclass.hInstance = win32api.GetModuleHandle(None)
        wndclass.lpszClassName = class_name
        wndclass.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
        wndclass.hbrBackground = win32con.COLOR_WINDOW
        wndclass.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        wndclass.lpfnWndProc = window_proc
        atom_class = win32gui.RegisterClass(wndclass)
        assert(atom_class != 0)

        # Center window on screen.
        screenx = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screeny = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        xpos = int(math.floor((screenx - width) / 2))
        ypos = int(math.floor((screeny - height) / 2))
        if xpos < 0:
            xpos = 0
        if ypos < 0:
            ypos = 0

        # Create window
        # window_style = (win32con.WS_OVERLAPPEDWINDOW | win32con.WS_CLIPCHILDREN
            # | win32con.WS_VISIBLE |win32con.WS_POPUP)
        window_style = win32con.WS_VISIBLE | win32con.WS_POPUP
        # window_style = ~win32con.WS_CAPTION &~win32con.WS_SYSMENU &~win32con.WS_SIZEBOX;
        window_style &= ~win32con.WS_HSCROLL & ~win32con.WS_VSCROLL
        window_handle = win32gui.CreateWindow(class_name, title, window_style,
                                            xpos, ypos, width, height,
                                            0, 0, wndclass.hInstance, None)
        assert(window_handle != 0)

        # # Window icon
        icon = os.path.abspath(icon)
        if not os.path.isfile(icon):
            icon = None
        if icon:
            # Load small and big icon.
            # WNDCLASSEX (along with hIconSm) is not supported by pywin32,
            # we need to use WM_SETICON message after window creation.
            # Ref:
            # 1. http://stackoverflow.com/questions/2234988
            # 2. http://blog.barthe.ph/2009/07/17/wmseticon/
            bigx = win32api.GetSystemMetrics(win32con.SM_CXICON)
            bigy = win32api.GetSystemMetrics(win32con.SM_CYICON)
            big_icon = win32gui.LoadImage(0, icon, win32con.IMAGE_ICON,
                                        bigx, bigy,
                                        win32con.LR_LOADFROMFILE)
            smallx = win32api.GetSystemMetrics(win32con.SM_CXSMICON)
            smally = win32api.GetSystemMetrics(win32con.SM_CYSMICON)
            small_icon = win32gui.LoadImage(0, icon, win32con.IMAGE_ICON,
                                            smallx, smally,
                                            win32con.LR_LOADFROMFILE)
            win32api.SendMessage(window_handle, win32con.WM_SETICON,
                                win32con.ICON_BIG, big_icon)
            win32api.SendMessage(window_handle, win32con.WM_SETICON,
                                win32con.ICON_SMALL, small_icon)

        return window_handle


    def close_window(self, window_handle, message, wparam, lparam):
        browser = self.cef.GetBrowserByWindowHandle(window_handle)
        browser.CloseBrowser(True)
        # OFF: win32gui.DestroyWindow(window_handle)
        return win32gui.DefWindowProc(window_handle, message, wparam, lparam)


    def exit_app(self, *_):
        win32gui.PostQuitMessage(0)
        return 0
