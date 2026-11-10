"""Small strict JSON CLI. Errors never leave partial report stdout."""
import argparse,json,sys
from .engine import compare
from .verify import verify
from .model import loads
from .controls import controls

def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['demo','run','verify']);p.add_argument('path',nargs='?');args=p.parse_args()
    try:
        if args.command=='demo':result=compare(controls()[0]['input'])
        else:
            if not args.path:raise ValueError('path required')
            limit=65536 if args.command=='run'else 8*1024*1024
            with open(args.path,'rb')as f:raw=f.read(limit+1)
            if len(raw)>limit:raise ValueError('file size bound')
            data=loads(raw.decode('utf-8'))
            result=compare(data)if args.command=='run'else {'valid':verify(data)}
        text=json.dumps(result,sort_keys=True,separators=(',',':'),allow_nan=False);print(text)
    except (ValueError,OSError,UnicodeError)as e:print(str(e),file=sys.stderr);return 2
    return 0
if __name__=='__main__':raise SystemExit(main())
