#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Script minimale per avviare il gioco.
"""

# PyChecker
#import os
#os.environ["PYCHECKER"] = "--stdlib"
#import pychecker.checker

if __name__ == "__main__":
    from src.engine import engine
    engine.start()
