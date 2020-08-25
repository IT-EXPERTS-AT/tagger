# Taggercore

## About
Taggercore contains utility classes for scanning AWS resources and applying tags to them.
The `usecase` package contains opinionated functions for performing tasks like scanning a region and global resources (e.g. IAM) or comparing resources to a certain tagging schema (e.g. `create_report.py`).
## Installation
Taggercore can be installed by running  
`pip install taggercore`

## Development

Install requirements:  
`pipenv install -e .[dev]`  

Run tests:  
`tox`
