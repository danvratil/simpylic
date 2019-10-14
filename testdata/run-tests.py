import json
import tempfile
import subprocess
import os
from io import StringIO

import simpylic as Simpylic

def main():
    with open('testdata/tests.json', encoding='utf-8') as infile:
        tests = json.load(infile)

    for test in tests:
        testfile = f'testdata/{test["test"]}.spy'
        print(f'Compiling {testfile}...', end='')

        buffer = StringIO()
        with open(testfile, encoding='utf-8') as src:
            Simpylic.run(src, buffer, Simpylic.Operation.Compile)
        buffer.seek(0)
        p = subprocess.Popen(['gcc', '-x', 'assembler', '-', '-o', '/tmp/simpylic-test-out'], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate(input = buffer.getvalue().encode('utf-8'))
        p.stdin.close()
        result = p.wait()
        if result != 0:
            raise RuntimeError(f'gcc error {result}: {err}')

        print('running...', end='')
        p = subprocess.Popen('/tmp/simpylic-test-out')
        result = p.wait()
        if result != int(test['return-code']) % 256:
            raise RuntimeError(f'The utility finished with return code {result} does not match the expected result {test["return-code"]}')

        print('OK.')

        os.remove('/tmp/simpylic-test-out')


if __name__ == '__main__':
    main()