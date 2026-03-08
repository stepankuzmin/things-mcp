FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock .python-version ./
RUN uv python install 3.14 --managed-python
RUN uv sync --managed-python --locked --no-dev

COPY src/ src/
COPY get_things_db_path.sh backup_things_db.sh ./

CMD ["uv", "run", "--managed-python", "--locked", "python", "src/main.py"]
