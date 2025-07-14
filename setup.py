from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kleinanzeigen-buecherwurm",
    version="0.1.0",
    author="Hannes",
    author_email="hannesgao.eth",
    description="A crawler for finding free antique book collections on Kleinanzeigen.de",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hannesgao/Kleinanzeige-Buecherwurm",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "selenium>=4.18.1",
        "beautifulsoup4>=4.12.3",
        "sqlalchemy>=2.0.25",
        "loguru>=0.7.2",
        "pyyaml>=6.0.1",
        "python-dotenv>=1.0.1",
        "requests>=2.31.0",
        "pandas>=2.2.0",
        "schedule>=1.2.0",
        "APScheduler>=3.10.4",
    ],
    entry_points={
        "console_scripts": [
            "kleinanzeigen-crawler=main:main",
        ],
    },
)