# epicsarchiver

![License](https://img.shields.io/badge/license-MIT-orange.svg) ![Python](https://img.shields.io/badge/python-v3.11-22558a.svg?logo=python&color=22558a) ![FastAPI](https://img.shields.io/badge/FastAPI-v0.105.0-3b9388.svg?logo=fastapi&color=3b9388) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-v2.0.23-brown.svg)

Archiving Epics PVs with Python and SQL

------------
## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

------------
## Installation

### Development
To set up the project for development, just clone the repository, install all the requirements, the project and the pre-commit hooks.

```bash
git clone -b main https://github.com/pyepics/epicsarchiver/git && cd epicsarchiver
pip install -r requirements.txt && pip install -r requirements_dev.txt
pip install -e .
pre-commit install
```

> Pre-commit is a tool that checks your code for any errors before you commit it. It helps maintain the quality of the codebase and reduces the chance of pushing faulty code. When you try to commit your changes, pre-commit will run checks defined in the [.pre-commit-config.yaml](.pre-commit-config.yaml) file. If any of these checks fail, the commit will be aborted.

### Running the Server
After setting up the project for development, you can start the Uvicorn server by running the [epicsarchiver.py](epicsarchiver.py) file:

```bash
python epicsarchiver.py
```


[back to top](#table-of-contents)

------------
## Usage

[back to top](#table-of-contents)

------------
## Contributing

All contributions to epicsarchiver are welcome! Here are some ways you can help:
- Report a bug by opening an [issue](https://github.com/pyepics/epicsarchiver/issues).
- Add new features, fix bugs or improve documentation by submitting a [pull request](https://github.com/pyepics/epicsarchiver/pulls).

Please adhere to the [GitHub flow](https://docs.github.com/en/get-started/quickstart/github-flow) model when making your contributions! This means creating a new branch for each feature or bug fix, and submitting your changes as a pull request against the main branch. If you're not sure how to contribute, please open an issue and we'll be happy to help you out.

By contributing to epicsarchiver, you agree that your contributions will be licensed under the MIT License.

[back to top](#table-of-contents)

------------
## License

epicsarchiver is distributed under the MIT license. You should have received a [copy](LICENSE) of the MIT License along with this program. If not, see https://mit-license.org/ for additional details.