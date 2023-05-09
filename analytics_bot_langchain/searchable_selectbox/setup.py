import setuptools

setuptools.setup(
    name="my-component",
    version="0.1.0",
    packages=["my_component"],
    include_package_data=True,
    install_requires=[
        "streamlit>=0.83"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)