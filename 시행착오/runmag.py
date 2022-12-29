import csv
import itertools
from math import ceil
import time
from bidict import bidict
from unittest import result
from matplotlib import pyplot as plt
from matplotlib import image as img
import numpy as np
from PIL import Image
from scipy.fftpack import dct, idct
np.set_printoptions(precision=6, suppress=True)

QUANTIZATION_TABLE = np.array((
    (16, 11, 10, 16, 24, 40, 51, 61),
    (12, 12, 14, 19, 26, 58, 60, 55),
    (14, 13, 16, 24, 40, 57, 69, 56),
    (14, 17, 22, 29, 51, 87, 80, 62),
    (18, 22, 37, 56, 68, 109, 103, 77),
    (24, 36, 55, 64, 81, 104, 113, 92),
    (49, 64, 78, 87, 103, 121, 120, 101),
    (72, 92, 95, 98, 112, 100, 103, 99)
))
EOB = (0, 0)
ZRL = (15, 0)
DC = 'DC'
AC = 'AC'
zigzag_table = [0, 1, 8, 16, 9, 2, 3, 10, 17, 24, 32, 25, 18, 11, 4, 5, 12, 19, 26,
                33, 40, 48, 41, 34, 27, 20, 13, 6, 7, 14, 21, 28, 35, 42, 49, 56, 57, 50, 43, 36, 29,
                22, 15, 23, 30, 37, 44, 51, 58, 59, 52, 45, 38, 31, 39, 46, 53, 60, 61, 54, 47, 55, 62, 63]


HUFFMAN_CATEGORIES = (
    (0, ),
    (-1, 1),
    (-3, -2, 2, 3),
    (*range(-7, -4 + 1), *range(4, 7 + 1)),
    (*range(-15, -8 + 1), *range(8, 15 + 1)),
    (*range(-31, -16 + 1), *range(16, 31 + 1)),
    (*range(-63, -32 + 1), *range(32, 63 + 1)),
    (*range(-127, -64 + 1), *range(64, 127 + 1)),
    (*range(-255, -128 + 1), *range(128, 255 + 1)),
    (*range(-511, -256 + 1), *range(256, 511 + 1)),
    (*range(-1023, -512 + 1), *range(512, 1023 + 1)),
    (*range(-2047, -1024 + 1), *range(1024, 2047 + 1)),
    (*range(-4095, -2048 + 1), *range(2048, 4095 + 1)),
    (*range(-8191, -4096 + 1), *range(4096, 8191 + 1)),
    (*range(-16383, -8192 + 1), *range(8192, 16383 + 1)),
    (*range(-32767, -16384 + 1), *range(16384, 32767 + 1))
)

