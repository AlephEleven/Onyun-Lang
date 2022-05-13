from lexer import Lexer
import pprint

'''
Concrete Syntax:

<Exp> ::= <ID> | <NUMBER> | {bool} | (args...)
<Exp> ::= <Exp> <OP> <Exp>
<Exp> ::= <Exp>
<Func> ::= f(<Exp>)


bool = true | false
<BOp> ::= <+|-|*|/|%>

Note - functional paranthesis are deal with via (args...), so actual syntax is f<Exp>
'''


class Parser:
    def __init__(self):
        pass

    def concrete_type(tok):
        match tok:
        # <Exp> ::= <ID> | <NUMBER>
            case {"ID": tk} | {"NUMBER": tk} | {"STRING": tk}:
                if(tk in ["true", "false"]):
                    return {"EXP": {"BOOL": True if tk=="true" else False}}
                else:
                    return {"EXP": tok}
            # <BOp> ::= <+|-|*|/>
            case {"ADD": _} | {"SUB": _} | {"MUL": _} | {"DIV": _} | {"MOD": _} | {"EXPO": _}:
                return {"OP": tok}
            case other:
                return other

    def print_tree(cst):
        pprint.pprint(cst)

    def apply_concrete(s_tok):
        return [Parser.concrete_type(tok) for tok in s_tok]

    def exp_list_to_tk_arr(matching, end_key):
        '''
        Deals with multiple args
        '''
        i = 1
        exp_com = 0
        exp_com_l = ["EXP", "COMMA"]
        for tk in matching:
            for key in tk:
                i += 1
                if key != exp_com_l[exp_com%2] and key==end_key:
                    return (True, i)
                if key != exp_com_l[exp_com%2]:
                    return (False, i)
                exp_com += 1
        return (False, i)

    def concrete_defs(cst, prec):
        '''
        Precendence based on python's ver.

        https://docs.python.org/3/reference/expressions.html#operator-precedence

        going from 0->16
        
        '''
        match cst, prec:
            case [], _:
                return []
            
            #<Exp> := set <Exp/Var> = <Exp>
            case [{'EXP': [{'KEY': 'set'}, {'EXP': {'ID': _}}]}, {"EQUAL": _}, {"EXP": _}, *t], 1:
                exp1 = cst[0]["EXP"]
                return [{"EXP": [exp1[0], {"EXP":[{"CLBRAC": "("}, exp1[1], {"COMMA": ","}, cst[2], {"CRBRAC": ")"}]} ]}] + Parser.concrete_defs(t, prec)

            #<Exp> := if <Bool> then <Exp> else <Exp>
            case [{"EXP": [{"KEY": "if"},{"EXP": _}]}, {"EXP": [{"KEY": "then"}, {"EXP": _}]}, {"EXP": [{"KEY": "else"}, {"EXP": _}]}, *t], 5:
                return [{"EXP": [{"KEY": "ite"},{"EXP":[{"CLBRAC": "("}, cst[0]["EXP"][1], {"COMMA": ","}, cst[1]["EXP"][1], {"COMMA": ","}, cst[2]["EXP"][1], {"CRBRAC": ")"}]} ]}] + Parser.concrete_defs(t, prec)

            #<Exp> := !<Bool>
            case [{'EXCLAMATION': _},{"EXP": _}, *t], 5:
                return [{"EXP": [{"KEY": "not"},{"EXP":[{"CLBRAC": "("}, cst[1], {"CRBRAC": ")"}]} ]}] + Parser.concrete_defs(t, prec)

            #<Exp> := <Bool> & <Bool>
            case [{"EXP": _}, {'AND': _}, {"EXP": _},  *t], 4:
                return [{"EXP": [{"KEY": "and"},{"EXP":[{"CLBRAC": "("}, cst[0], {"COMMA": ","}, cst[2],  {"CRBRAC": ")"}]} ]}] + Parser.concrete_defs(t, prec)

            #<Exp> := <Bool> ~ <Bool>
            case [{"EXP": _}, {'OR': _}, {"EXP": _},  *t], 3:
                return [{"EXP": [{"KEY": "or"},{"EXP":[{"CLBRAC": "("}, cst[0], {"COMMA": ","}, cst[2],  {"CRBRAC": ")"}]} ]}] + Parser.concrete_defs(t, prec)

            #<Exp> := <Exp> |> <Key>
            case [{"EXP": e}, {"LINE": _}, {"ARBRAC": _}, {"KEY": _}, *t], 7:
                try:
                    _ = e[0]["CLBRAC"]
                    return [{"EXP": [cst[3]]+[cst[0]]}] + Parser.concrete_defs(t, prec)
                except:
                    return [{"EXP": [cst[3],{"EXP":[{"CLBRAC": "("}, cst[0], {"CRBRAC": ")"}]} ]}] + Parser.concrete_defs(t, prec)
            
            #<Exp> := <Exp> <Op> <Exp>
            case [{"EXP": _}, {"OP":{"ADD": _} | {"SUB": _}}, {"EXP": _}, *t], 11:
                return [{"EXP": cst[:3]}]+Parser.concrete_defs(t, prec)
            case [{"EXP": _}, {"OP":{"MUL":_} | {"DIV": _} | {"MOD": _}}, {"EXP": _}, *t], 12:
                return [{"EXP": cst[:3]}]+Parser.concrete_defs(t, prec)
            case [{"EXP": _}, {"OP":{"EXPO":_}}, {"EXP": _}, *t], 14:
                return [{"EXP": cst[:3]}]+Parser.concrete_defs(t, prec)           
                
            #<Exp> := [<Exp>]
            case [{"KEY": "list"}, {"EXP": _}, *t], 15:
                return [{"EXP": cst[:2]}] + Parser.concrete_defs(t, prec)
            
            #<Exp> := f(<Exp>)
            case [{"KEY": _}, {"EXP": _}, *t], 15:
                return [{"EXP": cst[:2]}] + Parser.concrete_defs(t, prec)

            #<Exp> := (...args)
            case [{"CLBRAC": _},*t], 16:
                exps = Parser.exp_list_to_tk_arr(t, "CRBRAC")
                if(exps[0]):
                    return [{"EXP": cst[:exps[1]]}]+Parser.concrete_defs(cst[exps[1]:], prec)
                else:
                    return [{"CLBRAC": "("}]+Parser.concrete_defs(t, prec)
            #<Exp> := [...args]
            case [{"SLBRAC": _},*t], 16:
                exps = Parser.exp_list_to_tk_arr(t, "SRBRAC")
                if(exps[0]):
                    return [{"KEY": "list"}, {"EXP": cst[:exps[1]]}]+Parser.concrete_defs(cst[exps[1]:], prec)
                else:
                    return [{"SLBRAC": "("}]+Parser.concrete_defs(t, prec)
            #<Exp> := (<Exp>)
            case [{"CLBRAC": _}, {"EXP": e}, {"CRBRAC": _}, *t], 16:
                return [{"EXP": cst[:3]}]+Parser.concrete_defs(t, prec)
            case [any, *t], _:
                return [any]+Parser.concrete_defs(t, prec)

    def apply_defs(cst):
        '''
        Applies CST defintions to list of string tokens

        Returns CST

        Raises exception if failed to make CST
        '''

        tmp_cst = []

        while(tmp_cst!=cst):
            tmp_cst = cst

            for i in reversed(range(0, 17)):
                cst = Parser.concrete_defs(cst, i)
        
        if len(cst) > 1:
            Parser.print_tree(cst)
            raise Exception("Parser Error: Invalid Syntax, unable to parse CST")

        return cst

    def parse_CST(string):
        '''
        Fully parses a string into a CST

        Ex: "abs(5)"

        Returns: [{'EXP': [{'KEY': 'abs'}, {'EXP': [[{'CLBRAC': '('}, {'EXP': {'NUMBER': '5'}}, {'CRBRAC': ')'}]]}]}]
        '''
        res = Parser.apply_defs(Parser.apply_concrete(Lexer.parse_string(string)))

        match res[0]["EXP"]:
            case {"NUMBER": _} | {"ID": _} | {"BOOL": _}:
                return [{"EXP": res[0]}][0]
            case _:
                return res[0]