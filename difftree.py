#! /usr/bin/env python3

_author__        = "James Ng"
__copyright__     = "Copyright 2016 James Ng"
__license__       = "GPL"
__version__       = "1.0"
__maintainer__    = "James Ng"
__email__         = "jng@slt.net"
__status__        = ""

import hashlib
import argparse
import os
import sys

# --- option processing and management
DEFAULT_BLOCK_SIZE = 8 * 1024 * 1024

pargs = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description='list the differences in files between two directories')
pargs.add_argument("-1", "--dir1", dest='dir1', required=True, help='first directory')
pargs.add_argument("-2", "--dir2", dest='dir2', required=True, help='second directory')
pargs.add_argument("-5", "--sha512", dest='sha512', action='count', help='use sha2-512 instead of sha2-256')
pargs.add_argument("-b", "--block-size", dest='chunk', metavar="<size>",type=int, help='block size to hash file, default 8192K', default=DEFAULT_BLOCK_SIZE)
pargs.add_argument("-r", "--reverse", dest='reverse', action='count', help='reverse comparison')
#
args = pargs.parse_args();

# --- reverse the src and dst directories
if args.reverse:
	dirswap = args.dir1
	args.dir1 = args.dir2
	args.dir2 = dirswap

# --- well, to compare directories, they must both be directories
for x in (args.dir1, args.dir2):
	if not os.path.isdir(x):
		print("{} is not a directory".format(x), file=sys.stderr)
		sys.exit(255)

# --- option validation
if args.chunk < 0:
	args.chunk = DEFAULT_BLOCK_SIZE

# --- for throwing exceptions
class PathError(Exception):
	def __init__(self, path, message):
		self.path = path
		self.message = message

def sha256(p):
	# --- path validation, open() throws useful errmsg so these are really redundant
	if not os.path.exists(p):
		raise PathError(p, "File not found")
	if os.path.isdir(p):
		raise PathError(p, "Is a directory")
	if not os.path.isfile(p):
		raise PathError(p, "Not a file")

	if args.sha512:
		hasher = hashlib.sha512()
	else:
		hasher = hashlib.sha256()

	# --- read the file in chunks so we don't blow up memory
	with open(p, "rb") as f:
		buf = True
		while buf:
			buf = f.read(args.chunk)
			hasher.update(buf)
	return hasher.hexdigest()

# --- walk a directory and return the sub-directories and files, paths are relative to the root provided.
def walktree(p):
	cwd = os.getcwd()
	os.chdir(p)
	treedirs = set()
	treefiles = set()
	for (root, dirs, files) in os.walk("."):
		for path in dirs:
			treedirs.add(os.path.normpath(os.path.join(root, path)))
		for path in files:
			treefiles.add(os.path.normpath(os.path.join(root, path)))

	os.chdir(cwd)
	return(treedirs, treefiles)

# --- bundle it into a class for easy access
class tree:
	def walk(self, root):
		self.root = root
		(self.dirs, self.files) = walktree(root)

	def __init__(self, root):
		self.walk(root)

	def print(self):
		for i in sorted(self.dirs):
			print("dir {}".format(i))
		for i in sorted(self.files):
			print("file {}".format(i))

	def printstatus(self):
		print("{}: {} dirs, {} files".format(self.root, len(self.dirs), len(self.files)))

try:
	dir1 = tree(args.dir1)
	dir2 = tree(args.dir2)

	dir1.printstatus()
	dir2.printstatus()

	print()
	print("The following directories are only in {}:".format(dir1.root))
	for i in sorted(dir1.dirs - dir2.dirs):
		print("exclusive_dir {}".format(i))

	print()
	print("The following directories are common to {} and {}:".format(dir1.root, dir2.root))
	for i in sorted(dir1.dirs & dir2.dirs):
		print("common_dir {}".format(i))

	print()
	print("The following directories are in missing in {}:".format(dir1.root))
	for i in sorted(dir2.dirs - dir1.dirs):
		print("missing_dir {}".format(i))

	print()
	print("The following files are only in {}:".format(dir1.root))
	for i in sorted(dir1.files - dir2.files):
		print("exclusive_file {}".format(i))

	print()
	print("The following files are common to {} and {}:".format(dir1.root, dir2.root))
	comfiles = (dir1.files & dir2.files)
	for i in sorted(comfiles):
		print("common_file {}".format(i))

	print()
	print("The following files are in missing in {}:".format(dir1.root))
	for i in sorted(dir2.files - dir1.files):
		print("missing_file {}".format(i))

	print()
	print("The following files have a different checksum in {}:".format(dir2.root))
	for i in (comfiles):
		if (sha256(os.path.join(dir1.root, i)) != sha256(os.path.join(dir2.root, i))):
			print("diff_file {}".format(i))
		#else:
		#	print(".".format(i), sep='')

except OSError as e:
	print("{}: {}".format(str(e.filename), e.strerror), file=sys.stderr)

except PathError as e:
	print("{}: {}".format(e.path, e.message), file=sys.stderr)