HUFFMAN_CATEGORY_CODEWORD = {
    DC: bidict({

        0:  '00',
        1:  '010',
        2:  '011',
        3:  '100',
        4:  '101',
        5:  '110',
        6:  '1110',
        7:  '11110',
        8:  '111110',
        9:  '1111110',
        10: '11111110',
        11: '111111110'
    }),
    AC: bidict({
        EOB: '1010',  # (0, 0)
        ZRL: '11111111001',  # (F, 0)

        (0, 1):  '00',
        (0, 2):  '01',
        (0, 3):  '100',
        (0, 4):  '1011',
        (0, 5):  '11010',
        (0, 6):  '1111000',
        (0, 7):  '11111000',
        (0, 8):  '1111110110',
        (0, 9):  '1111111110000010',
        (0, 10): '1111111110000011',

        (1, 1):  '1100',
        (1, 2):  '11011',
        (1, 3):  '1111001',
        (1, 4):  '111110110',
        (1, 5):  '11111110110',
        (1, 6):  '1111111110000100',
        (1, 7):  '1111111110000101',
        (1, 8):  '1111111110000110',
        (1, 9):  '1111111110000111',
        (1, 10): '1111111110001000',

        (2, 1):  '11100',
        (2, 2):  '11111001',
        (2, 3):  '1111110111',
        (2, 4):  '111111110100',
        (2, 5):  '1111111110001001',
        (2, 6):  '1111111110001010',
        (2, 7):  '1111111110001011',
        (2, 8):  '1111111110001100',
        (2, 9):  '1111111110001101',
        (2, 10): '1111111110001110',

        (3, 1):  '111010',
        (3, 2):  '111110111',
        (3, 3):  '111111110101',
        (3, 4):  '1111111110001111',
        (3, 5):  '1111111110010000',
        (3, 6):  '1111111110010001',
        (3, 7):  '1111111110010010',
        (3, 8):  '1111111110010011',
        (3, 9):  '1111111110010100',
        (3, 10): '1111111110010101',

        (4, 1):  '111011',
        (4, 2):  '1111111000',
        (4, 3):  '1111111110010110',
        (4, 4):  '1111111110010111',
        (4, 5):  '1111111110011000',
        (4, 6):  '1111111110011001',
        (4, 7):  '1111111110011010',
        (4, 8):  '1111111110011011',
        (4, 9):  '1111111110011100',
        (4, 10): '1111111110011101',

        (5, 1):  '1111010',
        (5, 2):  '11111110111',
        (5, 3):  '1111111110011110',
        (5, 4):  '1111111110011111',
        (5, 5):  '1111111110100000',
        (5, 6):  '1111111110100001',
        (5, 7):  '1111111110100010',
        (5, 8):  '1111111110100011',
        (5, 9):  '1111111110100100',
        (5, 10): '1111111110100101',

        (6, 1):  '1111011',
        (6, 2):  '111111110110',
        (6, 3):  '1111111110100110',
        (6, 4):  '1111111110100111',
        (6, 5):  '1111111110101000',
        (6, 6):  '1111111110101001',
        (6, 7):  '1111111110101010',
        (6, 8):  '1111111110101011',
        (6, 9):  '1111111110101100',
        (6, 10): '1111111110101101',

        (7, 1):  '11111010',
        (7, 2):  '111111110111',
        (7, 3):  '1111111110101110',
        (7, 4):  '1111111110101111',
        (7, 5):  '1111111110110000',
        (7, 6):  '1111111110110001',
        (7, 7):  '1111111110110010',
        (7, 8):  '1111111110110011',
        (7, 9):  '1111111110110100',
        (7, 10): '1111111110110101',

        (8, 1):  '111111000',
        (8, 2):  '111111111000000',
        (8, 3):  '1111111110110110',
        (8, 4):  '1111111110110111',
        (8, 5):  '1111111110111000',
        (8, 6):  '1111111110111001',
        (8, 7):  '1111111110111010',
        (8, 8):  '1111111110111011',
        (8, 9):  '1111111110111100',
        (8, 10): '1111111110111101',

        (9, 1):  '111111001',
        (9, 2):  '1111111110111110',
        (9, 3):  '1111111110111111',
        (9, 4):  '1111111111000000',
        (9, 5):  '1111111111000001',
        (9, 6):  '1111111111000010',
        (9, 7):  '1111111111000011',
        (9, 8):  '1111111111000100',
        (9, 9):  '1111111111000101',
        (9, 10): '1111111111000110',
        # A
        (10, 1):  '111111010',
        (10, 2):  '1111111111000111',
        (10, 3):  '1111111111001000',
        (10, 4):  '1111111111001001',
        (10, 5):  '1111111111001010',
        (10, 6):  '1111111111001011',
        (10, 7):  '1111111111001100',
        (10, 8):  '1111111111001101',
        (10, 9):  '1111111111001110',
        (10, 10): '1111111111001111',
        # B
        (11, 1):  '1111111001',
        (11, 2):  '1111111111010000',
        (11, 3):  '1111111111010001',
        (11, 4):  '1111111111010010',
        (11, 5):  '1111111111010011',
        (11, 6):  '1111111111010100',
        (11, 7):  '1111111111010101',
        (11, 8):  '1111111111010110',
        (11, 9):  '1111111111010111',
        (11, 10): '1111111111011000',
        # C
        (12, 1):  '1111111010',
        (12, 2):  '1111111111011001',
        (12, 3):  '1111111111011010',
        (12, 4):  '1111111111011011',
        (12, 5):  '1111111111011100',
        (12, 6):  '1111111111011101',
        (12, 7):  '1111111111011110',
        (12, 8):  '1111111111011111',
        (12, 9):  '1111111111100000',
        (12, 10): '1111111111100001',
        # D
        (13, 1):  '11111111000',
        (13, 2):  '1111111111100010',
        (13, 3):  '1111111111100011',
        (13, 4):  '1111111111100100',
        (13, 5):  '1111111111100101',
        (13, 6):  '1111111111100110',
        (13, 7):  '1111111111100111',
        (13, 8):  '1111111111101000',
        (13, 9):  '1111111111101001',
        (13, 10): '1111111111101010',
        # E
        (14, 1):  '1111111111101011',
        (14, 2):  '1111111111101100',
        (14, 3):  '1111111111101101',
        (14, 4):  '1111111111101110',
        (14, 5):  '1111111111101111',
        (14, 6):  '1111111111110000',
        (14, 7):  '1111111111110001',
        (14, 8):  '1111111111110010',
        (14, 9):  '1111111111110011',
        (14, 10): '1111111111110100',
        # F
        (15, 1):  '1111111111110101',
        (15, 2):  '1111111111110110',
        (15, 3):  '1111111111110111',
        (15, 4):  '1111111111111000',
        (15, 5):  '1111111111111001',
        (15, 6):  '1111111111111010',
        (15, 7):  '1111111111111011',
        (15, 8):  '1111111111111100',
        (15, 9):  '1111111111111101',
        (15, 10): '1111111111111110'
    })
}


