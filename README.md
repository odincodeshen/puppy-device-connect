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

## Profiles

The adapter supports two deployment profiles:

- `puppypi`: real PuppyPi hardware. The host path is fixed to
  `/home/pi/device_connect`, the ROS2 container is `puppypi_ros2`, and the
  PuppyPi workspace setup path is `/home/ubuntu/ros2_ws/install/setup.bash`.
- `rpi5`: generic Raspberry Pi 5 test hardware. The host path defaults to
  `${HOME}/device_connect`, so it works with any Linux username. The default ROS2
  container is `test`.

Profiles live in:

```text
profiles/puppypi.env
profiles/rpi5.env
```

Select a profile with:

```bash
DEVICE_PROFILE=puppypi ./start_fabric.sh
DEVICE_PROFILE=rpi5 ./start_fabric.sh
```

You can also point at a custom shell profile:

```bash
PROFILE_FILE=/path/to/custom.env ./start_fabric.sh
```

Do not set `DEVICE_ID` unless you need to override it. In fabric mode,
`DeviceRuntime` reads the device ID from the credentials file. If `DEVICE_ID` is
set, it must exactly match the `device_id` inside the credentials file.

## Runtime assumptions

- Python environment with `device-connect-edge` installed.
- Docker is available on the host.
- The selected ROS2 container is already running.
- ROS2 Humble setup is available at `ROS_SETUP` inside the container.
- The robot workspace setup is available at `PUPPYPI_SETUP` inside the container.

For the real PuppyPi, start the robot control stack before starting this adapter:

```bash
docker start puppypi_ros2
docker exec -it -u ubuntu -w /home/ubuntu puppypi_ros2 /bin/zsh
```

Inside the container:

```bash
export ROS_DOMAIN_ID=0
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
source /opt/ros/humble/setup.bash
source /home/ubuntu/ros2_ws/install/setup.bash
ros2 launch puppy_control puppy_control.launch.py
```

Leave that process running. The Device Connect adapter does not start the robot
controller; it only executes read-only `ros2` inspection commands through
`docker exec`.

## Fabric mode

Use fabric mode when the device should appear in the hosted dashboard.

```bash
cd /home/pi/device_connect
DEVICE_PROFILE=puppypi ./puppy-device-connect/start_fabric.sh
```

The credentials file is device-specific and must not be committed.

For generic Raspberry Pi 5 testing:

```bash
cd ~/device_connect
DEVICE_PROFILE=rpi5 ./puppy-device-connect/start_fabric.sh
```

Override any profile value inline when needed:

```bash
DEVICE_PROFILE=rpi5 \
PUPPYPI_CONTAINER=my_ros2_container \
FABRIC_CREDENTIALS_FILE="$HOME/device_connect/puppy-device-connect/my-rpi5.creds.json" \
./puppy-device-connect/start_fabric.sh
```

## Local D2D mode

Use D2D mode for local network testing with Zenoh discovery:

```bash
cd /home/pi/device_connect
DEVICE_PROFILE=puppypi ./puppy-device-connect/start_d2d.sh
```

For generic Raspberry Pi 5 testing:

```bash
cd ~/device_connect
DEVICE_PROFILE=rpi5 ./puppy-device-connect/start_d2d.sh
```

D2D mode defaults the device ID to `<profile>-d2d`, such as `puppypi-d2d` or
`rpi5-d2d`. Override it with `DEVICE_ID=...` when running multiple test devices.

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
~/.config/systemd/user/puppypi-device-connect.service
```

To start it now and also enable automatic startup for future boots:

```bash
systemctl --user daemon-reload
systemctl --user enable --now puppypi-device-connect.service
```

To keep the service installed but prevent it from starting automatically on
future boots:

```bash
systemctl --user disable puppypi-device-connect.service
```

This does not stop a service that is already running. Start or stop it manually
with:

```bash
systemctl --user start puppypi-device-connect.service
systemctl --user stop puppypi-device-connect.service
```

To disable automatic startup and stop the currently running service in one
command:

```bash
systemctl --user disable --now puppypi-device-connect.service
```

Check the current state with:

```bash
systemctl --user is-enabled puppypi-device-connect.service
systemctl --user is-active puppypi-device-connect.service
```

For generic Raspberry Pi 5 systemd usage, copy the example and change:

```ini
WorkingDirectory=/home/<user>/device_connect
Environment=DEVICE_PROFILE=rpi5
ExecStart=/home/<user>/device_connect/puppy-device-connect/start_fabric.sh
```
