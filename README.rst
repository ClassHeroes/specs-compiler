Spec compiler
-------------

Usage
~~~~~

Ensure that python 3.6 and .direnv is installed, then::

  make install
  make compile
  open build

Note that the configuration assumes that the specs repository is located at ``../specs-sources`` or in ``./specs-sources``.

Exposed in a container as:

  docker.com/classheroes/specs-compiler:latest
