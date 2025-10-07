# SearxNG MCP Server

A Model Context Protocol (MCP) server that provides search capabilities through [SearxNG](https://docs.searxng.org/), the privacy-respecting metasearch engine.

## Usage

### Using uvx

You can also just pip install this but we recommend using `uv`.

```bash
# With command line argument
uvx searxng-mcp-server --searxng-url https://searx.be

# With environment variable
SEARXNG_URL=https://searx.be uvx searxng-mcp-server
```

**Package link**: [https://pypi.org/project/searxng-mcp-server/](https://pypi.org/project/searxng-mcp-server/)

### Using Docker/Podman

```bash
# With command line argument
podman run --rm -i docker.io/icewreck/searxng-mcp-server:latest --searxng-url https://searx.be

# With environment variable
podman run --rm -i -e SEARXNG_URL=https://searx.be docker.io/icewreck/searxng-mcp-server:latest
```

## Available Tools

- **`search_web`**: General web search with language and time filtering
- **`search_images`**: Image search across multiple search engines
- **`search_videos`**: Video search from various platforms
- **`search_news`**: News search with time range filtering

## Configuration

The server requires a SearxNG instance URL. You can provide it via:

- **Environment Variable**: `SEARXNG_URL=https://your-searxng-instance.com`
- **Command Line Argument**: `--searxng-url https://your-searxng-instance.com`

Optional: `SEARXNG_TIMEOUT` (default: 30), `SEARXNG_USER_AGENT`, `LOG_LEVEL`
