.RECIPEPREFIX := >

.PHONY: lint typecheck test-unit test-integration test-e2e test verify worker-smoke worker-logged

lint:
>uv run ruff check .

typecheck:
>uv run mypy src

test-unit:
>uv run pytest tests/unit -m "not integration and not e2e"

test-integration:
>uv run pytest tests/integration -m integration

test-e2e:
>uv run pytest tests/e2e -m e2e

test: test-unit test-integration test-e2e

verify: lint typecheck test

worker-smoke:
>uv run python -m {{PYTHON_PACKAGE_NAME}}.worker.main --once --seed-demo-if-empty

worker-logged:
>mkdir -p logs
>LOG_FILE="logs/worker-$$(date +%Y%m%d-%H%M%S).log"; \
>LOG_LEVEL="$${LOG_LEVEL:-INFO}"; \
>echo "Writing worker log to $$LOG_FILE"; \
>uv run python -m {{PYTHON_PACKAGE_NAME}}.worker.main --log-file "$$LOG_FILE" --log-level "$$LOG_LEVEL"
