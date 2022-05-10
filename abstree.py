from parser import Parser
from readkw import *

kws_lexer = KWLexer("lang.json").lexer_kw
kws_syn = kws_lexer["token-syntax"]

class AbsTree:
    def __init__(self):
        pass

    def expr_cls(name, params, str_rep):
        return type(name, (object,), {"vals": params, "str": str_rep, "id": name, "arglen":1 if not isinstance(params, list) else len(params)})

    def est(expr_obj):
        return AbsTree.expr(expr_obj).str

    def print_expr(expr_obj, space=0):
        print(f"{' '*space}Name: {expr_obj.id}")
        try:
            vals = expr_obj.vals
            print(f"{' '*space}(")
            for i in vals:
                AbsTree.print_expr(i, space+2)
            print(f"{' '*space})")
        except:
            print(f"{' '*space}Value: {expr_obj.vals}")

        print(f"{' '*space}Args: {expr_obj.arglen}")

    def expr(exp):

        match exp:
            case {"EXP": {"NUMBER": v}}:
                return AbsTree.expr_cls("Num", v, f"Num {v}")
            case {"EXP": {"ID": v}}:
                return AbsTree.expr_cls("Var", v, f"Var {v}")
            case {"EXP": {"BOOL": v}}:
                return AbsTree.expr_cls("Bool", v, f"Bool {v}")
            case {"Func": (name, vs)}:
                return AbsTree.expr_cls(name, [AbsTree.expr(v) for v in vs], f"{name[1:]} {[AbsTree.est(v) for v in vs]}")
            case {"Op": (name, vs)}:
                return AbsTree.expr_cls(name, [AbsTree.expr({"EXP": v}) for v in vs], f"{name[1:]} {[AbsTree.est({'EXP': v}) for v in vs]}")
            case v:
                return AbsTree.abs_defs(v)
    
    def exp_name(exp_n):
        return "E"+exp_n.capitalize()

    def abs_defs(abst):
        match abst:
            case {"EXP": v}:
                match v:
                    #<Exp> ::= f<Exp>
                    case {"KEY": fname}, {"EXP": e}:
                        return AbsTree.expr({"Func": (AbsTree.exp_name(fname), e[1:-1][::2])})
                    #<Exp> ::= <Exp> <Op> <Exp>
                    case {"EXP": e1}, {"OP": op}, {"EXP": e2}:
                        return AbsTree.expr({"Op": (AbsTree.exp_name(list(op.keys())[0]), [e1, e2]) })
                    #<Exp> ::= <Exp> | (<Exp>)
                    case {"EXP": e} | [{'CLBRAC': '('}, {'EXP': e}, {'CRBRAC': ')'}]:
                        return AbsTree.expr({"EXP":e})
                    case _:
                        return AbsTree.expr_cls("invalid", {"str": -1}, "Invalid")
            case _:
                return AbsTree.expr_cls("invalid", {"str": -1}, "Invalid")
    
    def parse_AST(string):
        return AbsTree.abs_defs(Parser.parse_CST(string))