def read_img(filename):
    with open(filename, 'rb') as file_object:
        ret = np.fromfile(file_object, dtype=np.uint8)
    return ret


def before_dct(arr):
    minus128 = np.zeros((8, 8), np.int8)
    for i in range(0, 8):
        for j in range(0, 8):
            minus128[i][j] = arr[i][j] - 128
    return minus128


def after_idct(arr):
    plus128 = np.zeros((8, 8), np.uint8)
    for i in range(0, 8):
        for j in range(0, 8):
            plus128[i][j] = arr[i][j] + 128
    return plus128


def dct2d(arr):
    # roundarr = np.zeros((8,8),np.float16)
    # dctarr = dct(dct(arr, norm='ortho', axis=0), norm='ortho', axis=1)
    # for i in range(0,8):
    #     for j in range(0,8):
    #         roundarr[i][j] = format(dctarr[i][j],'.8f')
    # return roundarr
    return dct(dct(arr, norm='ortho', axis=0), norm='ortho', axis=1)


def idct2d(arr):
    return np.int8(idct(idct(arr, norm='ortho', axis=0), norm='ortho', axis=1))


def quantize(block, inverse=False):  # jpeg퀄리티는 QUANTIZATION_TABLE값에 반비례

    quantization_table = QUANTIZATION_TABLE
    roundarr = np.zeros((8, 8), np.int8)

    if inverse:
        quantarr = block * (quantization_table)
        # return quantarr
        for i in range(0, 8):
            for j in range(0, 8):
                roundarr[i][j] = round(quantarr[i][j])
        return roundarr
    else:
        quantarr = block / (quantization_table)
        # return quantarr
        for i in range(0, 8):
            for j in range(0, 8):
                roundarr[i][j] = round(quantarr[i][j])
        return roundarr


def zigzag(arr):
    flat_arr = arr.flatten()
    z = 0
    zig_arr = np.zeros(64, np.int8)
    for i in zigzag_table:
        zig_arr[z] = flat_arr[i]
        z += 1

    return zig_arr


def izigzag(zig_arr):
    arr = np.zeros((8, 8), np.int8)
    z = 0
    for i in zigzag_table:
        arr[i//8][i % 8] = zig_arr[z]
        z += 1
    return arr


# def encode_differential(seq):
#     for idx, item in enumerate(seq):
#         if idx == 0:
#             dc_diff.append(item)
#         else:
#             dc_diff.append(item - seq[idx-1])

#     # dc diff 값을 계산해서 dcdiff 리스트 하나 만들어서 넣어둬야할듯

def encode_differential(dc):
    if len(dc_diff) == 0:
        dc_diff.append(dc)
    elif len(dc_diff) ==1:
        dc_diff.append(dc-dc_diff[len(dc_diff)-1])
        
    else:
        tmp = list(itertools.accumulate(dc_diff))
        dc_diff.append(dc-tmp[len(tmp)-1])

def decode_differential(seq):
    tmp = list(itertools.accumulate(seq))

    return tmp[len(tmp)-1]


def encode_dc(dc_diff):  # encode dc와 같은 함수 dc허프만 전에 사용해야함
    for i in range(0, len(HUFFMAN_CATEGORIES)):
        k = 0
        for j in HUFFMAN_CATEGORIES[i]:

            if dc_diff == j:
                return (i, k)
            k += 1


def decode_dc(size, index):
    return HUFFMAN_CATEGORIES[size][index]


def encode_index(dc):  # encode dc와 같은 함수 dc허프만 전에 사용해야함
    for i in range(0, len(HUFFMAN_CATEGORIES)):
        k = 0
        for j in HUFFMAN_CATEGORIES[i]:

            if dc == j:
                return (i, k)
            k += 1


def decode_index(size, index):
    return HUFFMAN_CATEGORIES[size][index]


def encode_dc_huffman(size, value):

    if size == 0:
        dcbits = HUFFMAN_CATEGORY_CODEWORD[DC][size]
        return dcbits
    dcbits = (HUFFMAN_CATEGORY_CODEWORD[DC][size]
              + '{:0{padding}b}'.format(value, padding=size))
    return dcbits


def decode_dc_huffman(bit_seq):
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
            current_idx + (16 if remaining_len > 16 else remaining_len)
        ]
        err_cache = current_slice
        while current_slice:
            if (current_slice in HUFFMAN_CATEGORY_CODEWORD[DC].inv):
                key = (HUFFMAN_CATEGORY_CODEWORD[DC].inv[current_slice])
                # DC
                # print(key)
                size = key
                if size == 0:
                    return 0, bit_seq[len(current_slice)+size:]
                else:
                    return HUFFMAN_CATEGORIES[size][diff_value(
                        current_idx + len(current_slice),
                        size
                    )], bit_seq[len(current_slice)+size:]
            elif len(current_slice)<2:#reversecheck를 위해서 추가했음.
                raise IndexError('There is not enough bits to decode DIFF value '
                             'codeword.')
            current_slice = current_slice[:-1]


