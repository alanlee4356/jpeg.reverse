import string
import re


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



# f.write(dataa)
f.close()