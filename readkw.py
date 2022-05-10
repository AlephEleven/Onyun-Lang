import sys
sys.tracebacklimit = 0


import json

class KWHandler:
    def __init__(self, kw):
        self.kw = ""
        self.readjson(kw)

    def readjson(self, filename):
        with open(filename, 'r') as f:
            self.kw = json.load(f)

    def __str__(self):
        return json.dumps(self.kw, indent=4)


class KWLexer(KWHandler):
    def __init__(self, kw):
        super().__init__(kw)
        self.lexer_defs()
        self.lexer_kw = self.kw["Lexer"]

    def lexer_defs(self):
        '''
        Fill Lexer section with single-character defintions
        '''
        tk_defs = {
            "whitespace": [' ', '\t', '\n'],
            "digit": [chr(i) for i in range(48, 58)],
            "letter": [chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)]
        }

        self.kw["Lexer"]["token-defs"] = tk_defs