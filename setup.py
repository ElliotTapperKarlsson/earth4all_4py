from setuptools import setup, find_packages

setup(
    name="earth4all_4py",           
    version="0.1",                  
    packages=find_packages(where="src"),
    package_dir={"": "src"},       
    install_requires=[                
        'numpy>=1.21.0',
        'matplotlib>=3.4.0',
        'scipy>=1.6.0',
        'pandas>=1.2.0'    
    ],
    python_requires=">=3.7", 
    description="Python implementation of the Earth4All model", 
    long_description=open("README.md").read(),  
    long_description_content_type="text/markdown",
    url="https://github.com/ElliotTapperKarlsson/earth4all_4py", 
    author="Elliot Tapper Karlsson",
    author_email="elliottk@kth.se",  
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", 
        "Operating System :: OS Independent",
    ],
    license="MIT",
    keywords="earth4all, modeling, python",    
)

