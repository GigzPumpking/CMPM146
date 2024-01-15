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

def breadth_first_search(frontier, neighbors, destination_box, boxes):
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

    while frontier:
        current = frontier.pop(0)

        if current == destination_box:
            path_found = True
            break

        for next_box in neighbors[current]:
            if next_box not in boxes:
                frontier.append(next_box)
                boxes[next_box] = current

    return path_found

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
    frontier = []
    detail_points = {}
    source_box = None
    destination_box = None

    for box in mesh["boxes"]:
        if box_contains_point(box, source_point):
            source_box = box
            frontier.append(source_box)
            boxes[source_box] = None
            detail_points[source_box] = source_point
            print("Source Box " + str(source_box))
        if box_contains_point(box, destination_point):
            destination_box = box
            detail_points[destination_box] = destination_point
            print("Destination Box " + str(destination_box))

    neighbors = mesh["adj"]

    if breadth_first_search(frontier, neighbors, destination_box, boxes):
        print("Path found")
    else:
        print("No path found")
        return path, boxes.keys()

    """
    Path reconstruction
    """

    path.append(destination_point)
    detail_points[destination_box] = destination_point
    came_from = boxes[destination_box]
    prev_box = destination_box
    while came_from is not None:
        xRange = [max(came_from[0], prev_box[0]), min(came_from[1], prev_box[1])]
        yRange = [max(came_from[2], prev_box[2]), min(came_from[3], prev_box[3])]
        
        newX = detail_points[prev_box][0]
        newY = detail_points[prev_box][1]

        if (detail_points[prev_box][0] < xRange[0]):
            newX = xRange[0]
        elif (detail_points[prev_box][0] > xRange[1]):
            newX = xRange[1]
        
        if (detail_points[prev_box][1] < yRange[0]):
            newY = yRange[0]
        elif (detail_points[prev_box][1] > yRange[1]):
            newY = yRange[1]

        detail_points[came_from] = (newX, newY)

        path.append(detail_points[came_from])
        prev_box = came_from
        came_from = boxes[came_from]

    path.append(source_point)
    path.reverse()

    return path, boxes.keys()
