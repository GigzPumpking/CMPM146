"""
Partner: Harsh Jha

Harsh and I worked together to get a sense of the initial program (like dropping two points together, finding source and destination boxes, searching for all boxes, etc).

For the search algorithms, we worked on Breadth First Search first. 

Harsh helped me with Djikstra, while A* was done individually.

Bidirectional A* was a team effort.
"""

from math import inf, sqrt
from heapq import heappop, heappush

def box_contains_point(box, point):
    """
    Checks if a given box contains a point.

    Args:
        box: box to be checked
        point: point to be checked

    Returns:
        True if the point is within the box, False otherwise
    """
    return box[0] <= point[0] <= box[1] and box[2] <= point[1] <= box[3]

def reconstruct_path(boxes, detail_points, destination_box, destination_point):
    """
    Reconstructs the path from source to destination.

    Args:
        boxes: dictionary containing explored boxes
        detail_points: dictionary containing detail points for each box
        destination_box: box containing the destination point

    Returns:
        A list of points from source to destination
    """
    path = []
    path.append(destination_point)
    path.append(detail_points[destination_box])
    current_box = boxes[destination_box]
    while current_box is not None:
        path.append(detail_points[current_box])
        current_box = boxes[current_box]

    return path

def calculate_detail_point(detail_points, current_box, next_box):
    """
    Calculates the detail point for a given box.

    Args:
        detail_points: dictionary containing detail points for each box
        current_box: box to be checked
        next_box: box to be checked

    Returns:
        detail point for the given box
    """
    xRange = [max(current_box[0], next_box[0]), min(current_box[1], next_box[1])]
    yRange = [max(current_box[2], next_box[2]), min(current_box[3], next_box[3])]

    newX = detail_points[current_box][0]
    newY = detail_points[current_box][1]

    if (detail_points[current_box][0] < xRange[0]):
        newX = min(xRange)
    elif (detail_points[current_box][0] > xRange[1]):
        newX = max(xRange)

    if (detail_points[current_box][1] < yRange[0]):
        newY = min(yRange)
    elif (detail_points[current_box][1] > yRange[1]):
        newY = max(yRange)

    return (newX, newY)

def calculate_distance(current_box, next_box):
    """
    Calculates the distance between two boxes' detail points.
    
    Args:
        detail_points: dictionary containing detail points for each box
        current_box: first box
        next_box: second box
        
        Returns:
            distance between the two boxes
    """

    return sqrt((current_box[0] - next_box[0])**2 + (current_box[2] - next_box[2])**2)

def euclidean_distance(source_point, destination_point):
    x1, y1 = source_point
    x2, y2 = destination_point
    return sqrt((x2 - x1)**2 + (y2 - y1)**2)   

def breadth_first_search(detail_points, neighbors, source_box, destination_box, destination_point, boxes):
    """
    Performs breadth-first search to find a path.

    Args:
        frontier: frontier for the breadth-first search
        neighbors: adjacency information for the mesh
        destination_box: box containing the destination point
        boxes: dictionary to store explored boxes

    Returns:
        True if a path is found, False otherwise
    """
    path_found = False
    frontier = []
    path = []

    if source_box:
        frontier.append(source_box)

    while frontier:
        current = frontier.pop(0)

        if current == destination_box:
            path_found = True
            reconstruct_path(boxes, detail_points, destination_box, destination_point)
            return path_found, path

        for next_box in neighbors[current]:
            if next_box not in boxes:
                detail_points[next_box] = calculate_detail_point(detail_points, current, next_box)
                frontier.append(next_box)
                boxes[next_box] = current

    return path_found, path

def dijkstra(detail_points, neighbors, source_box, destination_box, destination_point, boxes):
    """
    Performs Dijkstra's algorithm to find a path.

    Args:
        frontier: frontier for Dijkstra's algorithm
        neighbors: adjacency information for the mesh
        destination_box: box containing the destination point
        boxes: dictionary to store explored boxes

    Returns:
        True if a path is found, False otherwise
    """
    path_found = False
    frontier = []
    cost_so_far = {}
    path = []

    if source_box:
        heappush(frontier, (0, source_box))
        cost_so_far[source_box] = 0

    while frontier:
        priority, current = heappop(frontier)

        if current == destination_box:
            path_found = True
            path = reconstruct_path(boxes, detail_points, destination_box, destination_point)
            return path_found, path

        for next_box in neighbors[current]:
            new_cost = priority + calculate_distance(current, next_box)
            if next_box not in cost_so_far or new_cost < cost_so_far[next_box]:
                detail_points[next_box] = calculate_detail_point(detail_points, current, next_box)
                cost_so_far[next_box] = new_cost
                heappush(frontier, (new_cost, next_box))
                boxes[next_box] = current

    return path_found, path

