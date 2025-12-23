import torch, traceback, sys, os
p = 'models/best (1).pt'
out = 'models/best_weights_only.pt'
print('Loading checkpoint (weights_only=False):', p)
try:
    ckpt = torch.load(p, map_location='cpu', weights_only=False)
    print('Loaded checkpoint type:', type(ckpt))
except Exception as e:
    print('ERROR loading checkpoint:', e)
    traceback.print_exc()
    sys.exit(1)

model_obj = ckpt.get('model', None) if isinstance(ckpt, dict) else None
if model_obj is None:
    print('No model object in checkpoint -- trying to locate state_dict directly')
    if isinstance(ckpt, dict) and any(isinstance(v, dict) for v in ckpt.values()):
        # try to find a nested state_dict
        for k,v in ckpt.items():
            if isinstance(v, dict) and all(hasattr(val, 'dtype') if hasattr(val, 'dtype') else True for val in v.values()):
                print('Found possible state_dict under key:', k)
                sd = v
                break
        else:
            print('Could not find state_dict in checkpoint')
            sys.exit(2)
else:
    sd = None
    # try common ways to get state dict
    try:
        sd = model_obj.state_dict()
        print('Obtained state_dict via model_obj.state_dict()')
    except Exception as e:
        print('state_dict() failed:', e)
        try:
            sd = getattr(model_obj, 'model').state_dict()
            print('Obtained state_dict via model_obj.model.state_dict()')
        except Exception as e2:
            print('model_obj.model.state_dict() failed:', e2)

if sd is None:
    print('Failed to extract state_dict from checkpoint model object')
    sys.exit(3)

print('Saving weights-only checkpoint to:', out)
try:
    torch.save({'model': sd}, out)
    print('Saved', out)
except Exception as e:
    print('ERROR saving weights-only checkpoint:', e)
    traceback.print_exc()
    sys.exit(4)

# Try loading the new weights-only file with YOLO
print('Verifying YOLO can load the new weights-only file...')
try:
    from ultralytics import YOLO
    m = YOLO(out)
    print('YOLO loaded weights-only file successfully:', type(m))
except Exception as e:
    print('YOLO failed to load weights-only file:', e)
    traceback.print_exc()
    sys.exit(5)

print('Conversion and verification complete')