def encode_run_length(seq):  # 튜플로 입력해줘야함
    groups = [(len(tuple(group)), key)
              for key, group in itertools.groupby(seq)]  # key 개의 group
    ret = []
    borrow = False  # Borrow one pair in the next group whose key is nonzero.
    if groups[-1][1] == 0:
        del groups[-1]
    for idx, (length, key) in enumerate(groups):
        if borrow:
            length -= 1
            borrow = False
        if length == 0:
            continue
        if key == 0:
            # Deal with the case run (0s) more than 16 --> ZRL.
            while length >= 16:
                ret.append(ZRL)
                length -= 16
            ret.append((length, groups[idx + 1][1]))
            borrow = True
        else:
            ret.extend(((0, key), ) * length)
    return ret + [EOB]


# def decode_run_length(seq):
#     # Remove the last element as the last created by EOB would always be a `0`.
#     result = tuple(item for l, k in seq for item in [0] * l + [k])[:-1]
#     return result
def decode_run_length(seq):

    index = 1
    result = np.zeros(256, np.int8)
    for length, value in seq:
        if length == 0:
            if index >= 64:
                return result

            result[index] = value
            index += 1

        else:
            if index >= 64:
                return result
            index += length
            result[index] = value
            index += 1

    return result


def encode_ac_huffman(run_length):
    acbits = ''
    # value = tuple(value)
    for value in run_length:

        # if value in (EOB, ZRL):
        if value == EOB:
            bits = HUFFMAN_CATEGORY_CODEWORD[AC][value]
            acbits += bits
            #acbits = '1010(EOB)'
            return acbits
        if value == ZRL:
            bits = HUFFMAN_CATEGORY_CODEWORD[AC][value]
            acbits += bits
            continue

        run, nonzero = value

        if nonzero == 0 or nonzero <= -1024 or nonzero >= 1024:
            raise ValueError(
                f'AC coefficient nonzero {value} should be within [-1023, 0) '
                'or (0, 1023].'
            )

        size, fixed_code_idx = encode_index(nonzero)
        bits = (HUFFMAN_CATEGORY_CODEWORD[AC][(run, size)]
                + '{:0{padding}b}'.format(fixed_code_idx, padding=size))  # 만약에 11이면 1011인데 -11은 -1011로 나오면안되고 1101
        acbits += bits
    return acbits


