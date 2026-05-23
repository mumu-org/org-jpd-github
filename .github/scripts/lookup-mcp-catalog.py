#!/usr/bin/env python3
"""Look up an MCP in the JFrog AI Catalog.

Usage:
    lookup-mcp-catalog.py <SERVER_ID> <PROJECT> <MCP>

Output (always a single line written to stdout):
    FOUND|<packageName>|<input1=description>,<input2=description>
    NOT_FOUND|<comma-separated available names>
    ERROR|<message>
"""

import json
import os
import ssl
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Optional

JFROG_CLI_CONFIG_PATH = Path.home() / ".jfrog" / "jfrog-cli.conf.v6"

MCP_REGISTRY_API_PATH = "/ml/core/api/v1/mcp-registry/allowed-registered-servers"
MCP_REGISTRY_PAGE_SIZE = 500
HTTP_TIMEOUT_SECONDS = 10

OUTPUT_FIELD_SEPARATOR = "|"

# JFrog exposes both legacy (JFROG_*) and CLI-native (JF_*) env var names
# for the same values, so we accept either form.
TOKEN_ENV_VARS = ("JFROG_ACCESS_TOKEN", "JF_ACCESS_TOKEN")
URL_ENV_VARS = ("JFROG_URL", "JF_URL")


class LookupError(Exception):
    """Raised when the lookup cannot proceed; the message is shown to the user."""


def parse_args(argv: list[str]) -> tuple[str, str, str]:
    if len(argv) != 4:
        raise LookupError("Usage: lookup-mcp-catalog.py <SERVER_ID> <PROJECT> <MCP>")
    return argv[1], argv[2], argv[3]


def load_credentials_from_cli_config(server_id: str) -> tuple[str, str]:
    """Try to load (token, url) from the JFrog CLI config for `server_id`."""
    try:
        with open(JFROG_CLI_CONFIG_PATH) as fh:
            config = json.load(fh)
    except (FileNotFoundError, PermissionError, json.JSONDecodeError):
        return "", ""

    server = next(
        (s for s in config.get("servers", []) if s.get("serverId") == server_id),
        None,
    )
    if not server:
        return "", ""
    return server.get("accessToken", ""), server.get("url", "")


def load_credentials_from_env() -> tuple[str, str]:
    """Try to load (token, url) from environment variables."""
    token = next(
        (os.environ.get(name, "") for name in TOKEN_ENV_VARS if os.environ.get(name)),
        "",
    )
    url = next(
        (os.environ.get(name, "") for name in URL_ENV_VARS if os.environ.get(name)),
        "",
    )
    return token, url


def resolve_credentials(server_id: str) -> tuple[str, str]:
    """Resolve (token, url) from CLI config first, then env vars."""
    token, url = load_credentials_from_cli_config(server_id)
    if not token or not url:
        env_token, env_url = load_credentials_from_env()
        token = token or env_token
        url = url or env_url
    if not token or not url:
        raise LookupError(
            "No credentials found. Set JFROG_ACCESS_TOKEN and JFROG_URL env "
            f"vars, or run: jf c add {server_id}"
        )
    return token, url


def _base_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise LookupError(f"Invalid JFrog URL: {url!r}")
    return f"{parsed.scheme}://{parsed.netloc}"


def fetch_catalog(url: str, token: str, project: str) -> dict[str, Any]:
    """Call the MCP registry API and return the parsed JSON response."""
    base_url = _base_url(url)
    safe_project = urllib.parse.quote(project, safe="")
    api_url = (
        f"{base_url}{MCP_REGISTRY_API_PATH}/{safe_project}"
        f"?pageSize={MCP_REGISTRY_PAGE_SIZE}"
    )
    request = urllib.request.Request(
        api_url, headers={"Authorization": f"Bearer {token}"}
    )
    try:
        with urllib.request.urlopen(
            request,
            timeout=HTTP_TIMEOUT_SECONDS,
            context=ssl.create_default_context(),
        ) as response:
            return json.loads(response.read())
    except Exception as exc:
        raise LookupError(f"Catalog API failed: {exc}") from exc


