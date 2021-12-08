from setuptools import setup

setup(
    name='HiveMind_presence',
    version='0.0.2a2',
    packages=['HiveMind_presence'],
    include_package_data=True,
    install_requires=["upnpclient>=0.0.8", "rich", "hivemind_bus_client~=0.0.3a2"],
    url='https://github.com/JarbasHiveMind/HiveMind-presence',
    license='MIT',
    author='jarbasAI',
    author_email='jarbasai@mailfence.com'
)
