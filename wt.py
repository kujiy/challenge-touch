import pykakasi
kks = pykakasi.kakasi()
text = "一番難しいのは最初の一歩である。"
result = kks.convert(text)
for item in result:
    print(item['hira'])

