import bugzoo.server
from boggart.core.location import FileLocation

from .analysis import Analysis


def test() -> None:
    import orchestrator.snapshot
    files = [
        "src/geometry/tf/src/transform_broadcaster.cpp",
        # "src/geometry/tf/src/transform_listener.cpp",
        # "src/geometry2/tf2/src/buffer_core.cpp",
        # "src/geometry2/tf2/src/cache.cpp",
        # "src/geometry2/tf2/src/static_cache.cpp",
        # "src/geometry2/tf2_ros/src/buffer.cpp",
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
    with bugzoo.server.ephemeral() as client_bugzoo:
        snapshot = orchestrator.snapshot.fetch_baseline_snapshot(client_bugzoo)
        analysis = Analysis.build(client_bugzoo, snapshot, files)

    analysis.dump()

    floc = FileLocation.from_string("/ros_ws/src/geometry/tf/src/transform_broadcaster.cpp@51:1")
    print("INSIDE FUNCTION? {}".format(analysis.is_inside_function(floc)))
    print("INSIDE VOID FUNCTION? {}".format(analysis.is_inside_void_function(floc)))
    print("INSIDE LOOP? {}".format(analysis.is_inside_loop(floc)))
