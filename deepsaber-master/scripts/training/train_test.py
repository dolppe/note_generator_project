import argparse
from email.policy import default

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                add_help=False)
parser.add_argument('--test',type=str,default='asdf')
parser.add_argument('--test1',type=str,default='a1')
parser.add_argument('--test2',type=str,default='a1')
parser.add_argument('--test3',type=str,default='a1')
parser.set_defaults(test='a3')

addstr = {'--test4' : 'b1', 'test' :'b2'}

for add_item in addstr:
    if parser.get_default(add_item) is None:
        parser.add_argument(add_item,type=str,default=addstr[add_item])
    else:
        parser.set_defaults(add_item=addstr[add_item])

ns,_ = parser.parse_known_args()

ns.test4 = 'asdf'
ns.test5 = 'asdfasdf'

strin = 'test411'

if strin in ns:
    ns.__dict__[strin]='asdfasdf'
else:
    ns.__dict__[strin] = 'zxcv'


print(ns.test5)



print('1')