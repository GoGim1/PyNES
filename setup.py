from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy
setup(ext_modules = cythonize([Extension(
    'c_render',
    sources=['render.pyx'],
    language='c++',
    include_dirs=[numpy.get_include()],
    library_dirs=[],
    libraries=[],
    extra_compile_args=[],
    extra_link_args=[]
    ),
    Extension(
    'c_cpu_addressing',
    sources=['cpu_addressing.pyx'],
    language='c++',
    include_dirs=[numpy.get_include()],
    library_dirs=[],
    libraries=[],
    extra_compile_args=[],
    extra_link_args=[]
    )

]))