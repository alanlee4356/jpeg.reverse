import string
import re

f = open("bip39words.txt", 'r+')
data = f.read()

wordlist = data.split()

f.write(wordlist)
# f.write(dataa)
f.close()