# def decode_ac_huffman(bit_seq,i,j):
    global k,l
    def diff_value(idx, size):
        if idx >= len(bit_seq) or idx + size > len(bit_seq):
            raise IndexError('There is not enough bits to decode DIFF value '
                             'codeword.')
        fixed = bit_seq[idx:idx + size]
        return int(fixed, 2)

    keys = []
    current_idx = 0
    while current_idx < len(bit_seq):
        #   1. Consume next 16 bits as `current_slice`.
        #   2. Try to find the `current_slice` in Huffman table.
        #   3. If found, yield the corresponding key and go to step 4.
        #      Otherwise, remove the last element in `current_slice` and go to
        #      step 2.
        #   4. Consume next n bits, where n is the category (size) in returned
        #      key yielded in step 3. Use those info to decode the data.          
        remaining_len = len(bit_seq) - current_idx
        current_slice = bit_seq[
            current_idx:
            current_idx + (16 if remaining_len > 16 else remaining_len)
        ]
        err_cache = current_slice
        if len(keys)>=21:
            if current_slice[0:4] == '1111':
                if i not in istack:
                    if j not in istack:
                        istack.append(i)
                        jstack.append(j)
                        rstack.append(remaining_len)
                        temppp=check(check_bits[-remaining_len+4:],istack[-1],jstack[-1])
                        print(temppp)
            elif len(keys)>23:
                print('error')
                if istack.index(i) == jstack.index(j):
                    tempp = istack.index(i)
                elif istack.index(i) < jstack.index(j):
                    tempp = jstack.index(j)
                replace(check_bits[-rstack[tempp]:-rstack[tempp]+4],'1010',0,4)
                break 
                   
                
                # if k ==0 and l==0:
                #     kstack.append(i)
                #     lstack.append(j)
                # else:
                #     kstack.append(k)
                #     lstack.append(l)
                # if check(check_bits[-remaining_len+4:],kstack[-1],lstack[-1]) == 0:#check했을때 남은비트없이 깔끔하면 
                #     kstack.pop(-1)
                #     lstack.pop(-1)
                #     k = kstack[-1]
                #     l = lstack[-1]
                #     keys.append((0,0))
                #     return keys, bit_seq[current_idx+4:]
                # else:
                #     kstack.pop(-1)
                #     lstack.pop(-1)
                #     k = kstack[-1]
                #     l = lstack[-1]
                #check했을때 남은비트가 있으면 그냥 다음줄로 진행
                    
        while current_slice:
            if (current_slice in
                    HUFFMAN_CATEGORY_CODEWORD[AC].inv):
                key = (HUFFMAN_CATEGORY_CODEWORD[AC].inv[current_slice])

                # AC
                run, size = key
                if key == ZRL:
                    keys.append(key)
                elif key == EOB:
                    keys.append(key)
                    return keys, bit_seq[current_idx+4:]
                else:
                    temp = (run, HUFFMAN_CATEGORIES[size][diff_value(
                        current_idx + len(current_slice),
                        size
                    )])
                    keys.append(temp)

                current_idx += len(current_slice) + size
                break
            # elif current_slice =='0101':
            #     keys.append(EOB)
            #     return keys, bit_seq[current_idx+4:]
            current_slice = current_slice[:-1]
        else:
            raise KeyError(
                f'Cannot find any prefix of {err_cache} in Huffman table.'
            )
    return keys

def decode_ac_huffman(bit_seq):

    def diff_value(idx, size):
        if idx >= len(bit_seq) or idx + size > len(bit_seq):
            raise IndexError('There is not enough bits to decode DIFF value '
                             'codeword.')
        fixed = bit_seq[idx:idx + size]
        return int(fixed, 2)

    keys = []
    current_idx = 0
    while current_idx < len(bit_seq):
        #   1. Consume next 16 bits as `current_slice`.
        #   2. Try to find the `current_slice` in Huffman table.
        #   3. If found, yield the corresponding key and go to step 4.
        #      Otherwise, remove the last element in `current_slice` and go to
        #      step 2.
        #   4. Consume next n bits, where n is the category (size) in returned
        #      key yielded in step 3. Use those info to decode the data.
        remaining_len = len(bit_seq) - current_idx
        current_slice = bit_seq[
            current_idx:
            current_idx + (16 if remaining_len > 16 else remaining_len)
        ]
        err_cache = current_slice
        while current_slice:
            if (current_slice in
                    HUFFMAN_CATEGORY_CODEWORD[AC].inv):
                key = (HUFFMAN_CATEGORY_CODEWORD[AC].inv[current_slice])

                # AC
                run, size = key
                if key == ZRL:
                    keys.append(key)
                elif key == EOB:
                    keys.append(key)
                    return keys, bit_seq[current_idx+4:]
                else:
                    temp = (run, HUFFMAN_CATEGORIES[size][diff_value(
                        current_idx + len(current_slice),
                        size
                    )])
                    keys.append(temp)

                current_idx += len(current_slice) + size
                break
            current_slice = current_slice[:-1]
        else:
            raise KeyError(
                f'Cannot find any prefix of {err_cache} in Huffman table.'
            )
    return keys


def check_ac_huffman(bit_seq):

    def diff_value(idx, size):
        if idx >= len(bit_seq) or idx + size > len(bit_seq):
            raise IndexError('There is not enough bits to decode DIFF value '
                             'codeword.')
        fixed = bit_seq[idx:idx + size]
        return int(fixed, 2)

    keys = []
    current_idx = 0
    while current_idx < len(bit_seq):
        #   1. Consume next 16 bits as `current_slice`.
        #   2. Try to find the `current_slice` in Huffman table.
        #   3. If found, yield the corresponding key and go to step 4.
        #      Otherwise, remove the last element in `current_slice` and go to
        #      step 2.
        #   4. Consume next n bits, where n is the category (size) in returned
        #      key yielded in step 3. Use those info to decode the data.          
        remaining_len = len(bit_seq) - current_idx
        current_slice = bit_seq[
            current_idx:
            current_idx + (16 if remaining_len > 16 else remaining_len)
        ]
        err_cache = current_slice
        
        
                    
        while current_slice:
            if (current_slice in
                    HUFFMAN_CATEGORY_CODEWORD[AC].inv):
                key = (HUFFMAN_CATEGORY_CODEWORD[AC].inv[current_slice])

                # AC
                run, size = key
                if key == ZRL:
                    keys.append(key)
                elif key == EOB:
                    keys.append(key)
                    return keys, bit_seq[current_idx+4:]
                else:
                    temp = (run, HUFFMAN_CATEGORIES[size][diff_value(
                        current_idx + len(current_slice),
                        size
                    )])
                    keys.append(temp)

                current_idx += len(current_slice) + size
                break
            # elif current_slice =='0101':
            #     keys.append(EOB)
            #     return keys, bit_seq[current_idx+4:]
            current_slice = current_slice[:-1]
        else:
            raise KeyError(
                f'Cannot find any prefix of {err_cache} in Huffman table.'
            )
    return keys


