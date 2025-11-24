mods = ['PIL','ultralytics','cv2','numpy','torch']
import importlib
for m in mods:
    try:
        mod = importlib.import_module(m)
        v = getattr(mod, '__version__', None)
        print(f"{m} OK", v)
    except Exception as e:
        print(f"{m} ERR", e)
