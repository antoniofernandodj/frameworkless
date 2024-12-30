rsgi:
	uv run granian app:app --port 7000 --interface rsgi

asgi:
	uv run uvicorn app:app --port 7000
