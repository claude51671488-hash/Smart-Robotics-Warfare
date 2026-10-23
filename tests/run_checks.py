"""Run source checks; exclusions are explicit and never count as passes."""
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import subprocess
import sys


def main():
    root=Path(__file__).resolve().parents[1]
    checks=sorted((root/'tests').glob('check_*.py'))
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--exclude',action='append',default=[],choices=[p.name for p in checks])
    parser.add_argument('--jobs',type=int,default=1)
    parser.add_argument('--report',type=Path,help='Optional JSON report; contains check output')
    args=parser.parse_args()
    if args.jobs<1:
        parser.error('--jobs must be positive')
    selected=[p for p in checks if p.name not in args.exclude]

    def run(check):
        try:
            result=subprocess.run([sys.executable,str(check)],cwd=root,text=True,
                                  capture_output=True,timeout=120)
            return {'test':check.name,'passed':result.returncode==0,
                    'output':result.stdout+result.stderr}
        except (OSError,subprocess.TimeoutExpired) as error:
            return {'test':check.name,'passed':False,'output':str(error)}

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results=list(pool.map(run,selected))
    for result in results:
        print(('PASS' if result['passed'] else 'FAIL')+': '+result['test'])
        if not result['passed']:
            print(result['output'])
    passed=sum(result['passed'] for result in results)
    excluded=sorted(set(args.exclude))
    print(f'{passed}/{len(results)} passed; {len(excluded)} explicitly excluded')
    if excluded:
        print('Excluded: '+', '.join(excluded))
    if args.report:
        args.report.write_text(json.dumps({'results':results,'excluded':excluded},
                                         ensure_ascii=False,indent=2),encoding='utf-8')
    return 0 if passed==len(results) else 1


if __name__=='__main__':
    sys.exit(main())
