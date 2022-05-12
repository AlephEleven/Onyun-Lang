from ds import *
from readkw import *
import math

def expr(val, is_str=False):
    match val:
        case bool(v):
            return ast.expr_cls("Bool", v, f"Bool {v}")
        case float(v) | int(v):
            return ast.expr_cls("Num", v, f"Num {v}")
        case str(v) if is_str:
            return ast.expr_cls("String", v, f"String {v}")
        case str(v):
            return ast.expr_cls("Var", v, f"Var {v}")
        case tuple(v):
            return ast.expr_cls("Tuple", v, f"Tuple {v}")
        case list(v):
            return ast.expr_cls("List", v, f"List {v}")
        case None:
            return ast.expr_cls("Unit", None, "Unit")

def string_of_expr(val):
    match val.id:
        case "Ok":
            return f"Ok ({string_of_expr(val.vals)})"
        case "Num" | "Var" | "Bool":
            return f"{val.id} {val.vals}"
        case "String":
            return f'{val.id} "{val.vals}"'
        case "Unit":
            return val.id
        case "List":
            return f'{val.id} {[string_of_expr(i) for i in val.vals]}'
        case _:
            return f'{val.id} {[string_of_expr(i) for i in val.vals]}'

def return_expr(val, is_str=False):
    return return_exp(expr(val, is_str))

def tempset(var, val):
    return eval_expr(ast.expr_cls("ESet", [var, val], f"ESet {[var, val]}"))

g_env = {}

