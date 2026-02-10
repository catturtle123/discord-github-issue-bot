# Run Tests

Run the project test suite.

## Steps
1. Run `python -m pytest tests/ -v` to execute all tests
2. If tests fail, analyze the output and fix issues
3. Run `python -m pytest tests/ -v --tb=short` for concise failure output
4. For coverage: `python -m pytest tests/ --cov=bot --cov=agent --cov=github --cov-report=term-missing`
