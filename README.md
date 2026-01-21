# MLflow AI Gateway on Databricks Apps

Deploy MLflow AI Gateway as a Databricks App to provide a unified API interface for 100+ LLM providers, accessible from anywhere including within your Databricks workspace.

## Features

- **100+ Providers**: OpenAI, Anthropic, Google Gemini, AWS Bedrock, Azure OpenAI, Cohere, Mistral, Databricks, and many more via LiteLLM
- **Web UI**: Configure API keys and endpoints through an intuitive interface
- **OpenAI-Compatible**: Drop-in replacement with `/gateway/mlflow/v1/chat/completions`
- **Passthrough APIs**: Access provider-native APIs (OpenAI, Anthropic, Gemini)
- **Streaming**: Full support for streaming responses
- **Zero-Downtime Updates**: Add/modify endpoints without restarting

## Quick Start

### 1. Deploy to Databricks Apps

```bash
# Deploy the app
databricks apps create mlflow-ai-gateway
databricks apps deploy mlflow-ai-gateway --source-code-path .
```

### 2. Configure via Web UI

1. Navigate to your app URL: `https://your-app.databricks.com/#/gateway`
2. **Create API Key**:
   - Go to **API Keys** tab
   - Click **Create API Key**
   - Select provider (e.g., Databricks, OpenAI)
   - Enter your credentials
3. **Create Endpoint**:
   - Go to **Endpoints** tab
   - Click **Create Endpoint**
   - Name it (e.g., `my-chat`)
   - Select provider and model
   - Choose your API key
  
### 3. Generate an OAuth Token 

Databricks Apps needs an OAuth Token. Use the Databricks CLI to generate one: 

  ```bash
   databricks auth token --profile <your profile name>
   ```

### 4. Query Your Endpoint

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://your-app.databricks.com/gateway/mlflow/v1",
    api_key="your token from step 3"
)

response = client.chat.completions.create(
    model="my-chat",  # Your endpoint name
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

## API Reference

### Unified APIs (work with any provider)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/gateway/{endpoint}/mlflow/invocations` | MLflow native format |
| POST | `/gateway/mlflow/v1/chat/completions` | OpenAI-compatible chat |
| POST | `/gateway/mlflow/v1/embeddings` | OpenAI-compatible embeddings |

### Passthrough APIs (provider-specific)

| Provider | Base URL | Notes |
|----------|----------|-------|
| OpenAI | `/gateway/openai/v1/...` | Full OpenAI API |
| Anthropic | `/gateway/anthropic/v1/messages` | Messages API |
| Gemini | `/gateway/gemini/v1beta/...` | Google Gemini API |

### Management

| URL | Description |
|-----|-------------|
| `/#/gateway` | Web UI for API keys and endpoints |
| `/docs` | Swagger API documentation |
| `/health` | Health check |

## Usage Examples

### MLflow Invocations API

```python
import requests

response = requests.post(
    "https://your-app.databricks.com/gateway/my-chat/mlflow/invocations",
    json={"messages": [{"role": "user", "content": "Hello!"}]}
)
print(response.json()["choices"][0]["message"]["content"])
```

### OpenAI SDK

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://your-app.databricks.com/gateway/mlflow/v1",
    api_key=""
)

