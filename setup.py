from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy

setup(ext_modules = cythonize([
    Extension('c_render',sources=['render.pyx'],language='c++',include_dirs=[numpy.get_include()],),
    Extension('c_cpu_addressing',sources=['cpu_addressing.pyx'],language='c++',),
    Extension('c_cpu',sources=['cpu.pyx'],language='c++',include_dirs=[numpy.get_include()],),
    Extension('c_cpu_instr',sources=['cpu_instr.pyx'],language='c++',)], compiler_directives={'profile': False}))