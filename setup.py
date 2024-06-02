from setuptools import setup, find_packages

setup(
    name='ditto',
    version='0.1.0',
    author='ug1y',
    author_email='yinhao@icode.pku.edu.cn',
    description='A blockDAG simulation framework',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ug1y/ditto',
    packages='ditto',
    install_requires=[
        'networkx==3.3.0',
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: science/Research',
        'Topic :: Software Development :: libraries',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    extras_require={
        'test': ['pytest'],
    }
)