def eval_expr(exp):
    global g_env
    match exp.id:
        case "Num":
            (n) = exp
            return return_exp(n)
        case "Var":
            (n) = exp
            return eval_expr(apply_env(n.vals, g_env))
        case "Bool":
            (n) = exp
            return return_exp(n)
        case "String":
            (n) = exp
            return return_exp(n)
        case "Unit":
            (n) = exp
            return return_exp(n)
        case "Tuple":
            (n) = exp
            return return_exp(n)
        case "List":
            (n) = exp
            return return_exp(n)
        case "EAdd":
            (n) = valid_args(exp, 2)
            v1 = num_of_numVal(eval_expr(n[0]))
            v2 = num_of_numVal(eval_expr(n[1]))
            return return_expr(v1+v2)
        case "ESub":
            (n) = valid_args(exp, 2)
            v1 = num_of_numVal(eval_expr(n[0]))
            v2 = num_of_numVal(eval_expr(n[1]))
            return return_expr(v1-v2)
        case "EMul":
            (n) = valid_args(exp, 2)
            v1 = num_of_numVal(eval_expr(n[0]))
            v2 = num_of_numVal(eval_expr(n[1]))
            return return_expr(v1*v2)
        case "EDiv":
            (n) = valid_args(exp, 2)
            v1 = num_of_numVal(eval_expr(n[0]))
            v2 = num_of_numVal(eval_expr(n[1]))
            if(v2==0):
                return error("Div: Division by zero!")
            return return_expr(v1/v2)
        case "EMod":
            (n) = valid_args(exp, 2)
            v1 = num_of_numVal(eval_expr(n[0]))
            v2 = num_of_numVal(eval_expr(n[1]))
            return return_expr(v1%v2)       
        case "EAbs":
            (n) = valid_args(exp, 1)
            v = num_of_numVal(eval_expr(n[0]))
            return return_expr(abs(v))
        case "EMax":
            (n) = valid_args(exp)
            vs = [num_of_numVal(eval_expr(ni)) for ni in n]
            if(len(vs)==0):
                return error("Max: function requires 1> arguments!")
            return return_expr(max(vs))
        case "EMin":
            (n) = valid_args(exp)
            vs = [num_of_numVal(eval_expr(ni)) for ni in n]
            if(len(vs)==0):
                return error("Min: function requires 1> arguments!")
            return return_expr(min(vs))
        case "EInt":
            (n) = valid_args(exp, 1)
            v = num_of_numVal(eval_expr(n[0]))
            return return_expr(int(v))
        case "EExp":
            (n) = valid_args(exp, 1)
            v = num_of_numVal(eval_expr(n[0]))
            return return_expr(math.exp(v))
        case "EIszero":
            (n) = valid_args(exp, 1)
            v = num_of_numVal(eval_expr(n[0]))
            return return_expr(v==0)
        case "ESet":
            (n) = valid_args(exp, 2)
            id = n[0].vals
            defin = eval_expr(n[1]).vals
            g_env = extend_env(id, defin, g_env)
            return return_expr(None)
        case "ECell":
            (n) = valid_args(exp)
            if (len(n)==0):
                return return_expr(None)
            vs = [eval_expr(n1) for n1 in n[:-1]]+[n[-1]]
            return eval_expr(vs[-1])
        case "EPrivcell":
            (n) = valid_args(exp)
            if (len(n)==0):
                return return_expr(None)
            temp, g_env = g_env, {}     
            vs = [eval_expr(n1) for n1 in n[:-1]]+[n[-1]]
            res = eval_expr(vs[-1])
            g_env = temp
            return res
        case "EStrnum":
            (n) = valid_args(exp)
            vs = [string_of_stringVal(eval_expr(ni)) for ni in n]
            return return_expr(float(''.join(vs)))
        case "ENumstr":
            (n) = valid_args(exp)
            vs = [str(num_of_numVal(eval_expr(ni))) for ni in n]
            return return_expr(''.join(vs), is_str=True)
        case "EConcat":
            (n) = valid_args(exp)
            vs = [string_of_stringVal(eval_expr(ni)) for ni in n]
            return return_expr(''.join(vs), is_str=True)
        case "EStrlen":
            (n) = valid_args(exp, 1)
            v = string_of_stringVal(eval_expr(n[0]))
            return return_expr(len(v))
        case "EFunc":
            (n) = valid_args(exp, 2)
            return return_expr((n[0], n[1]))
        case "EApp":
            (n) = valid_args(exp, 2)
            v1 = any_of_anyVal(eval_expr(n[0]))
            v2 = n[1]
            temp = dict(g_env)
            tempset(v1[0], v2)
            res = return_expr(any_of_anyVal(eval_expr(v1[1])))
            g_env = temp
            return res
        case "EEle":
            (n) = valid_args(exp, 2)
            index = num_of_numVal(eval_expr(n[1]))
            ls = [any_of_anyVal(eval_expr(val)) for val in list_of_listVal(eval_expr(n[0]))]
            return return_expr(ls[int(index)])
        case "EPush":
            (n) = valid_args(exp, 2)
            v1 = list_of_listVal(eval_expr(n[0]))
            v2 = n[1]
            return return_expr(list([v2]+v1))  
        case "EHead":
            (n) = valid_args(exp, 1)
            v = list_of_listVal(eval_expr(n[0]))
            res = any_of_anyVal(eval_expr(v[0]))
            return return_expr(res)
        case "EArrlen":
            (n) = valid_args(exp, 1)
            v = list_of_listVal(eval_expr(n[0]))
            return return_expr(len(v))
        case "ETail":
            (n) = valid_args(exp, 1)
            v = list_of_listVal(eval_expr(n[0]))
            res = [eval_expr(val).vals for val in v[1:]]
            return return_expr(list(res))  
        case "ENot":
            (n) = valid_args(exp, 1)
            v = bool_of_boolVal(eval_expr(n[0]))
            return return_expr(bool(not v))
        case "EAnd":
            (n) = valid_args(exp, 2)
            v1 = bool_of_boolVal(eval_expr(n[0]))
            v2 = bool_of_boolVal(eval_expr(n[1]))
            return return_expr(bool(v1 and v2))
        case "EOr":
            (n) = valid_args(exp, 2)
            v1 = bool_of_boolVal(eval_expr(n[0]))
            v2 = bool_of_boolVal(eval_expr(n[1]))
            return return_expr(bool(v1 or v2))
        case "EIte":
            (n) = valid_args(exp, 3)
            v1 = bool_of_boolVal(eval_expr(n[0]))
            if(v1):
                return eval_expr(n[1])
            else:
                return eval_expr(n[2])  

        case any:
            return error(f"Interp Error: Not Implemented ({any})")

def interp(line):
    return eval_expr(ast.parse_AST(line))

def interpS(line):
    return "Onyun: "+string_of_expr(interp(line))

