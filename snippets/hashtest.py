import hashlib

print(hashlib.algorithms_guaranteed)

h = hashlib.sha256()
h.update("My content".encode('utf-8'))
print(h.hexdigest())
print(h.digest())

file = "./snippets/node-step.py"
BLOCK_SIZE = 65536 # 64 kb

file_hash = hashlib.sha256()
with open(file, 'rb') as f:
    fb = f.read(BLOCK_SIZE)
    while len(fb) > 0:
        file_hash.update(fb)
        fb = f.read(BLOCK_SIZE)

print(file_hash.hexdigest())
hash = "a4cf4d17f838f0b9db00e76b31e02ca1dc6005185dd54f67b240306c0f77b2db"