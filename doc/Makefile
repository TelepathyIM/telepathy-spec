all: spec.html

spec.html: ../telepathy/*.py ../telepathy/server/*.py doc-generator.py
	chmod +x doc-generator.py
	PYTHONPATH=.. ./doc-generator.py telepathy.server order >spec.html
