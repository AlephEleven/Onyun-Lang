import sys
from interp import *
from parser import Parser
from abstree import AbsTree
from lexer import Lexer

argv = sys.argv

if(len(argv)!=3):
    raise Exception("Run as: python3.10 [interp|cst|ast|tokens] [filename]")

F = open(argv[2], "r")
content = F.read()


match argv[1]:
    case "interp":
        print(interpS(content))
    case "cst":
        Parser.print_tree(Parser.parse_CST(content))
    case "ast":
        AbsTree.print_expr(AbsTree.parse_AST(content))
    case "tokens":
        print(Lexer.parse_string(content))
