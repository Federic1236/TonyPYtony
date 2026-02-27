from setuptools import setup, find_packages

setup(
    name="tonyPYtony",
    version="0.1.0",
    author="Federic and Garnaaax",
    description="Forza Tony Pitony!",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Federic1236/tonyPYtony",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'tony=tonypytony.interpreter:main',
        ],
    },
)
