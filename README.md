# yup

yup generates HTML documentation for your REST API from YAML files. It will
perform HTTP requests against the API endpoint to validate that your examples
work, and to capture example responses for the documentation.

Installation:

    pip install yup

Usage:

    yup --input-dir DIR --output-dir DIR --url http://127.0.0.1

Options:

- `input-dir` is the directory to read YAML files from.
- `output-dir` is the directoy to write HTML files into.
- `url` is the base URL to use for example requests.
