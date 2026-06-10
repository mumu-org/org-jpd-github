# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is a **demonstration repository** for integrating the JFrog Platform (JPD) with GitHub, Jenkins, and CI/CD security tooling. The application code (a Maven Spring Boot WAR, an npm package) exists only as a vehicle to exercise JFrog features — the value is in the **CI workflows, JFrog CLI invocations, and Evidence/AppTrust/security configuration**, not the apps themselves. Documentation (README files) is written in Chinese; commit messages mix Chinese and English.

The JFrog features being demonstrated: **Evidence** (SLSA build provenance attestations), **AppTrust** (application versioning), **Frogbot** (PR/repo security scanning), **Xray** (build scanning), **Curation** (dependency policy), and **transitive dependency / contextual analysis**.

## Repository layout

- `app-maven/` — Spring Boot WAR (`com.example.github.jfrog.maven:app-maven`), packaged into a Docker image. Deliberately pins vulnerable deps (`fastjson 1.2.21`, `log4j-core 2.9.1`) to produce scan findings.
- `app-npm/` — npm package, also Dockerized. Deliberately pins vulnerable/malicious-looking deps (`crossenv`, old `lodash`/`ejs`) for Curation/Xray demos.
- `transitive-demo/` — multi-module Maven chain (`app-maven → internal-package → internal-utils → xstream:1.4.15` CVE) demonstrating transitive dependency analysis. Has its own pom modules.
- `.github/workflows/` — the three CI pipelines (see below).
- `ops/` — Kubernetes deployment manifests (`deployment.yaml`, `service.yaml`) and an ops Dockerfile.
- `Jenkinsfile-evidence`, `Jenkinsfile-MR` — Jenkins equivalents of the Evidence flow. **Note:** `Jenkinsfile-evidence` is explicitly marked incomplete (copied from an npm project, not yet adapted).

## CI workflows (`.github/workflows/`)

- **`jfrog-evidence.yml`** — Build, Push, and Attest. Builds the Maven WAR, publishes a build, pushes a Docker image, and attaches SLSA build-provenance Evidence to the WAR, the build, and the Docker image (via `actions/attest-build-provenance`). Triggers on push to `main`. The Sonar Evidence step is commented out (requires Sonar Enterprise).
- **`jfrog-jf-scan.yml`** — Builds/publishes the npm package, runs `jf curation-audit`, and runs `jf bs` (Xray build scan). Triggers on PR (`pull_request_target`), push to `main`, and dispatch.
- **`frogbotV3.yml`** — Downloads the Frogbot v3 binary and runs `scan-pull-request` (on PRs) or `scan-repository` (on push to `jfrog-evidence`).

## Critical: multi-environment switching

This repo is run against **three different JFrog platforms**, and the active one is selected by **commenting/uncommenting blocks** throughout the codebase. When editing, keep all three variants present (commented) and only flip which is active. The three environments:

| Environment | URL / domain | How referenced |
|---|---|---|
| **Demo JPD** (currently active) | `demo.jfrogchina.com` | `vars.JF_CHINA_URL`, `vars.JPD_CHINA_DOMAIN`, `secrets.JF_CHINA_*` |
| **Soleng JPD** | `soleng.jfrog.io` | `vars.JF_URL`, OIDC `slash-l/jpd-github@github` |
| **Local k8s** | `jfrog.local:32012` / `slash.jfrog.local:30012` | hardcoded in pom/Dockerfile |

This switching appears in: workflow `env:` blocks and auth steps, `app-maven/pom.xml` `<distributionManagement>`, both `Dockerfile`s (`FROM` lines), and `.jfrog/projects/*.yaml` `serverId`. Authentication also varies — Demo JPD uses username/password secrets, Soleng uses OIDC token output.

### Server IDs
- `.jfrog/projects/*.yaml` (per-app resolver/deployer config) reference `serverId: demo-jfrogchina`.
- Workflows set up the CLI via `jfrog/setup-jfrog-cli@v4` which creates server `setup-jfrog-cli-server`, then `jf c use setup-jfrog-cli-server`. The `jf mvnc`/`jf npmc` config commands explicitly pass `--server-id-resolve`/`--server-id-deploy=setup-jfrog-cli-server`.

### JFrog repositories
- Maven: resolve/deploy via `slash-maven-virtual`; the evidence workflow searches `slash-maven-dev-local`.
- npm: `slash-npm-virtual`.
- Docker: `slash-docker-dev-local`.

## Common commands

Maven app (from `app-maven/`):
```bash
mvn install                              # build the WAR
mvn verify org.sonarsource.scanner.maven:sonar-maven-plugin:sonar \
  -Dsonar.projectKey=slash-l_jpd-github # Sonar scan (needs SONAR_TOKEN env)
```
The CI uses a versioned build via `-Drevision=...` against `${revision}` — note `pom.xml` currently hardcodes `<version>2.0.0</version>`; to demo Evidence you must switch it to `<version>${revision}</version>` (the alternative is commented in the pom).

npm app (from `app-npm/`):
```bash
npm install
npm install -g @sonar/scan && sonar \
  -Dsonar.token=<token> -Dsonar.projectKey=slash-l_jpd-github -Dsonar.organization=slash-l
```
There is **no real test suite** — `app-npm`'s `test` script intentionally exits 1.

JFrog CLI patterns used throughout (build → publish → scan → attest evidence):
```bash
jf mvnc / jf npmc           # configure resolve/deploy repos + server IDs
jf mvn install / jf npm install --build-name=<name> --build-number=<n>
jf rt bce <name> <n> && jf rt bp <name> <n>   # collect env + publish build
jf bs <name> <n>            # Xray build scan
jf curation-audit           # Curation policy audit
jf evd create ...           # attach Evidence (predicate + signing key + alias)
jf apptrust version-create  # create an AppTrust application version
```

## MCP server management (from `.github/copilot-instructions.md`)

All MCP servers MUST be installed **only** through the JFrog MCP Gateway (`@jfrog/mcp-gateway` from registry `https://releases.jfrog.io/artifactory/api/npm/coding-agents-npm/`) — never via direct `npx`/`pip`/`docker`. Config lives in `.vscode/mcp.json` (and `.cursor/mcp.json`). Each entry uses `command: npx` with args `@jfrog/mcp-gateway --registry <url> --server <SERVER_ID>` and `env._JF_MCP_LOADER_ARGS = "project=<NAME>&mcp=<PACKAGE_NAME>"`.

To resolve project/server: reuse `_JF_MCP_LOADER_ARGS` from existing entries → else `JF_PROJECT` env → else read `~/.jfrog/jfrog-cli.conf.v6` via a **terminal command** (never glob/file-search — it skips hidden dirs). Look up package names via `python3 .github/scripts/lookup-mcp-catalog.py "<SERVER_ID>" "<PROJECT>" "<MCP_SEARCH>"` (a single Bash call; `__list_all__` lists the whole catalog). Never guess package names; they must come from the catalog. The actual JFrog MCP tools in this session are exposed under `jf_gateway_*`.
