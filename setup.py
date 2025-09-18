from setuptools import setup, find_packages

setup(
    name="mStock-TradingApi-A",
    version="0.0.0",
    author="Mirae Asset Capital Markets (India) Private Limited", 
    description="A Python SDK for Connecting to mStock Trading API and Streaming API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/MiraeAsset-mStock/pytradingapi-typeA",
    packages=find_packages(),
    package_dir={'mStock-TradingApi-A': 'tradingapi_a'},
    install_requires=[
        "autobahn", 
        "requests",
        "responses",
        "pytest",
        "setuptools",
        "twisted"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries"
    ],
    
    python_requires=">=3.11",
) 