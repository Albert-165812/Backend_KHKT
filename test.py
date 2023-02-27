import binascii

data = u'tạm biệt'
print(data) # tạm biệt

a = binascii.hexlify(data.encode('cp1258', errors='backslashreplace'))
print(a) # b'745c75316561316d2062695c753165633774'
# if i dont use the error handler here, then I get a UnicodeEncodeError for \u1ea1

print(
    binascii.unhexlify(a).decode('unicode-escape') # tạm biệt
)