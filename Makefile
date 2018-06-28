develop: setup-git install-requirements

upgrade: install-requirements

setup-git:
	pip install "pre-commit>=1.10.1,<1.11.0"
	pre-commit install
	git config branch.autosetuprebase always
	git config --bool flake8.strict true
	cd .git/hooks && ln -sf ../../hooks/* ./

install-requirements: install-python-requirements install-js-requirements

install-python-requirements:
	pip install "setuptools>=17.0"
	pip install "pip>=9.0.0,<10.0.0"
	pip install -e .
	pip install "file://`pwd`#egg=gitboard[tests]"

install-js-requirements:
	yarn install

test:
	py.test tests
