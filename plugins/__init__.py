# ════════════════════════════════════════
#  Satoru — Plugin Auto-Loader
# ════════════════════════════════════════
import glob
import importlib
import os

_plugin_dir = os.path.dirname(__file__)

def load_all():
    files = sorted(glob.glob(os.path.join(_plugin_dir, "*.py")))
    loaded = []
    for f in files:
        name = os.path.basename(f)[:-3]
        if name.startswith("_"):
            continue
        try:
            importlib.import_module(f"plugins.{name}")
            loaded.append(name)
        except Exception as e:
            print(f"  ✗ plugins/{name}: {e}")
    return loaded
