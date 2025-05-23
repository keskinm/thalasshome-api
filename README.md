![CI](https://github.com/keskinm/thalasshome-api/actions/workflows/ci.yml/badge.svg)


## Browse

`gcloud app browse`

## Check logs

Interactive:
`gcloud app logs tail -s default`

Past:
`gcloud app logs read --limit=10`


## Cleaning deployments

`gcloud app versions list`

`gcloud app versions delete 20250302t153056`

Or don't even bother and delete all previous ones (with 0 traffic) directly:

`gcloud app versions list --format="value(VERSION.ID,TRAFFIC_SPLIT)" | awk '$2 == "0.00" {print $1}' | xargs gcloud app versions delete -q`

## 📦 Library Installation on Cloud (Google App Engine)
Google App Engine requires a requirements.txt file for dependency installation. Since we use Poetry for dependency management locally, we need to export the dependencies into a format that App Engine can process:

`poetry export -f requirements.txt --output requirements.txt --without-hashes`

👉 Key Points:

poetry export generates a flat list of dependencies in requirements.txt.

The `--without-hashes` flag ensures App Engine can process the file correctly.
Poetry is only used locally as a dependency management tool.

## 🚀 Deployment Process:

Generate requirements.txt (as shown above).
Ensure requirements.txt is included in Git (git add requirements.txt).
Deploy to App Engine: `gcloud app deploy`

## Dev library installation

`poetry install --with dev`


## Install pre-commit hooks

`poetry run pre-commit install`

### update

`poetry run pre-commit autoupdate`
