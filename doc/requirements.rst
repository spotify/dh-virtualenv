===========
pipenv's conversation to get requirements.txt
===========
A Requirements file is just a list of pip install arguments placed in a file.

Uses of Requirements file:
------------
1)To achive a relatable installation Requirements files are used to hold 
  the result from pip freeze.

py -m pip freeze > requirements.txt
py -m pip install -r requirements.txt

2)Requirements files are used to resolve dependencies.
  if pkg1 requires pkg3>=1.0 and pkg2 requires pkg3>=1.0,<=2.0, and 
  if pkg1 is resolved first, pip will only use pkg3>=1.0, and 
  could easily end up installing a version of pkg3 that conflicts
  with the needs of pkg2. To solve this problem, you can place pkg3>=1.0,<=2.0
  (i.e. the correct specification) into your requirements file directly along 
  with the other top level requirements.

pkg1
pkg2
pkg3>=1.0,<=2.0

3)Requirements files are used to force pip to install an alternate version of a sub-dependency.
  For example, suppose ProjectA in your requirements file requires ProjectB, 
  but the latest version (v1.3) has a bug, you can force pip to accept earlier versions.

ProjectA
ProjectB<1.3

------------

How to generate Requirements.txt

------------
Below is the code using pip freeze :

pip3 freeze > requirements.txt  # Python3
pip freeze > requirements.txt  # Python2

pip freeze saves all packages in the environment including those 
that you don't use in your current project.
------------
Below is the code used to generate requirements.txt :

pip install pipreqs
pipreqs /path/to/project


