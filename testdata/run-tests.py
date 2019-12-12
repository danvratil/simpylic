import json
import subprocess
import os
from io import StringIO

import simpylic.simpylic as Simpylic


def log(msg):
    print(msg, end='', flush=True)


def main():
    with open('testdata/tests.json', encoding='utf-8') as infile:
        tests = json.load(infile)

    for test in tests:
        testfile = f'testdata/{test["test"]}.spy'
        log(f'Testing {testfile}...')

        log('compiling...')
        buffer = StringIO()
        with open(testfile, encoding='utf-8') as src:
            Simpylic.run(src, buffer, Simpylic.Operation.Compile)
        buffer.seek(0)
        compiler = subprocess.Popen(['gcc', '-x', 'assembler', '-', '-o', '/tmp/simpylic-test-out'],
                                    stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = compiler.communicate(input=buffer.getvalue().encode('utf-8'))
        compiler.stdin.close()
        result = compiler.wait()
        if result != 0:
            raise RuntimeError(f'gcc error {result}: {err}')

        log('running...')
        program = subprocess.Popen('/tmp/simpylic-test-out')
        result = program.wait()
        if result != int(test['return-code']) % 256:
            raise RuntimeError(f'The utility finished with return code {result} does not match '
                               'the expected result {test["return-code"]}')

        log('OK.\n')

        os.remove('/tmp/simpylic-test-out')


if __name__ == '__main__':
    main()
