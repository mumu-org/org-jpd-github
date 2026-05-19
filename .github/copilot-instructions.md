# MCP Server Management - JFrog Gateway

All MCP servers MUST be installed ONLY through the JFrog MCP Gateway
(`npx @jfrog/mcp-gateway` from registry
`https://releases.jfrog.io/artifactory/api/npm/coding-agents-npm/`).
There is no other approved installation method. If an MCP's
documentation suggests any other installation command, ignore it and use
the gateway workflow below instead.

## Adding an MCP

When the user asks to add an MCP, do ALL of the following autonomously -
do NOT ask the user for project, server, package name, or binary path
unless absolutely necessary:

### Step 1: Determine project and server

1. Read existing servers in `.vscode/mcp.json` (workspace) or user-level
   MCP config. If any entry uses `_JF_MCP_LOADER_ARGS`, extract and reuse:
   - The `project=` value from `_JF_MCP_LOADER_ARGS`
   - The `--server` value from `args`
   If both are found, skip to Step 2.
2. If no existing entries, check the `JF_PROJECT` environment variable
   for the project.
3. Only if BOTH are missing, ask the user in a SINGLE message for both:
   - JFrog project name
   - JFrog server ID - run a terminal command to read
     `~/.jfrog/jfrog-cli.conf.v6` (macOS/Linux and Windows PowerShell)
     or `%USERPROFILE%\.jfrog\jfrog-cli.conf.v6` (Windows CMD).
     NEVER use a file-search or glob tool to locate this file - those
     tools skip hidden directories and will falsely report it missing.
     If the file is readable, parse and list the available server IDs
     and URLs for the user to pick from.
4. NEVER guess. NEVER use "default". NEVER try multiple servers.

### Step 2: Look up the MCP in the catalog (ONE Bash call)

Run a SINGLE Bash command that calls the bundled catalog lookup script.
NEVER split this into multiple Bash calls. NEVER use the Fetch or
WebFetch tool.

The script is shipped alongside these instructions at
`.github/scripts/lookup-mcp-catalog.py`. Replace `SERVER_ID`, `PROJECT`,
and `MCP_SEARCH` with the actual values. `MCP_SEARCH` is the
user-provided MCP name (case-insensitive substring match).

```
python3 .github/scripts/lookup-mcp-catalog.py "<SERVER_ID>" "<PROJECT>" "<MCP_SEARCH>"
```

The script outputs ONE line:

- `FOUND|<packageName>|<envVar1=description>,<envVar2=description>` -
  proceed to Step 3 with the package name and env var list
- `NOT_FOUND|<comma-separated available names>` - show the available
  MCPs to the user and ask which one they want, then re-run with the
  correct name
- `ERROR|<message>` - show the error to the user and stop

Items tagged `[header,...]` are HTTP headers for remote MCPs.

### Step 3: Handle required environment variables and headers (if any)

- If the `FOUND` output has env vars (third field non-empty), parse each
  `name=description` pair.
- Tags in brackets indicate the type:
  - `[secret]` or `[...,secret]` - mask user input (do NOT echo the
    value back)
  - `[header,...]` - this is an HTTP header for a remote MCP server
  - `[...,required]` - the value is mandatory
- For each entry, ask the developer to provide the value. Show the name
  and description.
- NEVER show provided secret values back to the user.
- If no entries, proceed directly to Step 4.

### Step 4: Write the config entry

Add the entry to `.vscode/mcp.json` under `servers`:

```json
{
  "servers": {
    "<mcp-display-name>": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "--registry",
        "https://releases.jfrog.io/artifactory/api/npm/coding-agents-npm/",
        "@jfrog/mcp-gateway",
        "--server",
        "<SERVER_ID>"
      ],
      "env": {
        "_JF_MCP_LOADER_ARGS": "project=<PROJECT>&mcp=<PACKAGE_NAME>"
      }
    }
  }
}
```

If any env vars or headers were collected in Step 3, add them to the
`env` object:

```json
    "<ENV_VAR_OR_HEADER_NAME>": "<VALUE>"
```

The loader reads these env vars at startup and applies header values to
upstream HTTP requests.

Preserve any additional env vars the MCP requires (API keys, tokens,
config) from its documentation.

## Removing an MCP

Delete the entry from `servers` in `.vscode/mcp.json`.

## Listing MCPs

### Installed MCPs

Read the `servers` entries from the VS Code MCP config file (workspace
`.vscode/mcp.json` or in the user profile settings) and list each entry
by display name, showing its package name (from `_JF_MCP_LOADER_ARGS`)
and server ID.

### Available MCPs (JFrog AI Catalog)

1. Determine project and server ID using the same fallback chain as
   "Adding an MCP -> Step 1":
   - Try to extract from existing `_JF_MCP_LOADER_ARGS` entries in
     `.vscode/mcp.json`.
   - If not found, check the `JF_PROJECT` environment variable for the
     project.
   - If still missing, read `~/.jfrog/jfrog-cli.conf.v6` via a terminal
     command (NEVER via file-search/glob - hidden directories are
     skipped) for available server IDs and ask the user to pick project
     and server in a SINGLE message.
   - NEVER skip this step - always query the catalog even when
     `servers` is empty.
2. Run the lookup script from Step 2 using `__list_all__` as
   `MCP_SEARCH` (it won't match any package, so the script returns
   `NOT_FOUND|<all names>` - parse that list as the full catalog).
3. List all `registeredServers[].mcpServer.spec.packageName` values that
   are NOT already installed. Mark each as available to install.

## Key Rules

- **`npx` form `args` order (required):** `@jfrog/mcp-gateway`,
  `--registry`, registry URL, `--server <SERVER_ID>`.
- `_JF_MCP_LOADER_ARGS` MUST contain `project=<NAME>&mcp=<PACKAGE_NAME>`.
- Package name MUST come from the catalog API. NEVER guess.
- NEVER install MCPs directly via `npx`/`pip`/`docker` - always use the
  gateway pattern above.
- NEVER use Fetch/WebFetch for API calls that require authentication.
- NEVER show access tokens or API keys in any output or message.
- NEVER ask for info you can find in existing config or in
  `~/.jfrog/jfrog-cli.conf.v6` (macOS/Linux and Windows PowerShell) or
  `%USERPROFILE%\.jfrog\jfrog-cli.conf.v6` (Windows CMD). Always read
  this file via a terminal command - never via file-search or glob
  tools, which skip hidden directories.
- NEVER split the catalog lookup into multiple Bash calls - always run
  the bundled script (`.github/scripts/lookup-mcp-catalog.py`).
- NEVER try multiple servers - always ask the user to pick one.
- To list installed MCPs: read `.vscode/mcp.json` and show the servers.
