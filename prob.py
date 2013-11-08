input = [0,3,4,2,1,10000000]
max = len(input)
posible = range(0,max)
o = input
k = 0
for a in input:
  try:
    print a-k
    print posible[a-k]
    del posible[a-k]
    k += 1
  except IndexError as ie:
    pass
# diff = [a for a in posible if a not in input]
print posible