def find_matching_mcp(
    catalog: dict[str, Any], mcp: str
) -> tuple[Optional[dict[str, Any]], list[str]]:
    """Return (matching MCP spec, list of all names) for the given mcp query."""
    mcp_query = mcp.lower()
    all_names: list[str] = []
    matching_mcp: Optional[dict[str, Any]] = None

    for entry in catalog.get("registeredServers", []):
        spec = entry.get("mcpServer", {}).get("spec", {})
        package_name = spec.get("packageName", "")
        display_name = spec.get("displayName", "")
        all_names.append(package_name or display_name)

        if not mcp_query:
            continue

        mcp_matches_entry = (
            mcp_query in package_name.lower() or mcp_query in display_name.lower()
        )
        if mcp_matches_entry:
            matching_mcp = spec
            break

    return matching_mcp, all_names


def collect_required_inputs(spec: dict[str, Any]) -> list[str]:
    """Collect required env vars and remote headers from the MCP spec."""
    server_type = spec.get("mcpServerType", {})
    inputs: list[str] = []
    inputs.extend(_collect_local_env_vars(server_type))
    inputs.extend(_collect_remote_headers(server_type))
    return inputs


def _collect_local_env_vars(server_type: dict[str, Any]) -> list[str]:
    env_vars = (
        server_type.get("local", {})
        .get("bootParams", {})
        .get("environmentVariables", [])
    )
    collected: list[str] = []
    for env_var in env_vars:
        if not env_var.get("isRequired"):
            continue
        tag = "[secret]" if env_var.get("isSecret") else ""
        collected.append(f"{env_var['name']}={tag}{env_var.get('description', '')}")
    return collected


def _collect_remote_headers(server_type: dict[str, Any]) -> list[str]:
    collected: list[str] = []
    for endpoint in server_type.get("remote", {}).get("endpoints", []):
        for header in endpoint.get("headers", []):
            mcp_input = header.get("mcpInput", {})
            input_details = mcp_input.get("mcpInputDetails", {})
            name = input_details.get("name")
            if not name or mcp_input.get("defaultValue"):
                continue
            tags = ["header"]
            if input_details.get("isRequired"):
                tags.append("required")
            if input_details.get("isSecret"):
                tags.append("secret")
            label = f"[{','.join(tags)}] {input_details.get('description', '')}"
            collected.append(f"{name}={label}")
    return collected


def _strip_separator(value: str) -> str:
    """Remove the output field separator from a value so it can't break parsing."""
    return value.replace(OUTPUT_FIELD_SEPARATOR, "-")


def format_found(spec: dict[str, Any]) -> str:
    package_name = _strip_separator(
        spec.get("packageName", "") or spec.get("displayName", "")
    )
    inputs = [_strip_separator(i) for i in collect_required_inputs(spec)]
    return (
        f"FOUND{OUTPUT_FIELD_SEPARATOR}{package_name}"
        f"{OUTPUT_FIELD_SEPARATOR}{','.join(inputs)}"
    )


def format_not_found(all_names: list[str]) -> str:
    safe_names = [_strip_separator(n) for n in all_names]
    return f"NOT_FOUND{OUTPUT_FIELD_SEPARATOR}{','.join(safe_names)}"


def format_error(message: str) -> str:
    return f"ERROR{OUTPUT_FIELD_SEPARATOR}{_strip_separator(message)}"


def main(argv: list[str]) -> str:
    try:
        server_id, project, mcp = parse_args(argv)
        token, url = resolve_credentials(server_id)
        catalog = fetch_catalog(url, token, project)
    except LookupError as exc:
        return format_error(str(exc))

    matching_mcp, all_names = find_matching_mcp(catalog, mcp)
    if matching_mcp is not None:
        return format_found(matching_mcp)
    return format_not_found(all_names)


if __name__ == "__main__":
    print(main(sys.argv))
