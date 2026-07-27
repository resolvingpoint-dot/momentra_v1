.PHONY: test-financial-acceptance test-financial-acceptance-report compose-test-up compose-test-down

compose-test-up:
	docker compose -f docker-compose.test.yml up -d
	@echo "Postgres: localhost:15433 / momentra_test"
	@echo "Redis: localhost:6380"

compose-test-down:
	docker compose -f docker-compose.test.yml down -v

# Pure ledger + marked suites (no DB required for financial_calculations).
test-financial-acceptance:
	pytest app/tests/acceptance -v -m "financial and not slow"

# Full report path — set env for live API journey:
# DEBUG=true ALLOW_TEST_AUTH=true \
# ACCEPTANCE_DATABASE_URL=postgresql://momentra:momentra_test@localhost:15433/momentra_test \
# CELERY_TASK_ALWAYS_EAGER=true REDIS_URL=redis://localhost:6380/0
test-financial-acceptance-report:
	mkdir -p artifacts
	pytest app/tests/acceptance -v --junitxml=artifacts/momentra-junit.xml \
		-m "acceptance" || true
	@echo "Artifacts under backend/artifacts/"
