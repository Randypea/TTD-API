from setuptools import setup, find_packages

setup(
    name='ttdapi',
    use_scm_version=True,
    setup_requires=['setuptools-scm', 'pytest-runner'],
    url='https://github.com/pocin/thetradingdesk-python-client',
    download_url='https://github.com/pocin/thetradingdesk-python-client',
    packages=find_packages(exclude=['tests']),
    test_suite='tests',
    tests_require=['pytest']
)
