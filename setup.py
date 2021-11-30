from setuptools import setup

setup(
    name='HiveMind_presence',
    version='0.0.1',
    packages=['HiveMind_presence'],
    include_package_data=True,
    install_requires=["upnpclient>=0.0.8", "rich"],
    url='https://github.com/JarbasHiveMind/HiveMind-presence',
    license='MIT',
    author='jarbasAI',
    author_email='jarbasai@mailfence.com',
    entry_points={
        'console_scripts': [
            'HiveMind-scan=HiveMind_presence.cli:scan_and_print',
            'HiveMind-announce=HiveMind_presence.__main__:main'
        ]
    }
)
