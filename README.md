# LCRA Flood Status Web Data Extractor API

A robust FastAPI-based service for extracting real-time flood status, lake levels, river conditions, and floodgate operations from the Lower Colorado River Authority (LCRA) Hydromet system.

---

## Overview

This project provides a RESTful API to access current flood status, lake levels, river conditions, and floodgate operations for the Lower Colorado River basin in Texas. It fetches data directly from LCRA's public APIs, structures it with Pydantic models, and exposes it via a modern, documented FastAPI interface.

---

## Features

- **Real-time Data**: Fetches up-to-date information from LCRA's official APIs.
- **Structured Models**: Uses Pydantic for data validation and serialization.
- **Multiple Endpoints**: Access lake levels, river conditions, floodgate operations, and a complete flood report.
- **Async & Fast**: Built with FastAPI and httpx for high performance.
- **Interactive Docs**: Swagger UI available at `/docs`.
- **Health Check**: `/health` endpoint to verify service and LCRA API availability.

---

## Requirements

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) (for dependency management)

---

## Setup & Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd lcra
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

---

## Usage

### Start the API Server

You can serve the API using the new CLI entrypoint:

```bash
python main.py serve --host 0.0.0.0 --port 8080
```
- The server will start on `http://localhost:8080/` by default.
- Swagger UI is available at [http://localhost:8080/docs](http://localhost:8080/docs)

### Extract LCRA Data from the Command Line

You can extract and print LCRA data directly using the CLI:

- **Full Flood Operations Report:**
  ```bash
  python main.py get --report
  ```
- **Lake Levels:**
  ```bash
  python main.py get --lake-levels
  ```
- **River Conditions:**
  ```bash
  python main.py get --river-conditions
  ```
- **Floodgate Operations:**
  ```bash
  python main.py get --floodgate-operations
  ```
- You can combine flags to extract multiple data types at once.

#### Save Output to a JSON File

You can save the result to a file in the `reports/` folder:

- **Auto-named (timestamped) file:**
  ```bash
  python main.py get --report --save
  # -> reports/report_2024-06-07T12-34-56.json
  ```
- **Custom filename:**
  ```bash
  python main.py get --report --saveas my_report
  # -> reports/my_report.json
  ```

Use `--save` for an auto-generated timestamped filename, or `--saveas <filename>` to specify a custom filename.

---

## API Endpoints

| Endpoint                  | Method | Description                                 |
|--------------------------|--------|---------------------------------------------|
| `/`                      | GET    | API root info                               |
| `/health`                | GET    | Health check (LCRA API connectivity)        |
| `/flood-report`          | GET    | Complete flood operations report            |
| `/lake-levels`           | GET    | Current lake levels at dams                 |
| `/river-conditions`      | GET    | Current river conditions                    |
| `/floodgate-operations`  | GET    | Current floodgate operations                |
| `/docs`                  | GET    | Swagger UI (interactive API docs)           |

---

## Example API Usage

### Get Complete Flood Report
```bash
curl http://localhost:8080/flood-report
```

### Get Lake Levels
```bash
curl http://localhost:8080/lake-levels
```

### Get River Conditions
```bash
curl http://localhost:8080/river-conditions
```

### Health Check
```bash
curl http://localhost:8080/health
```

### Interactive API Docs
Open [http://localhost:8080/docs](http://localhost:8080/docs) in your browser.

---

## Troubleshooting

- **No Data Returned**: Ensure the LCRA website and APIs are accessible from your network. The `/health` endpoint will indicate if the upstream API is reachable.
- **Dependency Issues**: Make sure you have run `uv sync` and are using the correct Python version.
- **Port Conflicts**: If port 8080 is in use, specify another port with `--port <number>`.
- **Pydantic Deprecation Warnings**: The code is compatible with Pydantic v2+; warnings are cosmetic but can be silenced by updating usage to `model_dump()`.

---

## Project Structure

```
lcra/
  main.py             # CLI entrypoint for API server and data extraction
  api/
    __init__.py         # FastAPI app and route definitions
  lcra/
    __init__.py       # Data models
  scraper/
    __init__.py       # LCRA data scraper logic
  pyproject.toml      # Project dependencies
  uv.lock             # uv dependency lock file
  README.md           # This file
```

---

## Credits

- [LCRA Hydromet](https://hydromet.lcra.org/) for public data
- [FastAPI](https://fastapi.tiangolo.com/)
- [httpx](https://www.python-httpx.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [uv](https://github.com/astral-sh/uv)

---

## License

This project is for educational and non-commercial use. Data is provided by LCRA and subject to their terms of use.
