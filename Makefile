rsgi:
	uv run granian app:app --port 7000 --interface rsgi

asgi:
	uv run uvicorn app:app --port 7000

test:
	uv run python -m unittest discover \
		--start-directory tests\
		--locals \
		--buffer \
		--verbose \
		--pattern "test_*.py" \
		--top-level-directory .