def d1_to_d2(pixel_values, row, col):
    d2 = np.zeros((row, col), np.uint8)
    for i in range(0, row):  # 1차원리스트를 2차원배열로 변경
        for j in range(0, col):
            d2[i][j] = pixel_values[i*row+j]
    return d2


def flip(arr):# 1111을 1010으로 만들기
    arr1 = list(arr)
    for i in range(len(arr1)):
        if arr1[i] == '1':
            arr1[i] = '0'
        elif arr1[i] == '0':
            arr1[i] = '1'
    
    arr = ''.join(arr1)
    return arr

def eobflip(arr):#1010을 1111로 만들기
    arr1 = list(arr)
    for i in range(-1,-5,-1):
        # if arr1[i] == '1':
        #     arr1[i] = '0'
        # elif arr1[i] == '0':
        #     arr1[i] = '1'
        if arr1[i] == '0':
            arr1[i] = '1'
    
    arr = ''.join(arr1)
    return arr

def eobflip1(arr):
    arr1 = list(arr)
    for i in range(-1,-5,-2):
        
        if arr1[i] == '1':
            arr1[i] = '0'
    
    arr = ''.join(arr1)
    return arr

    
        



def replace(encoded_bits, replace_bits, start, length):  # 원본, 변경할비트,시작점,길이
    encoded = list(encoded_bits)
    replaced = list(replace_bits)
    for i in range(length):
        encoded[start+i] = replaced[i]
    encoded_bits = ''.join(encoded)
    return encoded_bits

def arrange(encoded_bits):
    index = len(encoded_bits)-4
    end = len(encoded_bits)
    while True:
        if encoded_bits[index:index+4] =='1010':
            #여기서부터 decoding진행하면됨. 만약에 디코딩이완전하지않으면 하나더 이전 1010으로 진행
            while index>0:
                index-=1
                if encoded_bits[index:index+4] == '1010':
                    try :
                        tmp,remain_tmp=decode_dc_huffman(encoded_bits[index+4:end])
                        decode_ac_huffman(remain_tmp)
                        print('이 1010은 이전블록의 eob구만')
                        end = index+4
                        break
                    except IndexError:
                        print('이 1010은 이전블록의 eob가 아니구만')
                    except KeyError:
                        print('이 1010은 이전블록의 eob가 아니구만')
                    except ValueError:
                        print('이 1010은 이전블록의 eob가 아니구만')
                elif encoded_bits[index:index+4] == '0101':
                    try :#'0101  11101001110011010 이 디코딩이 잘되는 문제'
                        tmp,remain_tmp=decode_dc_huffman(encoded_bits[index+4:end])
                        decode_ac_huffman(remain_tmp)
                        print('이 0101은 이전블록의 eob구만')
                        
                        end = index+4
                        break
                    except IndexError:
                        print('이 0101은 이전블록의 eob가 아니구만')
                    except KeyError:
                        print('이 1010은 이전블록의 eob가 아니구만')
                    except ValueError:
                        print('이 1010은 이전블록의 eob가 아니구만')
                    
            
                
        elif encoded_bits[index:index+4] =='0101':#지금 여기 오류있음
            #여기서부터 decoding진행하면됨. 만약에디코딩이 완전하지않으면 하나더 이전 1010으로 진행
            while index>0:
                index-=1
                if encoded_bits[index:index+4] == '1010':
                    try :
                        tmp,remain_tmp=decode_dc_huffman(eobflip(encoded_bits[index+4:end]))
                        decode_ac_huffman(remain_tmp)
                        print('이 1010은 이전블록의 eob구만')
                        encoded_bits_tmp = replace(encoded_bits,eobflip(encoded_bits[index+4:end]),index+4,end-index-4)
                        encoded_bits = encoded_bits_tmp
                        end = index+4
                        break
                    except IndexError:
                        print('이 1010은 이전블록의 eob가 아니구만')
                    except KeyError:
                        print('이 1010은 이전블록의 eob가 아니구만')
                    except ValueError:
                        print('이 1010은 이전블록의 eob가 아니구만')
                elif encoded_bits[index:index+4] == '0101':
                    try :
                        tmp,remain_tmp=decode_dc_huffman(eobflip(encoded_bits[index+4:end]))
                        decode_ac_huffman(remain_tmp)
                        print('이 0101은 이전블록의 eob구만')
                        encoded_bits_tmp = replace(encoded_bits,eobflip(encoded_bits[index+4:end]),index+4,end-index-4)
                        encoded_bits = encoded_bits_tmp
                        end = index+4

                        break
                    except IndexError:
                        print('이 0101은 이전블록의 eob가 아니구만')
                    except KeyError:
                        print('이 1010은 이전블록의 eob가 아니구만')
                    except ValueError:
                        print('이 1010은 이전블록의 eob가 아니구만')
        if end<5:
            return encoded_bits

