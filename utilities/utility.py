# coding: UTF-8
import sys
import os
import os.path
from pprint import pprint

# 絶対パス取得
def get_pass(target):
    return os.path.join(os.path.dirname(__file__), '../' + target)

# オブジェクトダンプ
def dump(data):
    pprint(vars(data))
    sys.exit()