from typing import Optional, List, Dict
import json

import bugzoo.server
from bugzoo.client import Client as BugZooClient
from bugzoo.core.bug import Bug as Snapshot
from bugzoo.core.container import Container
from boggart.core.location import FileLocationRange

import orchestrator.snapshot

from .exceptions import BondException


def analyze(client_bugzoo: BugZooClient,
            snapshot: Snapshot) -> None:
    # FIXME assumes binaries are already present in container
    container = None  # type: Optional[Container]
    try:
        container = client_bugzoo.containers.provision(snapshot)
        find_loops(client_bugzoo, snapshot, container)
    finally:
        if container:
            del client_bugzoo.containers[container.uid]


def find_loops(client_bugzoo: BugZooClient,
               snapshot: Snapshot,
               container: Container
               ) -> None:
    loop_bodies = []  # type: List[FileLocationRange]

    out_fn = "loops.json"
    files = [
        "src/geometry/tf/src/transform_broadcaster.cpp",
        "src/geometry/tf/src/transform_listener.cpp",
        "src/geometry2/tf2/src/buffer_core.cpp",
        "src/geometry2/tf2/src/cache.cpp",
        "src/geometry2/tf2/src/static_cache.cpp",
        "src/geometry2/tf2_ros/src/buffer.cpp",
        # "src/geometry2/tf2_ros/src/buffer_client.cpp",
        # "src/geometry2/tf2_ros/src/buffer_server.cpp",
        # "src/geometry2/tf2_ros/src/static_transform_broadcaster.cpp",
        # "src/geometry2/tf2_ros/src/transform_broadcaster.cpp",
        # "src/geometry2/tf2_ros/src/transform_listener.cpp",
        # "src/navigation/amcl/src/amcl/map/map_cspace.cpp",
        # "src/navigation/amcl/src/amcl/sensors/amcl_laser.cpp",
        # "src/navigation/amcl/src/amcl/sensors/amcl_odom.cpp",
        # "src/navigation/amcl/src/amcl/sensors/amcl_sensor.cpp",
        # "src/navigation/amcl/src/amcl_node.cpp",
        # "src/navigation/base_local_planner/src/costmap_model.cpp",
        # "src/navigation/base_local_planner/src/footprint_helper.cpp",
        # "src/navigation/base_local_planner/src/goal_functions.cpp",
        # "src/navigation/base_local_planner/src/latched_stop_rotate_controller.cpp",
        # "src/navigation/base_local_planner/src/local_planner_util.cpp",
        # "src/navigation/base_local_planner/src/map_cell.cpp",
        # "src/navigation/base_local_planner/src/map_grid.cpp",
        # "src/navigation/base_local_planner/src/map_grid_cost_function.cpp",
        # "src/navigation/base_local_planner/src/map_grid_visualizer.cpp",
        # "src/navigation/base_local_planner/src/obstacle_cost_function.cpp",
        # "src/navigation/base_local_planner/src/odometry_helper_ros.cpp",
        # "src/navigation/base_local_planner/src/oscillation_cost_function.cpp",
        # "src/navigation/base_local_planner/src/point_grid.cpp",
        # "src/navigation/base_local_planner/src/simple_scored_sampling_planner.cpp",
        # "src/navigation/base_local_planner/src/simple_trajectory_generator.cpp",
        # "src/navigation/base_local_planner/src/trajectory.cpp",
        # "src/navigation/base_local_planner/src/voxel_grid_model.cpp",
        # "src/navigation/costmap_2d/plugins/inflation_layer.cpp",
        # "src/navigation/costmap_2d/plugins/obstacle_layer.cpp",
        # "src/navigation/costmap_2d/plugins/static_layer.cpp",
        # "src/navigation/costmap_2d/plugins/voxel_layer.cpp",
        # "src/navigation/costmap_2d/src/costmap_2d.cpp",
        # "src/navigation/costmap_2d/src/costmap_2d_publisher.cpp",
        # "src/navigation/costmap_2d/src/costmap_2d_ros.cpp",
        # "src/navigation/costmap_2d/src/costmap_layer.cpp",
        # "src/navigation/costmap_2d/src/costmap_math.cpp",
        # "src/navigation/costmap_2d/src/footprint.cpp"
    ]
    cmd = "bond-loop-finder {}"
    cmd = cmd.format(' '.join(files))
    workdir = "/ros_ws"
    outcome = client_bugzoo.containers.exec(container, cmd, context=workdir)
    # print("executed: {}".format(outcome.output))

    if outcome.code != 0:
        msg = "loop finder exited with non-zero code: {}"
        msg = msg.format(outcome.code)
        raise BondException(msg)

    output = client_bugzoo.files.read(container, out_fn)
    jsn = json.loads(output)  # type: List[Dict[str, str]]
    for loop_info in jsn:
        loc = FileLocationRange.from_string(loop_info['body'])
        loop_bodies.append(loc)

    print(loop_bodies)


def test() -> None:
    with bugzoo.server.ephemeral() as client_bugzoo:
        snapshot = orchestrator.snapshot.fetch_baseline_snapshot(client_bugzoo)
        analyze(client_bugzoo, snapshot)
