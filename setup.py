from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Information Technology',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3',
    'Topic :: Security'
]


setup(
    name ='EC2StepShell',
    version ='0.0.1',
    description ='EC2StepShell is an AWS post-exploitation tool for getting reverse shells in public or private EC2 instances',
    long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
    author = 'Eduard Agavriloae',
    author_email='saw-your-packet@breakingbreakpoints.com',
    license='MIT',
    classifiers=classifiers,
    keywords='EC2StepShell',
    packages=find_packages(),
    requires=['colorama', 'termcolor', 'pyfiglet', 'boto3'],
    url='https://github.com/saw-your-packet/EC2StepShell',
    py_modules=['ec2stepshell']
)