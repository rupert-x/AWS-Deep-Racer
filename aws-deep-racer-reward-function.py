import math

def reward_function(params):
    '''
    Custom reward function for AWS DeepRacer.
    Encourages staying close to the center line, maintaining optimal speed,
    smooth steering, following the track direction, and rewarding progress.
    '''

    # Read input parameters
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']
    all_wheels_on_track = params['all_wheels_on_track']
    speed = params['speed']
    steering = abs(params['steering_angle'])  # Only need the absolute steering angle
    progress = params['progress']
    steps = params['steps']
    is_offtrack = params['is_offtrack']
    is_crashed = params['is_crashed']
    is_reversed = params['is_reversed']
    heading = params['heading']
    waypoints = params['waypoints']
    closest_waypoints = params['closest_waypoints']

    # Initialize reward
    reward = 1e-3  # Small number to avoid zero reward

    # Penalize if the car is off-track, crashed, or reversed
    if not all_wheels_on_track or is_offtrack or is_crashed or is_reversed:
        return reward  # Minimum reward

    # Calculate markers at varying distances from the center line
    marker_1 = 0.1 * track_width
    marker_2 = 0.25 * track_width
    marker_3 = 0.5 * track_width

    # Give higher reward for being closer to the center line
    if distance_from_center <= marker_1:
        reward = 1.0
    elif distance_from_center <= marker_2:
        reward = 0.5
    elif distance_from_center <= marker_3:
        reward = 0.1
    else:
        reward = 1e-3  # Likely crashed or close to off-track

    # Penalize large steering to prevent zig-zagging
    ABS_STEERING_THRESHOLD = 10  # Degrees (reduced from 15)
    if steering > ABS_STEERING_THRESHOLD:
        reward *= 0.7  # Increased penalty for oversteering

    # Encourage optimal speed
    OPTIMAL_SPEED_MIN = 1.5  # m/s
    OPTIMAL_SPEED_MAX = 2.5  # m/s
    if OPTIMAL_SPEED_MIN <= speed <= OPTIMAL_SPEED_MAX:
        reward *= 1.5  # Reward for maintaining optimal speed
    elif speed < OPTIMAL_SPEED_MIN:
        reward *= 0.8  # Penalize if too slow
    else:
        reward *= 0.9  # Slight penalty for going too fast

    # Calculate the direction of the center line based on the closest waypoints
    next_point = waypoints[closest_waypoints[1]]
    prev_point = waypoints[closest_waypoints[0]]

    # Calculate the direction in degrees
    track_direction = math.atan2(
        next_point[1] - prev_point[1],
        next_point[0] - prev_point[0]
    )
    track_direction = math.degrees(track_direction)

    # Calculate the difference between the track direction and the heading direction of the car
    direction_diff = abs(track_direction - heading)
    if direction_diff > 180:
        direction_diff = 360 - direction_diff

    # Penalize if the heading is too far from the track direction
    DIRECTION_THRESHOLD = 15.0  # Degrees
    if direction_diff > DIRECTION_THRESHOLD and speed > 2.0:
        reward *= 0.5  # Penalize for high speed during sharp turns

    # Encourage progress
    reward += 10 * progress / 100  # Scale progress reward
    if progress >= 90:
        reward += 50  # Bonus reward for nearing completion of the track

    # Ensure reward is a reasonable number
    reward = float(max(reward, 1e-3))

    return reward