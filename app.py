"""
MLflow AI Gateway - Databricks Apps Deployment (MLflow 3.9+)

This app runs the full MLflow Tracking Server with the integrated AI Gateway.
The AI Gateway is built into MLflow server and uses:
- SQL backend for storing API keys and endpoint configurations
- Web UI for managing endpoints at /gateway
- LiteLLM integration for 100+ model providers

API Endpoints:
- GET  /health                                    - Health check
- GET  /#/gateway                                 - Web UI for managing gateway
- POST /gateway/{endpoint}/mlflow/invocations     - Query endpoint (MLflow format)
- POST /gateway/mlflow/v1/chat/completions        - OpenAI-compatible chat
- POST /gateway/openai/v1/chat/completions        - OpenAI passthrough
- POST /gateway/anthropic/v1/messages             - Anthropic passthrough

Prerequisites:
- Configure API keys via the web UI at /#/gateway
- Create endpoints via the web UI
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Start the MLflow server with AI Gateway."""

    # Configuration
    host = os.environ.get("HOST", "0.0.0.0")
    port = os.environ.get("PORT", "8000")

    # Database backend - SQLite for simplicity, can use PostgreSQL in production
    db_path = Path(__file__).parent / "mlflow.db"
    backend_store_uri = os.environ.get(
        "MLFLOW_BACKEND_STORE_URI",
        f"sqlite:///{db_path}"
    )

    # Artifact storage
    artifacts_dir = Path(__file__).parent / "mlartifacts"
    artifacts_dir.mkdir(exist_ok=True)
    default_artifact_root = os.environ.get(
        "MLFLOW_DEFAULT_ARTIFACT_ROOT",
        str(artifacts_dir)
    )

    logger.info(f"Starting MLflow Server with AI Gateway")
    logger.info(f"Host: {host}:{port}")
    logger.info(f"Backend Store: {backend_store_uri}")
    logger.info(f"Artifact Root: {default_artifact_root}")
    logger.info(f"")
    logger.info(f"Gateway UI: http://{host}:{port}/#/gateway")
    logger.info(f"Swagger UI: http://{host}:{port}/docs")

    # Build the mlflow server command
    cmd = [
        sys.executable, "-m", "mlflow", "server",
        "--host", host,
        "--port", port,
        "--backend-store-uri", backend_store_uri,
        "--default-artifact-root", default_artifact_root,
        "--serve-artifacts",
    ]

    # Add workers if specified
    workers = os.environ.get("MLFLOW_WORKERS")
    if workers:
        cmd.extend(["--workers", workers])

    logger.info(f"Command: {' '.join(cmd)}")

    # Execute mlflow server
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"MLflow server failed with exit code {e.returncode}")
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        sys.exit(0)


if __name__ == "__main__":
    main()
