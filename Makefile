run_dev_env:
	cd deployments; docker compose -f docker-compose.dev.yml up

clean_dev_env:
	docker stop project_base_dev project_base_postgres project_base_postgres_test project_base_pgweb || true
	docker rm -f project_base_dev project_base_postgres project_base_postgres_test project_base_pgweb || true

build: build_docker build_precommit

build_docker:
	rm -rf .venv;cd deployments; DOCKER_BUILDKIT=1 docker build -t dev/project_base:latest -f Dockerfile.dev ..

# somehow it need to be rebuild to check new files todo fix
run_precommit:
	nix develop . --command pre-commit run --all-files

install_hooks:
	chmod +x deployments/hooks/*
	cp deployments/hooks/* .git/hooks/

clean:
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

go_in_docker:
	docker exec -it project_base_dev /bin/bash

test:
	poetry run pytest

run_dev_frontend:
	cd sources/frontend && npm run dev 
