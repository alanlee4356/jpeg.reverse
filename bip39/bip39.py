import string
import re
from bidict import bidict
import random
import math

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

def decode_huffman(bit_seq):#철자하나씩 디코딩하는데 단어의 시작과끝을 구분못함 스페이스바나 개행문자를 문자의끝으로 인식시켜야할듯
    def diff_value(idx, size):
        if idx >= len(bit_seq) or idx + size > len(bit_seq):
            raise IndexError('There is not enough bits to decode DIFF value '
                             'codeword.')
        fixed = bit_seq[idx:idx + size]
        return int(fixed, 2)
    current_idx = 0
    while current_idx < len(bit_seq):
        remaining_len = len(bit_seq) - current_idx
        current_slice = bit_seq[
            current_idx:
            current_idx + (8 if remaining_len > 8 else remaining_len)
        ]
        
        while current_slice:
            if (current_slice in HUFFMAN_CATEGORY_CODEWORD.inv):
                key = (HUFFMAN_CATEGORY_CODEWORD.inv[current_slice])
                
                return key,bit_seq[len(current_slice):]
            
            current_slice = current_slice[:-1]

def decoding(remain_bits):
    while True:
        word,remain_bits = decode_huffman(remain_bits)
        decoded_words.append(word)
        if len(remain_bits) == 0:
            break
    return decoded_words

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
decoded_words =[]

wordList = data.split()
# sampleList = random.sample(wordList, 100)
sampleList = wordList[0:10]

encoded_bits = encode_huffman(sampleList)



for i in range (0,int(math.ceil(len(encoded_bits)/10)),1):
    flipped_bits +=flip(encoded_bits[i*10:i*10+10])
    
decoding(encoded_bits)
decoding(flipped_bits)#flip된거 디코딩하면 비트가 남는데 그러면 되돌아가서 플립해야함 결국엔 jpeg랑 다를게없음.



    






alp = {}#alphabet

countalp(data)
sort_alp = sorted(alp.items(), key = lambda pair : pair[1], reverse=True)#빈도가 높은순으로 정렬
print(sort_alp)
print(sum(alp.values()))



# f.write(dataa)
f.close()