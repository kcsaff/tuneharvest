.PHONY: install clean
install:
	python3 setup.py install

venv:
	python3 -m venv venv
	bash -c ". venv/bin/activate; pip3 install -r requirements.txt"

clean:
	rm -rf venv

