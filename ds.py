from abstree import AbsTree as ast

def error(string):
    raise Exception(string)

def return_exp(exp):
    return ast.expr_cls("Ok", exp, f"Ok({exp}")

def valid_args(exp, *argmax):
    if(len(argmax)!=1):
        return exp.vals
    if exp.arglen > argmax[0]:
        raise Exception(f"{exp.id}: Too many arguments, takes {argmax[0]}, given {exp.arglen}")
    else:
        return exp.vals

def rem_ok(exp):
    match exp.id:
        case "Ok":
            return exp.vals
        case _:
            return exp

def extend_env(id, defin, env):
    if id in env:
        env[id] = [defin]+env[id]
    else:
        env[id] = [defin]
    return env
            
def apply_env(id, env, indx=0):
    if id in env:
        return env[id][indx]
    else:
        raise Exception(f"{id} not found!")

def any_of_anyVal(exp):
    match exp.vals.id:
        case "Num":
            return float(exp.vals.vals)
        case "Var" | "String":
            return str(exp.vals.vals)
        case "Bool":
            return bool(exp.vals.vals) 
        case "Tuple" | "List":
            return exp.vals.vals
        case _:
            return Exception("Type not found.")

def num_of_numVal(exp):
    match exp.vals.id:
        case "Num":
            return float(exp.vals.vals)
        case _:
            raise Exception("Expected a Num!")

def var_of_varVal(exp):
    match exp.vals.id:
        case "Var":
            return str(exp.vals.vals)
        case _:
            raise Exception("Expected a Var!")

def bool_of_boolVal(exp):
    match exp.vals.id:
        case "Bool":
            return bool(exp.vals.vals)
        case _:
            raise Exception("Expected a Bool!")

def string_of_stringVal(exp):
    match exp.vals.id:
        case "String":
            return str(exp.vals.vals)
        case _:
            raise Exception("Expected a String!")