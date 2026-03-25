from __future__ import annotations

import argparse
import base64
import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from sandbox_agent_runtime.runtime_config.errors import WorkspaceRuntimeConfigError
from sandbox_agent_runtime.runtime_config.models import WorkspaceMcpCatalogEntry
from sandbox_agent_runtime.workspace_tool_loader import load_workspace_tools

logging.basicConfig(level=os.getenv("SANDBOX_AGENT_LOG_LEVEL", "INFO"))
logger = logging.getLogger("workspace_mcp_sidecar")


@dataclass(frozen=True)
class WorkspaceMcpSidecarRequest:
    workspace_dir: str
    catalog_json_base64: str
    host: str
    port: int
    server_name: str


def _parse_args(argv: list[str]) -> str:
    parser = argparse.ArgumentParser(description="Workspace MCP sidecar for runtime-local workspace tools")
    parser.add_argument("--request-base64", required=True, help="Base64-encoded JSON request payload")
    parsed = parser.parse_args(argv)
    return str(parsed.request_base64)


def _decode_request_base64(encoded: str) -> dict[str, object]:
    try:
        raw = base64.b64decode(encoded.encode("utf-8"), validate=True).decode("utf-8")
        payload = json.loads(raw)
    except Exception as exc:
        raise WorkspaceRuntimeConfigError(
            code="workspace_mcp_sidecar_start_failed",
            path="request_base64",
            message=f"invalid sidecar request payload: {exc}",
        ) from exc
    if not isinstance(payload, dict):
        raise WorkspaceRuntimeConfigError(
            code="workspace_mcp_sidecar_start_failed",
            path="request_base64",
            message="request payload must decode to an object",
        )
    return payload


def _request_string(payload: dict[str, object], *, key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise WorkspaceRuntimeConfigError(
            code="workspace_mcp_sidecar_start_failed",
            path=key,
            message=f"{key} is required",
        )
    return value


def _request_port(payload: dict[str, object]) -> int:
    value = payload.get("port")
    if isinstance(value, bool):
        value = None
    if not isinstance(value, int) or value <= 0:
        raise WorkspaceRuntimeConfigError(
            code="workspace_mcp_sidecar_start_failed",
            path="port",
            message="port must be a positive integer",
        )
    return value


def _decode_request(encoded: str) -> WorkspaceMcpSidecarRequest:
    payload = _decode_request_base64(encoded)
    return WorkspaceMcpSidecarRequest(
        workspace_dir=_request_string(payload, key="workspace_dir"),
        catalog_json_base64=_request_string(payload, key="catalog_json_base64"),
        host=str(payload.get("host", "127.0.0.1") or "127.0.0.1"),
        port=_request_port(payload),
        server_name=str(payload.get("server_name", "workspace") or "workspace"),
    )


def _decode_catalog(encoded: str) -> tuple[WorkspaceMcpCatalogEntry, ...]:
    try:
        raw = base64.b64decode(encoded.encode("utf-8"), validate=True).decode("utf-8")
        payload = json.loads(raw)
    except Exception as exc:
        raise WorkspaceRuntimeConfigError(
            code="workspace_mcp_sidecar_start_failed",
            path="catalog_json_base64",
            message=f"invalid sidecar catalog payload: {exc}",
        ) from exc
    if not isinstance(payload, list):
        raise WorkspaceRuntimeConfigError(
            code="workspace_mcp_sidecar_start_failed",
            path="catalog_json_base64",
            message="catalog payload must decode to a list",
        )

    entries: list[WorkspaceMcpCatalogEntry] = []
    for item in payload:
        if not isinstance(item, dict):
            raise WorkspaceRuntimeConfigError(
                code="workspace_mcp_sidecar_start_failed",
                path="catalog_json_base64",
                message="catalog entries must be objects",
            )
        entries.append(
            WorkspaceMcpCatalogEntry(
                tool_id=str(item.get("tool_id", "")),
                tool_name=str(item.get("tool_name", "")),
                module_path=str(item.get("module_path", "")),
                symbol_name=str(item.get("symbol_name", "")),
            )
        )
    return tuple(entries)


def _workspace_path(value: str) -> Path:
    path = Path(value).resolve()
    if not path.is_dir():
        raise WorkspaceRuntimeConfigError(
            code="workspace_mcp_sidecar_start_failed",
            path="workspace_dir",
            message=f"workspace directory does not exist: {path}",
        )
    return path


def main(argv: list[str] | None = None) -> int:
    request = _decode_request(_parse_args(argv or sys.argv[1:]))

    try:
        workspace_dir = _workspace_path(request.workspace_dir)
        catalog = _decode_catalog(request.catalog_json_base64)
        loaded_tools = load_workspace_tools(workspace_dir=workspace_dir, catalog=catalog)

        mcp = FastMCP(
            request.server_name,
            host=request.host,
            port=request.port,
            json_response=True,
            stateless_http=True,
        )
        for tool in loaded_tools:
            mcp.tool(name=tool.tool_name)(tool.callable_obj)

        logger.info(
            "Starting workspace MCP sidecar at %s:%s with %s tools",
            request.host,
            request.port,
            len(loaded_tools),
            extra={
                "event": "workspace_mcp.sidecar.start",
                "outcome": "success",
                "workspace_catalog_tool_count": len(loaded_tools),
            },
        )
        mcp.run(transport="streamable-http")
    except WorkspaceRuntimeConfigError:
        logger.exception("Workspace MCP sidecar configuration failure")
        return 2
    except Exception:
        logger.exception("Workspace MCP sidecar failed")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