# Chat
response = client.chat.completions.create(
    model="my-chat",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Streaming
for chunk in client.chat.completions.create(
    model="my-chat",
    messages=[{"role": "user", "content": "Hello!"}],
    stream=True
):
    print(chunk.choices[0].delta.content or "", end="")
```

### Anthropic Passthrough

```python
import anthropic

client = anthropic.Anthropic(
    base_url="https://your-app.databricks.com/gateway/anthropic",
    api_key="dummy"
)

response = client.messages.create(
    model="my-anthropic-endpoint",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## Supported Providers

| Provider | Chat | Embeddings | Notes |
|----------|------|------------|-------|
| OpenAI | ✅ | ✅ | GPT-4, GPT-5, etc. |
| Azure OpenAI | ✅ | ✅ | Enterprise OpenAI |
| Anthropic | ✅ | ❌ | Claude models |
| Google Gemini | ✅ | ✅ | Gemini models |
| AWS Bedrock | ✅ | ✅ | Claude, Titan, etc. |
| Databricks | ✅ | ✅ | Foundation Model APIs |
| Cohere | ✅ | ✅ | Command, Embed |
| Mistral | ✅ | ✅ | Mistral AI |
| Together AI | ✅ | ✅ | Open-source models |
| Groq | ✅ | ❌ | Fast inference |
| Ollama | ✅ | ✅ | Local models |

See [LiteLLM Providers](https://docs.litellm.ai/docs/providers) for the full list.

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python app.py

# Or directly with mlflow
mlflow server --port 8000
```

Visit `http://localhost:8000/#/gateway` to configure endpoints.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Databricks Workspace                      │
│  ┌─────────────┐    ┌─────────────────────────────────────┐ │
│  │  Notebooks  │───▶│     MLflow Server + AI Gateway      │ │
│  │   & Jobs    │    │  ┌─────────────────────────────────┐│ │
│  └─────────────┘    │  │ Web UI: /#/gateway              ││ │
│                     │  │ API: /gateway/mlflow/v1/...     ││ │
│                     │  │ Passthrough: /gateway/openai/...││ │
│                     │  └─────────────────────────────────┘│ │
│                     │           │ LiteLLM                  │ │
│                     └───────────┼──────────────────────────┘ │
└─────────────────────────────────┼────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
   ┌─────────┐             ┌────────────┐            ┌───────────┐
   │ OpenAI  │             │ Anthropic  │            │ Databricks│
   │ Azure   │             │  (Claude)  │            │   FMAPI   │
   └─────────┘             └────────────┘            └───────────┘
```

## Files

| File | Description |
|------|-------------|
| `app.py` | Main application - starts MLflow server |
| `app.yaml` | Databricks Apps configuration |
| `requirements.txt` | Python dependencies |
| `examples/` | Usage examples and notebooks |

## Authentication for Programmatic Access

Databricks Apps use **OAuth/OIDC** for authentication. This means:
- **Browser access works** automatically (SSO via Databricks login)
- **Programmatic access requires an OAuth access token**

### Quick Start: Using Databricks CLI (Recommended)

The simplest way to get an access token is using the Databricks CLI:

```bash
# 1. Make sure you're authenticated with Databricks CLI
databricks auth login --host https://your-workspace.cloud.databricks.com

# 2. Generate an access token
databricks auth token
```

This outputs a token you can use with the OpenAI client:

```python
from openai import OpenAI

# Get token from: databricks auth token
ACCESS_TOKEN = "eyJhbGciOiJS..."  # Your token from CLI

client = OpenAI(
    base_url="https://mlflow-ai-gateway-xxx.databricksapps.com/gateway/mlflow/v1",
    api_key=ACCESS_TOKEN  # Pass the OAuth token as api_key
)

response = client.chat.completions.create(
    model="databricks-claude",  # Your endpoint name
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

### Option 2: Service Principal OAuth (For Automation)

For automated pipelines and CI/CD, use a Service Principal:

1. **Create a Service Principal**:
   ```bash
   databricks service-principals create --display-name "mlflow-gateway-client"
   ```

2. **Grant App Permission**:
   ```bash
   databricks apps set-permissions mlflow-ai-gateway --json '{
     "access_control_list": [{
       "service_principal_name": "<sp-application-id>",
       "permission_level": "CAN_USE"
     }]
   }'
   ```

3. **Create OAuth Secret** (via Admin Console > Service Principals > Secrets)

4. **Use OAuth Token**:
   ```python
   from examples.gateway_client import GatewayClient

   client = GatewayClient(
       gateway_url="https://mlflow-ai-gateway-xxx.databricksapps.com",
       databricks_host="https://your-workspace.cloud.databricks.com",
       client_id="<service-principal-client-id>",
       client_secret="<service-principal-secret>"
   )

   response = client.chat("my-endpoint", "Hello!")
   ```

See `examples/setup_service_principal.py` for detailed setup instructions.

### Option 3: From Databricks Notebooks

When running from a Databricks notebook, use the SDK to get a token automatically:

```python
from databricks.sdk import WorkspaceClient
from openai import OpenAI

# Get token from notebook context
w = WorkspaceClient()
token = w.config.token

client = OpenAI(
    base_url="https://mlflow-ai-gateway-xxx.databricksapps.com/gateway/mlflow/v1",
    api_key=token
)

response = client.chat.completions.create(
    model="databricks-claude",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## Troubleshooting

### "401 Unauthorized" when calling API
- Databricks Apps require OAuth, not PAT tokens
- Set up a Service Principal (see Authentication section above)
- Or use the cluster deployment alternative

### "Endpoint not found"
- Ensure you've created the endpoint via the web UI at `/#/gateway`
- Check the endpoint name matches exactly (case-sensitive)

### "API key error"
- Create an API key via the web UI first
- Ensure the API key is associated with your endpoint

### View logs
```bash
databricks apps get-logs mlflow-ai-gateway
```

## License

Apache 2.0
