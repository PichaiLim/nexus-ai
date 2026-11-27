FROM python:3.15.2-slim AS build
WORKDIR /build
COPY apps/api/requirements.txt .
RUN python -m venv /opt/nexus && /opt/nexus/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.15.2-slim AS runtime
ENV PATH="/opt/nexus/bin:$PATH" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY --from=build /opt/nexus /opt/nexus
COPY apps/api/nexus_ai ./nexus_ai
USER 10001:10001
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "nexus_ai.main:app", "--host", "0.0.0.0", "--port", "8000"]
