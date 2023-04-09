import json
import datetime


def load_jsonl(fn):
    with open(fn) as fp:
        for line in fp:
            yield fn, json.loads(line)


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat(sep=' ')  # XXX: date only


class JsonOutputter:
    def __init__(self, dbname):
        self.dbname = dbname
        self.outputs = {}  # tblname -> fp
        self.encoder = JsonEncoder()

    def output(self, tblname, row):
        if tblname not in self.outputs:
            fn = f'{self.dbname}-{tblname}.jsonl'
            self.outputs[tblname] = open(fn, 'w')

        self.outputs[tblname].write(self.encoder.encode(row) + '\n')

    def close(self):
        for fp in self.outputs.values():
            fp.close()
