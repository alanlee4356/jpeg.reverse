

TRANSITION_P ={
'1':	339/4096,
'2':	566/4096,
'3':	610/4096,
'4':	427/4096,
'5':	293/4096,
'6':	251/4096,
'7':	228/4096,
'8':	210/4096,
'9':	176/4096,
'10':	152/4096,
'11':	129/4096,
'12':	119/4096,
'13':	113/4096,
'14':	98/4096,
'15':	120/4096,
'16':	73/4096,
'17':	75/4096,
'18':	50/4096,
'19':	31/4096,
'20':	15/4096,
'21':	14/4096,
'22':	2/4096,
'23':	5/4096
}

#https://hipgyung.tistory.com/entry/HMM-Viterbi-%EB%B9%84%ED%84%B0%EB%B9%84-%EC%95%8C%EA%B3%A0%EB%A6%AC%EC%A6%98-%EC%BD%94%EB%93%9C


line_nodes = [0,1,1,2,2,3] #n+1번째 라인의 경우의수 n+1은 n+1~n+2사이 
line_num = 0
value_nodes = [0,3,4,[2,3],[3,4],[5,6,7]] #n번째 라인마다의 확률값 리스트 안에 리스트 넣기
value_num = 0
print(line_nodes[1])
def viterbi():
    #build map
    #edge들의 값을 적어주기
    def buildmap():
        print()
        
