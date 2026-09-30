.DEFAULT_GOAL := help
.PHONY: help setup lint format typecheck test ql-check check db db-docker \
        db-archive query query-csv docker-build clean clean-all

# User-configurable variables
SOURCE  ?=
URL     ?=
DB      ?=
SUITE   ?= all
ARCH      ?= x86_64
VERSION   ?= v6.13
TOOLCHAIN ?= gcc-13

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

setup: ## Install project dependencies
	uv sync --frozen

lint: ## Run linter
	uv run ruff check src/ tests/

format: ## Format code
	uv run ruff format src/ tests/

typecheck: ## Run the Python type checker
	uv run ty check src/ tests/

test: ## Run tests
	uv run pytest -q

ql-check: ## Compile-check every CodeQL query
	codeql query compile --check-only --keep-going --warnings=error -- queries/

check: lint ## Lint + format check + type check + test
	uv run ruff format --check src/ tests/
	uv run ty check src/ tests/
	uv run pytest -q

db: ## Build CodeQL database (SOURCE= or URL= required)
	$(if $(SOURCE),, $(if $(URL),, $(error Set SOURCE=/path/to/linux or URL=https://...)))
	uv run linux-ql build \
		-v $(VERSION) -a $(ARCH) \
		$(if $(SOURCE),-S $(SOURCE)) \
		$(if $(URL),-u $(URL))

db-docker: ## Build CodeQL database via Docker (SOURCE= or URL= required)
	$(if $(SOURCE),, $(if $(URL),, $(error Set SOURCE=/path/to/linux or URL=https://...)))
	uv run linux-ql docker \
		-a $(ARCH) --toolchain $(TOOLCHAIN) \
		$(if $(SOURCE),-S $(SOURCE)) \
		-- -v $(VERSION) -a $(ARCH) \
		$(if $(URL),-u $(URL))

db-archive: ## Compress a database for release (DB= required)
	$(if $(DB),, $(error Set DB=/path/to/database.db))
	tar -C "$(dir $(DB))" -cf - "$(notdir $(DB))" | zstd -T0 -9 -o "$(DB).tar.zst"

query: ## Run query suite (DB= required, SUITE= optional)
	$(if $(DB),, $(error Set DB=/path/to/database.db))
	uv run linux-ql query -d $(DB) -s $(SUITE)

query-csv: ## Run query suite with CSV export (DB= required)
	$(if $(DB),, $(error Set DB=/path/to/database.db))
	uv run linux-ql query -d $(DB) -s $(SUITE) --csv

docker-build: ## Build the per-arch Docker image (ARCH=, TOOLCHAIN=)
	docker build --platform linux/amd64 \
		--build-arg TUXMAKE_IMAGE=tuxmake/$(ARCH)_$(TOOLCHAIN):latest \
		-t linux-ql-$(ARCH)-$(TOOLCHAIN) .

clean: ## Remove build artifacts
	rm -rf .downloads/ results/ linux-*/

clean-all: clean ## Remove artifacts and databases
	rm -rf *.db
