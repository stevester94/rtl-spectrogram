from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize( ["src/Orig_PLL.py", "src/Fast_PLL.py", "src/Fast_Cython_PLL.pyx"] )
)
