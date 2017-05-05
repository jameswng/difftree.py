
## DIFFTREE.PY

*difftree.py* compares two directories and determines how dir2 differs from dir1
```
usage: difftree.py [-h] -1 DIR1 -2 DIR2 [-5] [-b <size>] [-r]

list the differences in files between two directories

optional arguments:
  -h, --help            show this help message and exit
  -1 DIR1, --dir1 DIR1  first directory
  -2 DIR2, --dir2 DIR2  second directory
  -5, --sha512          use sha2-512 instead of sha2-256
  -b <size>, --block-size <size>
                        block size to hash file, default 8192K
  -r, --reverse         reverse comparison
