import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='jintonic',
    version='0.0.1',
    author='Ismail Negm',
    author_email='ismailnegm@protonmail.com',
    url='https://github.com/inegm/jintonic',
    license='MIT License',
    description='Just Intonation with Python',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
