#!/usr/bin/python

import glob, os, shutil, subprocess, sys, tempfile

tempdir = None
compiler = os.getcwd() + '/bootstrap/compile.py'

def runTest(test, source):
	print 'Running test', test

	files = {}
	compileArgs = None
	expect = None

	infile = None
	inexpect = None
	for line in source.split('\n'):
		if line and line[0] == '#':
			match = True
			elems = line.split(' ')
			if elems[0] == '#file' and not infile and not inexpect:
				infile = [elems[1], '']
			elif elems[0] == '#expect' and not infile and not inexpect:
				expect = ''
				inexpect = True
			elif elems[0] == '#end':
				if infile:
					files[infile[0]] = infile[1]
					infile = None
				elif inexpect:
					inexpect = None
			elif elems[0] == '#compile':
				compileArgs = elems[1:]
			else:
				match = False
			if match:
				continue

		if inexpect:
			expect += line + '\n'
		elif infile:
			infile[1] += line + '\n'

	for fn, source in files.items():
		file(fn, 'w').write(source)

	args = [compiler] + compileArgs
	if subprocess.call(args) != 0:
		print 'Failed to compile'
		return False
	print 'Succeeded'
	return True

def main(*tests):
	global tempdir
	tempdir = tempfile.mkdtemp()
	origdir = os.getcwd()

	if not tests:
		tests = glob.glob('test/*.test')

	succeeded = 0
	for test in tests:
		try:
			source = file(test).read()
		except:
			print 'Could not read test', test
			return 1

		os.chdir(tempdir)
		succeeded += 1 if runTest(test, source) else 0
		os.chdir(origdir)
		print

	shutil.rmtree(tempdir)

	print 'Total:', len(tests)
	print 'Succeeded:', succeeded
	print 'Failed:', len(tests) - succeeded

if __name__=='__main__':
	sys.exit(main(*sys.argv[1:]))
