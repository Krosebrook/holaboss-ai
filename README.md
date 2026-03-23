# Hola Boss OSS

This repo now contains both the local desktop app and the runtime it embeds.

## What This Repo Is

- `desktop/`: Electron desktop workspace app
- `runtime/`: packaged Python runtime, tests, and bundle tooling
- `.github/workflows/`: release and publishing workflows

This repository is public OSS. It supports local development and local runtime packaging without requiring login.

Backend-connected Holaboss product behavior is separate from the baseline local OSS workflow.

## What Works Without Login

- local desktop development
- local runtime packaging
- local workspace/runtime flows
- local typechecking and runtime tests

## What May Require Holaboss Backend Access

- hosted sign-in flows
- auth-backed product features
- backend-connected Holaboss services

## Prerequisites

- Node.js 22+
- npm
- Python 3.12
- `uv`

## Quick Start

Install desktop dependencies:

```bash
npm run desktop:install
```

Build and stage a local runtime bundle from this repo into `desktop/out/runtime-macos`:

```bash
npm run desktop:prepare-runtime:local
```

Run the desktop app in development:

```bash
npm run desktop:dev
```

This starts:

- the Vite renderer dev server
- the Electron main/preload watcher
- the Electron app itself

## Common Commands

Run the desktop typecheck:

```bash
npm run desktop:typecheck
```

Run runtime tests:

```bash
npm run runtime:test
```

Build a local macOS desktop bundle with the locally built runtime embedded:

```bash
npm run desktop:dist:mac:local
```

Stage the latest released runtime bundle for your current host platform:

```bash
npm run desktop:prepare-runtime
```

## Development Notes

The root `package.json` is just a thin command wrapper for the desktop app. The actual desktop project still lives in `desktop/package.json`.

`runtime/` remains independently buildable and testable. The desktop app consumes its packaged output rather than importing Python source files directly.

For local desktop work, the default flow is:

```bash
npm run desktop:install
npm run desktop:prepare-runtime:local
npm run desktop:dev
```

For runtime-only work, the main command is:

```bash
npm run runtime:test
```
