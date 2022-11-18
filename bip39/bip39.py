import string
import re
from bidict import bidict

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

        if chr is not '\n':
            if chr in alp:

                alp[chr] += 1
            

            else :

                alp[chr]= 1


f = open("bip39/bip39words.txt", 'r+') # file 읽기
data = f.read()


# wordlist = data.split()
# print(wordlist)

alp = {}#alphabet

countalp(data)
sort_alp = sorted(alp.items(), key = lambda pair : pair[1], reverse=True)#빈도가 높은순으로 정렬
print(sort_alp)
print(sum(alp.values()))



# f.write(dataa)
f.close()