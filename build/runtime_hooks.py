import sys
import os

if getattr(sys, "frozen", False):
    base = getattr(sys, "_MEIPASS", None)
    if base:
        src_path = os.path.join(base, "src")
        if os.path.isdir(src_path) and src_path not in sys.path:
            sys.path.insert(0, src_path)
