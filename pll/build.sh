set -eou pipefail
python3 setup.py build_ext
cp build/lib.linux*/*.so .