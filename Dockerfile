# syntax=docker/dockerfile:1
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN pip install --no-cache-dir build hatchling

# Copy only the files needed for the build
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Build a wheel
RUN python -m build --wheel --outdir /tmp/dist

# ── Runtime ──
FROM python:3.12-slim

WORKDIR /app

# Copy the wheel from the builder stage
COPY --from=builder /tmp/dist/*.whl /tmp/

# Install the wheel (no build deps at runtime)
RUN pip install --no-cache-dir /tmp/mcp_conformance-*.whl && \
    rm /tmp/mcp_conformance-*.whl

# The scenarios directory — mount at runtime to provide your own
RUN mkdir /scenarios
VOLUME /scenarios

ENTRYPOINT ["mcp-conformance"]
CMD ["--help"]
