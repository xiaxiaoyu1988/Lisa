'''
File: platform.py
Project: lisa
File Created: Friday, 25th May 2018 4:17:43 pm
Author: xiaxiaoyu (<<xyyvsxh@gmail.com>>)
-----
Copyright All Rights Reserved - 2018
'''

class PlatformException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)