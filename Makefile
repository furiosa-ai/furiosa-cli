compile:
	python ./setup.py develop
lint:
	pylint nux
test:
	python -m unittest discover -v -s ./test
clean:
	rm -rf build dist furiosacli.egg-info

default: compile