#!make
-include .env
export $(shell sed 's/=.*//' .env)
SHELL := /bin/bash

IMAGE_NAME = code.abifog.com/packages/searxng-mcp-server:latest

.PHONY: *

pex:
	uv pip compile pyproject.toml > requirements.txt
	uvx pex -r requirements.txt . -o ./build/searxng-mcp-server -e searxng_mcp_server:main --python python3

build:
	uv pip compile pyproject.toml > requirements.txt
	podman build -t $(IMAGE_NAME) .
	podman push $(IMAGE_NAME)

develop:
	uv venv ./.venv
	uv sync
	uv pip install -e .
	touch .env

format:
	uv tool run ruff format ./src

lint:
	uv tool run ruff check --fix src/
	uv tool run ruff check

mypy:
	mypy ./src

run:
	searxng-mcp-server

run-container:
	podman run --rm -it \
		--name searxng-mcp-server \
		$(IMAGE_NAME)