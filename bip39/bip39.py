import string
import re
from bidict import bidict
import random

HUFFMAN_CATEGORY_CODEWORD = bidict(
    {

        'e' : '100',
        'a' : '0000',
        'r' : '0001',
        't' : '0011',
        'o' : '0100',
        'i' : '0101',
        'n' : '0111',
        's' : '1010',
        'l' : '1100',
        'c' : '1110',
        'u' : '00100',
        'd' : '01100',
        'p' : '01101',
        'm' : '10110',
        'h' : '11010',
        'g' : '11011',
        'b' : '11111',
        'y' : '001010',
        'f' : '001011',
        'w' : '101110',
        'v' : '101111',
        'k' : '111100',
        'x' : '11110100',
        'z' : '11110101',
        'j' : '11110110',
        'q' : '11110111'
}
    )


def countalp(data):
    for chr in data:

        if chr != '\n':
            if chr in alp:

                alp[chr] += 1
            

            else :

                alp[chr]= 1

def encode_huffman(sampleList):
    bits = ''
    for word in sampleList:
        for i in word:
            bits+= HUFFMAN_CATEGORY_CODEWORD[i]
    return bits

def flip(arr):
    arr1 = list(arr)
    for i in range(len(arr1)):
        if arr1[i] == '1':
            arr1[i] = '0'
        elif arr1[i] == '0':
            arr1[i] = '1'
    
    arr = ''.join(arr1)
    return arr

f = open("bip39/bip39words.txt", 'r+') # file 읽기
data = f.read()                   
encoded_bits = ''
flipped_bits = ''

wordList = data.split()
# sampleList = random.sample(wordList, 100)
sampleList = wordList[0:100]

encoded_bits = encode_huffman(sampleList)

for i in range (0,int(len(encoded_bits)/100),1):
    flipped_bits +=flip(encoded_bits[i*100:i*100+100])


    






alp = {}#alphabet

countalp(data)
sort_alp = sorted(alp.items(), key = lambda pair : pair[1], reverse=True)#빈도가 높은순으로 정렬
print(sort_alp)
print(sum(alp.values()))



# f.write(dataa)
f.close()