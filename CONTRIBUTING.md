# Contributing

If you are looking to contribute to the codebase, the following instructions should help you set up your environment.

### Guidelines
For ease of development, we utilize pre-commit hooks and GitHub Actions in order to keep consistent formatting.

These include:
- Ruff code formatting
- Trailing whitespace trimmer
- EOF newline checks
- YAML and JSON formatting checks
- File size limiter (currently 150kb)
- 'requirements.txt' validator
- Private key detection
- Branch committing restrictions

### Prerequisites
This script is developed with *Python 3.13*.

### Installation
To clone and set up the repo,

```bash
git clone https://github.com/Furglitch/modorganizer2-linux-installer -b rewrite
cd modorganizer2-linux-installer
python -m venv ./venv
source ./venv/bin/activate
pip install -r ./requirements.txt
pre-commit install
```
