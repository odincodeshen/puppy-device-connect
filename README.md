# Hiwonder PuppyPi Device Connect adapter

This directory contains a read-only Device Connect adapter for a Raspberry Pi 5
running the PuppyPi ROS2 stack in Docker.

The adapter registers the Pi as a Device Connect device and exposes safe ROS2
inspection RPCs over the fabric. It is intended for remote observability,
diagnostics, and discovery. It does not publish ROS2 messages, call mutating ROS2
services, or command robot motion.

## Scope

- Register a PuppyPi/ROS2 quadruped as a Device Connect device.
- Report device identity and availability for dashboard visibility.
- Execute read-only ROS2 CLI queries inside the PuppyPi ROS2 Docker container.
- Expose read-only RPCs for nodes, topics, services, packages, interfaces, and
  topic metadata.
- Declare informational events for diagnostics and ROS graph changes.

Out of scope:

- Walking, pose, motor, or actuator control.
- Mutating ROS2 state.
- PuppyPi SDK control integration.
- Device Connect framework, server, or dashboard changes.

## Runtime assumptions

- Python environment with `device-connect-edge` installed.
- Docker container named `puppypi-ros2`.
- ROS2 Humble setup at `/opt/ros/humble/setup.bash` inside the container.
- PuppyPi workspace setup at `/workspace/PuppyPi/src/install/setup.bash` inside
  the container.

The container and setup paths can be overridden with:

```bash
PUPPYPI_CONTAINER=puppypi-ros2
ROS_SETUP=/opt/ros/humble/setup.bash
PUPPYPI_SETUP=/workspace/PuppyPi/src/install/setup.bash
```

## Fabric mode

Use fabric mode when the device should appear in the hosted dashboard.

```bash
cd /home/odin/device-connect
export MESSAGING_CREDENTIALS_FILE=/home/odin/device-connect/beta-odin-pi5.creds.json
./puppy-device-connect/start_fabric.sh
```

The credentials file is device-specific and must not be committed.

## Local D2D mode

Use D2D mode for local network testing with Zenoh discovery:

```bash
cd /home/odin/device-connect
./puppy-device-connect/start_d2d.sh
```

## RPCs

- `echo(text)`
- `get_status()`
- `get_ros_nodes(limit=200, contains="")`
- `get_ros_topics(limit=200, contains="")`
- `get_ros_services(limit=200, contains="")`
- `get_ros_packages(limit=200, contains="puppy")`
- `get_ros_interfaces(limit=200, contains="puppy")`
- `get_topic_info(topic)`

## Systemd

`puppypi-device-connect.service.example` is an example user service. Copy it to:

```bash
~/.config/systemd/user/pi5-device-connect.service
```

To start it now and also enable automatic startup for future boots:

```bash
systemctl --user daemon-reload
systemctl --user enable --now pi5-device-connect.service
```

To keep the service installed but prevent it from starting automatically on
future boots:

```bash
systemctl --user disable pi5-device-connect.service
```

This does not stop a service that is already running. Start or stop it manually
with:

```bash
systemctl --user start pi5-device-connect.service
systemctl --user stop pi5-device-connect.service
```

To disable automatic startup and stop the currently running service in one
command:

```bash
systemctl --user disable --now pi5-device-connect.service
```

Check the current state with:

```bash
systemctl --user is-enabled pi5-device-connect.service
systemctl --user is-active pi5-device-connect.service
```
