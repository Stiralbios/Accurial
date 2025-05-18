# Configure Pycharm

## Marking directories
- Mark `sources` as root directory


## Add python interpreter
- Add new `docker compose` interpreter
- Select `deployments/docker-compose.dev.yml`
- Select `project_base_dev`
- Next
- Select `Vitual Environment`
- Add `/home/project_base/.venv/bin/python` as path
- You are all set


## Adding test config
- Nothing for now, just `make clean_dev_env` a lot (it will erase data from the db so not great :/)