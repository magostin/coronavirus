.PHONY: clean data lint requirements sync_data_to_s3 sync_data_from_s3

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
BUCKET = [OPTIONAL] your-bucket-for-syncing-data (do not include 's3://')
PROFILE = default
PROJECT_NAME = coronavirus
PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install Python Dependencies
requirements: test_environment
	$(PYTHON_INTERPRETER) -m pip install -U pip setuptools wheel
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt

update:
	git -C data/raw/COVID-19 pull origin master
	git -C data/raw/protezione-civile pull origin master

## Make Dataset
data: update
	rm -f data/processed/data.h5
	$(PYTHON_INTERPRETER) src/data/make_dataset.py data/raw data/processed

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using flake8
lint:
	flake8 src

## Upload Data to S3
sync_data_to_s3:
ifeq (default,$(PROFILE))
	aws s3 sync data/ s3://$(BUCKET)/data/
else
	aws s3 sync data/ s3://$(BUCKET)/data/ --profile $(PROFILE)
endif

## Download Data from S3
sync_data_from_s3:
ifeq (default,$(PROFILE))
	aws s3 sync s3://$(BUCKET)/data/ data/
else
	aws s3 sync s3://$(BUCKET)/data/ data/ --profile $(PROFILE)
endif

report:
	papermill "notebooks\parametrized\riepilogo_regione.ipynb" "notebooks\reports\veneto.ipynb" -p regione 5
	papermill "notebooks\parametrized\riepilogo_regione.ipynb" "notebooks\reports\friuli.ipynb" -p regione 6
	papermill "notebooks\parametrized\riepilogo_regione.ipynb" "notebooks\reports\lombardia.ipynb" -p regione 3
	papermill "notebooks\parametrized\country_summary.ipynb" "notebooks\reports\italy.ipynb" -p country 'Italy'
	papermill "notebooks\parametrized\country_summary.ipynb" "notebooks\reports\austria.ipynb" -p country 'Austria'
	#papermill "notebooks\parametrized\country_summary.ipynb" "notebooks\reports\germany.ipynb" -p country 'Germany'
	#papermill "notebooks\parametrized\country_summary.ipynb" "notebooks\reports\spain.ipynb" -p country 'Spain'
	#papermill "notebooks\parametrized\country_summary.ipynb" "notebooks\reports\france.ipynb" -p country 'France'
	#papermill "notebooks\parametrized\country_summary.ipynb" "notebooks\reports\USA.ipynb" -p country 'United States of America'
	#papermill "notebooks\parametrized\country_summary.ipynb" "notebooks\reports\UK.ipynb" -p country 'United Kingdom'
	jupyter nbconvert --execute --to html notebooks/reports/*.ipynb --no-input --output-dir=reports
