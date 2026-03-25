# ruff: noqa: S101

from __future__ import annotations

import base64
import json

from sandbox_agent_runtime import workspace_mcp_sidecar
from sandbox_agent_runtime.runtime_config.errors import WorkspaceRuntimeConfigError


def test_request_from_args_decodes_request_base64() -> None:
    encoded = base64.b64encode(
        json.dumps(
            {
                "workspace_dir": "/tmp/workspace-1",
                "catalog_json_base64": "e30=",
                "host": "127.0.0.1",
                "port": 8080,
                "server_name": "workspace__abc123",
            }
        ).encode("utf-8")
    ).decode("utf-8")

    args = workspace_mcp_sidecar._decode_request(workspace_mcp_sidecar._parse_args(["--request-base64", encoded]))

    assert args.workspace_dir == "/tmp/workspace-1"
    assert args.catalog_json_base64 == "e30="
    assert args.host == "127.0.0.1"
    assert args.port == 8080
    assert args.server_name == "workspace__abc123"


def test_request_from_args_rejects_invalid_request_base64() -> None:
    try:
        workspace_mcp_sidecar._decode_request(workspace_mcp_sidecar._parse_args(["--request-base64", "not-base64"]))
    except WorkspaceRuntimeConfigError as exc:
        assert exc.path == "request_base64"
    else:
        raise AssertionError("expected WorkspaceRuntimeConfigError")
