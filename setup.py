from setuptools import setup, find_packages

setup(
    name='ditto',
    version='0.4.0',
    author='ug1y',
    author_email='yinhao@icode.pku.edu.cn',
    description='A hybrid blockDAG simulation framework',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    # url='https://github.com/ug1y/ditto',
    packages=find_packages(),
    install_requires=[
        'networkx==3.3.0',
        'numpy==1.26.0',
        'simpy==4.1.0',
        'bokeh==3.5.0',
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