def astar(detail_points, neighbors, source_box, destination_box, destination_point, boxes):
    """
    Performs A* search to find a path.

    Args:
        frontier: frontier for A* search
        neighbors: adjacency information for the mesh
        destination_box: box containing the destination point
        boxes: dictionary to store explored boxes

    Returns:
        True if a path is found, False otherwise
    """
    path_found = False
    frontier = []
    cost_so_far = {}
    path = []

    if source_box:
        heappush(frontier, (0, source_box))
        cost_so_far[source_box] = 0

    while frontier:
        priority, current = heappop(frontier)

        if current == destination_box:
            path_found = True
            path = reconstruct_path(boxes, detail_points, destination_box, destination_point)
            return path_found, path

        for next_box in neighbors[current]:
            new_cost = cost_so_far[current]
            if next_box not in cost_so_far or new_cost < cost_so_far[next_box]:
                detail_points[next_box] = calculate_detail_point(detail_points, current, next_box)
                cost_so_far[next_box] = new_cost
                priority = new_cost + euclidean_distance(detail_points[next_box], detail_points[destination_box])
                heappush(frontier, (priority, next_box))
                boxes[next_box] = current

    return path_found, path

def bidirectional_astar(neighbors, source_box, source_point, destination_box, destination_point, boxes):
    """
    Performs bidirectional A* search to find a path.

    Args:
        frontier: frontier for bidirectional A* search
        neighbors: adjacency information for the mesh
        destination_box: box containing the destination point
        boxes: dictionary to store explored boxes

    Returns:
        True if a path is found, False otherwise
    """
    path_found = False
    frontier = []
    path = []

    f_paths = {}
    b_paths = {}

    f_cost_so_far = {}
    b_cost_so_far = {}

    f_detail_points = {}
    b_detail_points = {}

    if source_box:
        f_paths[source_box] = None
        f_cost_so_far[source_box] = 0
        f_detail_points[source_box] = source_point
        heappush(frontier, (0, source_box, 1))

    if destination_box:
        b_paths[destination_box] = None
        b_cost_so_far[destination_box] = 0
        b_detail_points[destination_box] = destination_point
        heappush(frontier, (0, destination_box, 0))

    while frontier:
        priority, current, current_destination = heappop(frontier)

        if (current in f_paths) and (current in b_paths):
            path_found = True
            current_box = current
            
            # Add the forward path
            while current_box is not None:
                path.insert(0, f_detail_points[current_box])
                current_box = f_paths[current_box]

            # Add the backward path in reverse order
            current_box = current
            while current_box is not None:
                path.append(b_detail_points[current_box])
                current_box = b_paths[current_box]

            f_paths.update(b_paths)
            
            return path_found, path, f_paths

        for next_box in neighbors[current]:
            new_cost = f_cost_so_far[current] if current_destination == 1 else b_cost_so_far[current]
            cost_so_far = 0
            paths = 0
            if current_destination == 1:
                paths = f_paths
                cost_so_far = f_cost_so_far
            else:
                paths = b_paths
                cost_so_far = b_cost_so_far

            if next_box not in cost_so_far or new_cost < cost_so_far[next_box]:
                cost_so_far[next_box] = new_cost  # update the cost
                priority = 0

                # setting detail points
                if current_destination == 1:
                    f_detail_points[next_box] = calculate_detail_point(f_detail_points, current, next_box)
                    priority = new_cost + euclidean_distance(f_detail_points[next_box], destination_point)
                else:           
                    b_detail_points[next_box] = calculate_detail_point(b_detail_points, current, next_box)
                    priority = new_cost + euclidean_distance(b_detail_points[next_box], source_point)
                heappush(frontier, (priority, next_box, current_destination))
                paths[next_box] = current

    f_paths.update(b_paths)
    return path_found, path, f_paths

def find_path (source_point, destination_point, mesh):

    """
    Searches for a path from source_point to destination_point through the mesh

    Args:
        source_point: starting point of the pathfinder
        destination_point: the ultimate goal the pathfinder must reach
        mesh: pathway constraints the path adheres to

    Returns:

        A path (list of points) from source_point to destination_point if exists
        A list of boxes explored by the algorithm
    """

    path = []
    boxes = {}
    detail_points = {}
    source_box = None
    destination_box = None
    path_found = False

    """
    Find source and destination boxes
    """

    for box in mesh["boxes"]:
        if box_contains_point(box, source_point):
            source_box = box
            boxes[source_box] = None
            detail_points[source_box] = source_point
            print("Source Box " + str(source_box))
        if box_contains_point(box, destination_point):
            destination_box = box
            detail_points[destination_box] = destination_point
            print("Destination Box " + str(destination_box))

    neighbors = mesh["adj"]

    """
    Run search algorithm
    """

    path_found, path, new_boxes = bidirectional_astar(neighbors, source_box, source_point, destination_box, destination_point, boxes)

    if path_found:
        print("Path found!")
    else:
        print("Path not found!")
        path = []
        path.append(source_point)
        path.append(destination_point)

    if new_boxes:
        boxes = new_boxes

    return path, boxes.keys()