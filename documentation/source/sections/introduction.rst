A cookiecutter template for a python package
-------------------------------------------------

Features
~~~~~~~~~~~~
- package structure scaffold
- Documentation with `Sphinx <https://www.sphinx-doc.org/en/master/>`_
- dependency management with `Poetry <https://python-poetry.org/>`_
- code formatting with `Black <https://black.readthedocs.io/en/stable/index.html>`_
- import sorting with isort


Usage
~~~~~~~~
#. Cut your cookie
    You need to have cookiecutter installed.

    Run :code:`cookiecutter <path_to_this_cookiecutter>` from within the directory, where you want to create the
    new project.

#. Initialize git repo
    Run :code:`git init` and commit initial state.

#. Setup the poetry venv

#. Run :code:`pre-commit install` to setup pre-commit hooks.

ToDos
~~~~~~~~~~~~
- Add pytest
- Add mypy
- Sort imports with isort
- Remove dummy code in package (useful for api doc testing)
- Continuous Integration with TBD
