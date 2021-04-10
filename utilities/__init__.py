# coding: UTF-8
import sys
import os.path
import glob
import importlib
import re

this_pass = os.path.dirname(os.path.abspath(__file__))

# ディレクトリ内オートロード
def loadModule():
    myself = sys.modules[__name__]

    # pythonファイルを読み込み
    mod_paths = glob.glob(os.path.join(this_pass, '*.py'))
    for file in mod_paths:
        mod_name = os.path.splitext(os.path.basename(file))[0]

        # initファイルは除外
        if re.search('.*__init__.*', mod_name) is None:
            module = importlib.import_module(__name__ + '.' + mod_name)

            for mod in module.__dict__.keys():
                if not mod in ['__builtins__', '__doc__', '__file__', '__name__', '__package__']:
                    myself.__dict__[mod] = module.__dict__[mod]

loadModule()