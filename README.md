# QUICKLCOUDY

QUICKLCOUDY is a small image-format conversion web application. A browser frontend uploads an image, the API queues the work, and a worker converts the file with Pillow.

## Architecture

```
browser -> frontend (nginx / Vite) -> API (FastAPI) -> Redis queue -> worker (Pillow)
                                         |                              |
                                         +------ shared file storage ---+
```

1. The frontend uploads an image and the requested output format.
2. The API validates the file, stores it, and enqueues a job in Redis.
3. The worker converts the image and writes the result to shared storage.
4. The frontend polls job status and downloads the converted file from the API.

Supported formats: JPEG / JPG, PNG, and WEBP. Uploads are limited to 10 MB.

## Services

| Service  | Role                                      | Default local port |
|----------|-------------------------------------------|--------------------|
| frontend | Upload UI, status, and download           | 5173 (dev), 8080 (Compose) |
| api      | REST API, validation, job status, files   | 8000 (Compose host port: 8001) |
| worker   | Image conversion                          | none |
| redis    | Job queue and job metadata                | 6379 |

## Environment variables

### API

| Variable       | Default                                           | Description |
|----------------|---------------------------------------------------|-------------|
| `REDIS_URL`    | `redis://localhost:6379/0`                        | Redis connection string |
| `DATA_DIR`     | `./data`                                          | Directory for uploads and outputs |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:8080`     | Comma-separated allowed origins |
| `MAX_UPLOAD_BYTES` | `10485760`                                    | Maximum upload size |

### Worker

| Variable     | Default                    | Description |
|--------------|----------------------------|-------------|
| `REDIS_URL`  | `redis://localhost:6379/0` | Redis connection string |
| `DATA_DIR`   | `./data`                   | Must match the API when running locally |

The worker reads the file paths stored on each job. When running the API and worker on the same machine, give both the same absolute `DATA_DIR`.

### Frontend (Docker image)

| Variable   | Default | Description |
|------------|---------|-------------|
| `API_HOST` | `api`   | Hostname of the API service used by nginx |
| `API_PORT` | `8000`  | API port used by nginx |

Local Vite development proxies `/api` and `/health` to `http://localhost:8000` (the local uvicorn port, not the Compose host port).

## Run locally

Prerequisites: Python 3.12+, Node.js 20+, and a running Redis instance.

```bash
# from the repository root
export DATA_DIR="$(pwd)/data"
export REDIS_URL="redis://localhost:6379/0"

python3 -m venv .venv
source .venv/bin/activate
pip install -r api/requirements.txt -r worker/requirements.txt

# terminal 1
cd api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# terminal 2
cd worker && python -m app.main

# terminal 3
cd frontend && npm install && npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

## Run with Docker Compose

```bash
docker compose up --build
```

Open [http://localhost:8080](http://localhost:8080).

The API is also available at [http://localhost:8001](http://localhost:8001). Compose publishes the API on host port `8001` so it does not collide with other local services using `8000`. Inside the Compose network the API still listens on port `8000`.

Stop with `docker compose down`.

## Build each Docker image

Each image builds from its own directory:

```bash
docker build -t quicklcoudy-frontend ./frontend
docker build -t quicklcoudy-api ./api
docker build -t quicklcoudy-worker ./worker
```
