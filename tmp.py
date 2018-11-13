# c++
# switch(smth): {
#     case "a":
#        funca();
#        break;
#     case "b":
#        funcb();
#        break;
       
#     case "c":
#        funcc();
#        break;

#     default:
#        funcd();
#        break;
# }

# python
from collections import defaultdict
def funca():
    print('a')

def funcb():
    print('b')

def funcd():
    print('d')


d = {
   'a': funca,
   'b': funca,
   'c': lambda : print('c'),
}

smth = 't'

d.get(smth, funcd)()