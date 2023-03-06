# n, k = map(int, input().split())
# number = list(input())
from collections import deque
n = 10
k = 4
number = deque('4177252841')
numberlen = len(number)
front = deque('')
rear = deque('')
answer = deque('')

front.append(4)
number.append(4)
print(number)