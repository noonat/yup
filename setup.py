import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

lib_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
with open(os.path.join(lib_dir, 'yup', '_version.py'), 'r') as version_file:
    exec(version_file.read())

setup(
    name='yup',
    version=__version__,
    author='Nathan Ostgard',
    author_email='no@nathanostgard.com',
    description='Generate REST API documentation from YAML files',
    long_description='yup generates REST API documentation from YAML files',
    url='https://github.com/noonat/yup',
    license='Apache License, Version 2.0',
    packages=['yup'],
    package_data={'yup': ['data/template.html',
                          'data/css/*.css',
                          'data/css/fonts/*.eot',
                          'data/css/fonts/*.ttf',
                          'data/css/fonts/*.woff']},
    package_dir={'yup': 'yup'},
    include_package_data=True,
    scripts=['scripts/yup'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License'],
    install_requires=['setuptools',
                      'jinja2',
                      'misaka',
                      'pygments',
                      'pyyaml',
                      'requests'],
    extras_require={},
    tests_require=[],
    zip_safe=False)
