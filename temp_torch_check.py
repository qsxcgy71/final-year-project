import torch
print("torch", torch.__version__)
print("cuda available", torch.cuda.is_available())
PY = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "-"
print("cuda device", PY)
