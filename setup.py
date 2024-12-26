from setuptools import setup, find_packages

setup(
    name='ditto',
    version='0.7.4',
    author='ug1y',
    author_email='yinhao@icode.pku.edu.cn',
    description='Ditto: A Hybrid BlockDAG Simulation Framework',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ug1y/Ditto',
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires=[
        'networkx==3.3.0',
        'numpy==1.26.0',
        'simpy==4.1.0',
        'bokeh==3.5.0',
        'click==8.1.7'
    ],
    extras_require={'test': ['pytest']}
)
