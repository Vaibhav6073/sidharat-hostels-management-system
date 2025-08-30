from setuptools import setup, find_packages

setup(
    name="sidharat-hostels",
    version="1.0.0",
    description="Complete Hostel Management System",
    author="Sidharat Hostels",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask>=2.3.0',
    ],
    entry_points={
        'console_scripts': [
            'sidharat-hostels=app:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)