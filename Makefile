.PHONY: test

 test:
	# ignore coverage of tests
	pytest --cov --cov-report html --cov-report term 

show-coverage:
	open htmlcov/index.html