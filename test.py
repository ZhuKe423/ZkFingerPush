# -*- coding: utf-8 -*-
from functools import wraps

def deco_entity(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        print(func.__name__+" decorater in")
        handle = func(*args, **kwargs)
        print(func.__name__ + " decorater out")
        return handle
    return decorated


class test_a():
    def __init__(self):
        self.m_donkey = 'this is my donkey!!'
    @deco_entity
    def aaa(self):
        print("this is aaa function!!!")
        self.bbb()
        print(self.m_donkey)

    def bbb(self):
        print("this is bbb function!!!")


if __name__ == "__main__":
    b = test_a()
    b.aaa()

