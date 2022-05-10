from readkw import *


#Lexer keywords
kws = KWLexer("lang.json").lexer_kw
kws_syn = kws["token-syntax"]
kws_id = kws["token-id"]

class Lexer:
    def __init__(self):
        pass

    def in_(val, ls):
        return val in ls

    def eval_string(sep_string, is_com=False):
        '''
        Evaluates a list of enumerated characters, and returns a list of character tokens

        Ex: "[(0, '5'), (1, '2'), (2, '+'), (3, 'a'), (4, ' ')]

        Returns: [{"DIGIT": '5'}, {"DIGIT: '2'}, {"ADD": '+'}, {"LETTER": 'a'}, {"WHITESPACE": ' '}]

        Handles comments and strings via is_com, allowing for any type of character to be passed while
        enabled

        Throws error at index of string if is_com is disabled and an unparseable token is found
        '''
        match sep_string:
            case []:
                return []

            case ([(_, ">"), (_, ">"), *t] | [(_, '"'), *t]) if not is_com:
                return Lexer.eval_string(sep_string, not is_com)

            case [(_, char), *t] if Lexer.in_(char, kws["token-defs"]["whitespace"]):
                return [{"WHITESPACE": char}]+Lexer.eval_string(t,False if char == '\n' else is_com)
            
            case [(_, char), *t] if Lexer.in_(char, kws["token-defs"]["digit"]):
                return [{"DIGIT": char}]+Lexer.eval_string(t, is_com)
            
            case [(_, char), *t] if Lexer.in_(char, kws["token-defs"]["letter"]):
                return [{"LETTER": char}]+Lexer.eval_string(t, is_com)
            
            case [(_, char), *t] if Lexer.in_(char, kws["token-syntax"]):
                return [{kws["token-syntax"][char]: char}]+Lexer.eval_string(t, is_com)
            
            case [(offset, char), *t]:
                if not is_com:
                    raise Exception(f"Lexer Error: Invalid string-rep token found at offset {offset}: <{char}>")
                else:
                    return [{"COMMENT": char}]+Lexer.eval_string(t, is_com)


    def eval_c_tok(c_tok):
        '''
        Evaluates a list of character tokens and returns a list of string tokens

        Ex: [{"LETTER": 'a'}, {"LETTER": 'b'}, {"LETTER": 's'}, {"CLBRAC": "("}, {"DIGIT": '5'}, {"CRBRAC": ")"}]
        
        Returns: [{"KEY": "abs"}, {"CLBRAC": '('}, {"NUMBER": '5'}, {"CRBRAC": ')'}]

        '''
        match c_tok:
            case []: 
                return []

            #single-line comment
            case [{"ARBRAC":_},{"ARBRAC":_}, *t]:
                fail = False
                try:
                    nl = t.index({'WHITESPACE': '\n'})
                    return Lexer.eval_c_tok(t[1+nl:])
                except:
                    fail = True
                if fail:
                    raise Exception("Lexer Error: Comment must end with newline")

            #string type
            case [{"QUOTE": '"'}, *t]:
                fail = False
                try:
                    eq = t.index({'QUOTE': '"'})
                    msg = ''.join([list(i.values())[0] for i in t[:eq]])
                    return [{"STRING": msg}]+Lexer.eval_c_tok(t[1+eq:])
                except:
                    fail = True
                if fail:
                    raise Exception("Lexer Error: string must end and begin with a quotation")

            case [{"DIGIT": c1}, {"DIGIT": c2}, *t] | [{"NUMBER": c1}, {"DIGIT": c2}, *t]:
                return Lexer.eval_c_tok([{"NUMBER": c1+c2}]+t)

            case [{"DIGIT": c}, *t]:
                return Lexer.eval_c_tok([{"NUMBER": c}]+t)

            case [{"LETTER": c1}, {"LETTER": c2}, *t] | [{"ID": c1}, {"LETTER": c2}, *t]:
                return Lexer.eval_c_tok([{"ID": c1+c2}]+t)

            case [{"LETTER": c}, *t]:
                return Lexer.eval_c_tok([{"ID": c}]+t)

            case [{"ID": id}, *t]:
                if Lexer.in_(id, kws_id):
                    return Lexer.eval_c_tok([{"KEY": id}]+t)
                else:
                    return [{"ID": id}] + Lexer.eval_c_tok(t)


            case [{"WHITESPACE": _}, *t]:
                return Lexer.eval_c_tok(t)
            #wildcard
            case [any, *t]:
                return [any]+Lexer.eval_c_tok(t)
    
    def parse_string(line):
        '''
        Fully parses a string into a list of string tokens

        Ex: "abs(5)"

        Returns: [{"KEY": "abs"}, {"CLBRAC": '('}, {"NUMBER": '5'}, {"CRBRAC": ')'}]
        '''
        return Lexer.eval_c_tok(Lexer.eval_string(list(enumerate(line))))