def pixel_diff(arr):  # [행,열] 픽셀값 차이 계산
    diff = 0
    for j in range(0, 8):
        for i in range(0, 7):
            diff += abs(int(arr[i+1, j]) - int(arr[i, j]))
    return diff/8


def dcvalue(a11):
    # dcval[1+64*int(i/8)+int(j/8)] = a17[0]
    dcval.append(a11)

def check(check_bits1,n,m):
    
    for k in range(n,img_size,8):
        for l in range(0,img_size,8):
            if (k == n and l>=m+8)or k>n:
                a11, check_bits1 = decode_dc_huffman(check_bits1)  # a11이 dc value
                dcvalue(a11)
                a12, check_bits1 = decode_ac_huffman(check_bits1,k,l)
                a13 = decode_run_length(a12)
                a13[0] = decode_differential(dcval)
                a14 = izigzag(a13)
                a15 = quantize(a14, True)
                a16 = idct2d(a15)
                a17 = after_idct(a16)
    
    
    if len(check_bits1) == 0:
        return 0
    else :
        return len(check_bits1)  
            
            
            
        
        
            
            
        
        
        
    return len(check_bits1)

    

def encoding(a1):

    a2 = before_dct(a1)
    a3 = dct2d(a2)
    a4 = quantize(a3)
    a5 = zigzag(a4)
    encode_differential(a5[0])
    size, value = encode_dc(dc_diff[len(dc_diff)-1])
    a7 = encode_dc_huffman(size, value)
    a8 = encode_run_length(tuple(a5)[1:])
    a9 = encode_ac_huffman(a8)
    # if len(a8)>21:
    
    rm.append(len(a8))
    a10 = a7+a9
    return a10

# def checkencoding(a1):

#     a2 = before_dct(a1)
#     a3 = dct2d(a2)
#     a4 = quantize(a3)
#     a5 = zigzag(a4)
#     encode_differential(a5[0])
#     size, value = encode_dc(dc_diff[len(dc_diff)-1])
#     a7 = encode_dc_huffman(size, value)
#     a8 = encode_run_length(tuple(a5)[1:])
#     a9 = encode_ac_huffman(a8)
#     rm.append(len(a8))
#     a10 = a7+a9
#     return a10


# def decoding(a10):  # normal
#     a11, remain_bits = decode_dc_huffman(a10)  # a11이 dc value
#     dcvalue(a11)
#     a12, remain_bits = decode_ac_huffman(remain_bits)
#     a13 = decode_run_length(a12)
#     a13[0] = decode_differential(dcval)
#     a14 = izigzag(a13)
#     a15 = quantize(a14, True)
#     a16 = idct2d(a15)
#     a17 = after_idct(a16)

#     return a17, remain_bits

def decoding(a10):  # reverse decoding
    
    a11, remain_bits = decode_dc_huffman(a10)  # a11이 dc value
    dcvalue(a11)
    try:
        a12, remain_bits = decode_ac_huffman(remain_bits)
    except ValueError:
        print("1111로 가정한것이 틀렸음 변경된 비트로 다시 실행")
    # rm1.append(len(a12))
    a13 = decode_run_length(a12)
    a13[0] = decode_differential(dcval)
    a14 = izigzag(a13)
    a15 = quantize(a14, True)
    a16 = idct2d(a15)
    a17 = after_idct(a16)

    return a17, remain_bits

# filename = '/Users/alanlee/Documents/GitHub/jpeg.reverse/시행착오/1.1.01.tiff'
filename = '1.gif'


