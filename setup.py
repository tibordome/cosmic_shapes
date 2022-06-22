import pathlib
from setuptools import find_packages, setup
from distutils.core import Extension
import numpy as np
import os
import sysconfig
from Cython.Build import cythonize
from Cython.Distutils import build_ext

def get_ext_filename_without_platform_suffix(filename):
    """ Retrieve filename of default cython files without the machine-dependent suffixes"""
    name, ext = os.path.splitext(filename)
    ext_suffix = sysconfig.get_config_var('EXT_SUFFIX')

    if ext_suffix == ext:
        return filename

    ext_suffix = ext_suffix.replace(ext, '')
    idx = name.find(ext_suffix)

    if idx == -1:
        return filename
    else:
        return name[:idx] + ext

class BuildExtWithoutPlatformSuffix(build_ext):
    """ Build Cython with naming convention that discards the machine-dependent suffixes"""
    def get_ext_filename(self, ext_name):
        filename = super().get_ext_filename(ext_name)
        return get_ext_filename_without_platform_suffix(filename)

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

ext_modules=[Extension(
                "cosmic_profiles.cython_helpers",
                sources=['cosmic_profiles/cython_helpers.c'],
                extra_compile_args=["-fopenmp"],
                extra_link_args=["-fopenmp"],
                include_dirs=[np.get_include(), '.']
            ), Extension(
                "cosmic_profiles.gen_csh_gx_cat",
                sources=['cosmic_profiles/gen_csh_gx_cat.c'],
                extra_compile_args=["-fopenmp"],
                extra_link_args=["-fopenmp"],
                include_dirs=[np.get_include(), '.']
            ), Extension(
                "cosmic_profiles.cosmic_profiles",
                sources=['cosmic_profiles/cosmic_profiles.c'],
                extra_compile_args=["-fopenmp"],
                extra_link_args=["-fopenmp"],
                include_dirs=[np.get_include(), '.']
            )]

# This call to setup() does all the work
setup(
    name="cosmic_profiles",
    version="1.0.0",
    description="Implements 3D point cloud algorithms for estimation and fitting of shape and density profiles",
    long_description=README,
    long_description_content_type="text/markdown",
    project_urls={
    'Documentation': 'https://cosmic-profiles.readthedocs.io/en/latest/',
    'Source': "https://github.com/tibordome/cosmic_profiles"
    },
    author="Tibor Dome",
    author_email="tibor.doeme@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Science/Research",
        "Operating System :: POSIX",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    cmdclass={'build_ext': BuildExtWithoutPlatformSuffix},
    ext_modules = cythonize(ext_modules),
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=["cython", "numpy>=1.19.2", "scikit-learn", "mpi4py", "h5py", "matplotlib", "pynbody", "nbodykit", "pynverse"]
)

