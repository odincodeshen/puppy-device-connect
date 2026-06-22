#!/usr/bin/env python3
"""Read-only Device Connect bridge for a Hiwonder PuppyPi ROS2 container."""

from __future__ import annotations

import asyncio
import os
import socket
import subprocess
from typing import Any

from device_connect_edge import DeviceRuntime
from device_connect_edge.drivers import DeviceDriver, emit, rpc
from device_connect_edge.types import DeviceStatus


CONTAINER = os.getenv("PUPPYPI_CONTAINER", "puppypi-ros2")
ROS_SETUP = os.getenv("ROS_SETUP", "/opt/ros/humble/setup.bash")
PUPPYPI_SETUP = os.getenv(
    "PUPPYPI_SETUP",
    "/workspace/PuppyPi/src/install/setup.bash",
)


def _run(args: list[str], timeout: float = 10.0) -> dict[str, Any]:
    proc = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def _run_ros(command: str, timeout: float = 10.0) -> dict[str, Any]:
    script = f"source {ROS_SETUP} && source {PUPPYPI_SETUP} && {command}"
    return _run(["docker", "exec", CONTAINER, "bash", "-lc", script], timeout=timeout)


def _lines(result: dict[str, Any], limit: int = 200, contains: str = "") -> dict[str, Any]:
    items = [line.strip() for line in result["stdout"].splitlines() if line.strip()]
    if contains:
        needle = contains.lower()
        items = [item for item in items if needle in item.lower()]
    bounded_limit = max(0, min(limit, 1000))
    return {
        "ok": result["ok"],
        "returncode": result["returncode"],
        "count": len(items),
        "items": items[:bounded_limit],
        "truncated": len(items) > bounded_limit,
        "stderr": result["stderr"],
    }


class PuppyPiRos2ReadOnlyDriver(DeviceDriver):
    """Expose safe ROS2 inspection RPCs for a PuppyPi ROS2 container."""

    device_type = os.getenv("DEVICE_TYPE", "quadruped")

    @property
    def status(self) -> DeviceStatus:
        return DeviceStatus(availability="available")

    @rpc()
    async def get_status(self) -> dict[str, Any]:
        """Return host, Docker, and ROS2 bridge status."""
        docker = _run(["docker", "inspect", "-f", "{{.State.Status}}", CONTAINER], timeout=5)
        ros = _run_ros(
            "printf 'ROS_DISTRO=%s\\n' \"$ROS_DISTRO\" && "
            "ros2 pkg list | grep -E '^(puppy_control|ros_robot_controller|interfaces)$'",
            timeout=10,
        )
        return {
            "device": "puppypi",
            "hostname": socket.gethostname(),
            "container": CONTAINER,
            "container_status": docker["stdout"].strip() if docker["ok"] else "unknown",
            "ros_ok": ros["ok"],
            "ros_output": ros["stdout"].splitlines(),
            "errors": {
                "docker": docker["stderr"],
                "ros": ros["stderr"],
            },
        }

    @rpc()
    async def echo(self, text: str) -> dict[str, str]:
        """Echo text for connectivity testing."""
        return {"echo": text}

    @emit(labels={"category": "robot", "safety": "informational"})
    async def robot_status_changed(self, status: str, detail: str = "") -> None:
        """Robot status changed."""
        pass

    @emit(labels={"category": "ros2", "safety": "informational"})
    async def ros_graph_changed(self, entity_type: str, name: str, change_type: str = "updated") -> None:
        """ROS2 graph entity changed."""
        pass

    @emit(labels={"category": "ros2", "safety": "informational"})
    async def telemetry_snapshot(self, node_count: int, topic_count: int, service_count: int) -> None:
        """ROS2 telemetry snapshot."""
        pass

    @emit(labels={"category": "diagnostics", "safety": "informational"})
    async def diagnostic_report(self, level: str, message: str, source: str = "puppypi") -> None:
        """Robot diagnostic report."""
        pass

    @rpc()
    async def get_ros_nodes(self, limit: int = 200, contains: str = "") -> dict[str, Any]:
        """List active ROS2 nodes."""
        return _lines(_run_ros("ros2 node list", timeout=10), limit=limit, contains=contains)

    @rpc()
    async def get_ros_topics(self, limit: int = 200, contains: str = "") -> dict[str, Any]:
        """List active ROS2 topics."""
        return _lines(_run_ros("ros2 topic list", timeout=10), limit=limit, contains=contains)

    @rpc()
    async def get_ros_services(self, limit: int = 200, contains: str = "") -> dict[str, Any]:
        """List active ROS2 services."""
        return _lines(_run_ros("ros2 service list", timeout=10), limit=limit, contains=contains)

    @rpc()
    async def get_ros_packages(self, limit: int = 200, contains: str = "puppy") -> dict[str, Any]:
        """List ROS2 packages, filtered to PuppyPi packages by default."""
        return _lines(_run_ros("ros2 pkg list", timeout=10), limit=limit, contains=contains)

    @rpc()
    async def get_ros_interfaces(self, limit: int = 200, contains: str = "puppy") -> dict[str, Any]:
        """List ROS2 interfaces, filtered to PuppyPi interfaces by default."""
        return _lines(_run_ros("ros2 interface list", timeout=10), limit=limit, contains=contains)

    @rpc()
    async def get_topic_info(self, topic: str) -> dict[str, Any]:
        """Return read-only metadata for a specific ROS2 topic."""
        if not topic.startswith("/") or any(ch in topic for ch in [";", "&", "|", "`", "$", "\\"]):
            return {"ok": False, "error": "topic must be an absolute ROS2 topic name"}
        result = _run_ros(f"ros2 topic info {topic}", timeout=10)
        return {
            "ok": result["ok"],
            "topic": topic,
            "stdout": result["stdout"],
            "stderr": result["stderr"],
        }


async def main() -> None:
    device_id = os.getenv("DEVICE_ID")
    if not device_id and not os.getenv("MESSAGING_CREDENTIALS_FILE"):
        device_id = "puppypi-001"

    runtime = DeviceRuntime(
        driver=PuppyPiRos2ReadOnlyDriver(),
        device_id=device_id,
    )
    await runtime.run()


if __name__ == "__main__":
    asyncio.run(main())
