import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="project_Kochanska",
    version="1.0",
    author="Kochańska Zofia",
    author_email="zk406116@students.mimuw.edu.pl",
    license="MIT",
    description="NYPD final project 2022/23",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zofiakk/NYPD_project",
    packages=['project_Kochanska', 'project_Kochanska.test'],
    entry_points = {
    'console_scripts': [
        'project_Kochanska=project_Kochanska.program:main',],},
    python_requires='>=3.6',
    install_requires=[
        'numpy==1.20.3',
        'pandas==1.3.4',
        'pytest==6.2.4'
    ],
)