image = Image.open(filename, 'r')
#image = img.imread(filename)
pixel_values = list(image.getdata())  # 얘떄문에 d1_to_d2함수 필요
img_size = 512
k = 0
l = 0
istack = []
jstack = []
rstack = []
arr = d1_to_d2(pixel_values, img_size, img_size)
arr1 = np.zeros((img_size, img_size), np.uint8)
encoded_bits = ''
check_bits = ''
randombits = ''
rnd = list(randombits)
diffmax = 0
dc_diff = []  # type: List[int]
dcval = []
lengths = []
rm = []#run magnitude (run,length)
rm1 = []
rmcount = []



# for i in range(0, img_size, 8):#플립 인코딩
#     for j in range(0, img_size, 8):
#         a1 = arr[i:i+8, j:j+8]
#         # if len(rnd) > int(img_size*(i/8)+(j/8)):
#         #     if rnd[int(img_size*(i/8)+(j/8))]=='1':
#         #         encoded_bits += eobflip(encoding(a1))
#         #     else:
#         #         encoded_bits += encoding(a1)
#         # else:
#             #lengths.append(len(encoding(a1)))
#         encoded_bits += encoding(a1)
        

# plt.hist(lengths,bins=30)
# print(len(encoded_bits)/4096)
# plt.show()

for i in range(0, img_size, 8):  # normal인코딩
    for j in range(0, img_size, 8):
        a1 = arr[i:i+8, j:j+8]
        encoded_bits += encoding(a1)

#arrange(encoded_bits)
# check_bits = encoded_bits


for i in range(0, img_size, 8):  # normal 디코딩
    for j in range(0, img_size, 8):

        a17, encoded_bits = decoding(encoded_bits)

        arr1[i:i+8, j:j+8] = a17
        # print(i, j)
        # print(a17)

        # print(pixel_diff(arr1[i:i+8, j:j+8]))
        # if pixel_diff(arr1[i:i+8, j:j+8]) > diffmax:
        #     diffmax = pixel_diff(arr1[i:i+8, j:j+8])

        if encoded_bits == '':
            break
    if encoded_bits == '':
        break

# for i in range(504, -1, -8):  # 역방향 디코딩
#     for j in range(504, -1, -8):

#         a17, encoded_bits = decoding(encoded_bits)

#         arr1[i:i+8, j:j+8] = a17
#         print(i, j)
#         print(a17)

#         # print(pixel_diff(arr1[i:i+8, j:j+8]))
#         # if pixel_diff(arr1[i:i+8, j:j+8]) > diffmax:
#         #     diffmax = pixel_diff(arr1[i:i+8, j:j+8])

#         if encoded_bits == '':
#             break
#     if encoded_bits == '':
#         break




# 아닐경우에는 숫자 1씩 올리고 2length 3length 플립해서 다시 하기 while문안에 encodedbits는 임시 local변수 하나 만들어서 해야할듯
# flip안했을때 1length, 2length ,3length flip했을때 abs(l-length)가 최솟값일때
# 8/26 디코드 런렝쓰 오류코드 -1 나오게 해서 위에꺼 실행할 예정


# plt.hist(list(itertools.accumulate(dcval)), bins=30, label="bins=30")
# plt.show

"""
이거 그냥 일반적으로 인코딩디코딩 하는거 테스트용으로 따로 만들어야할듯
length만큼 플립해서 디코딩해보고 1010이 안나오면 2length 3length 플립 후 디코딩
플립해서 디코딩 할때 사용한 비트를 bits라고 했을때 length-bits는 원상복구
만약에 encoded_bits가 length보다 적으면 끝까지 플립
"""
# encoded_bits 평균비트수 175.36 176비트 단위로 플립해봐야할듯

for i in range(63):#AC Run Magnitude 갯수 세보는것
    rmcount.append(rm.count(i))

plt.hist(rm,bins=23)
plt.show()
# tuple(rm1)
# run,mag = zip(*rm1)#튜플 리스트를 스캐터로 시각화 하는방법을 찾아보기
# plt.scatter(run,mag)
# plt.show()

newimg = Image.fromarray(arr1)
plt.imshow(newimg, cmap=plt.cm.gray)  # 그레이스케일은 cmap=plt.cm.gray설정필요

plt.show()

f = open('write.csv','w', newline='')
wr = csv.writer(f)
for i in range(0,len(rmcount)):
    wr.writerow([i,rmcount[i]])
    
f.close


'''
        순서
        before_dct
        dct2d
        quantize
        zigzag
        encode_dc
        encode_dc_huffman
        encode_run_length
        encode_ac_huffman
        decode_dc_huffman
        decode_dc
        decode_ac_huffman
        decode_run_length
        izigzag
        quantize
        idct2d
        '''
