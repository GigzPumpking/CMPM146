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

def graph_cost(current, next_box):
    """
    Calculates the cost of moving from the current box to the next box.

    Args:
        current: current box
        next_box: next box

    Returns:
        Cost of moving from current to next_box
    """
    # You need to implement this based on your problem's requirements
    # For example, it might involve calculating the distance between the boxes
    # or some other metric relevant to your problem.

    """ get the distance between the two boxes """
    x1 = (current[0] + current[1]) / 2
    y1 = (current[2] + current[3]) / 2
    x2 = (next_box[0] + next_box[1]) / 2
    y2 = (next_box[2] + next_box[3]) / 2

    cost = ((x1 - x2)**2 + (y1 - y2)**2)**0.5

    return cost

def breadth_first_search(neighbors, source_box, destination_box, boxes):
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

    if source_box:
        frontier.append(source_box)

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

def dijkstra(neighbors, source_box, destination_box, boxes):
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
    frontier = {}
    cost_so_far = {}

    if source_box:
        frontier[source_box] = 0
        cost_so_far[source_box] = 0

    while frontier:
        current = frontier.popitem()[0]

        if current == destination_box:
            path_found = True
            break

        for next_box in neighbors[current]:
            new_cost = cost_so_far[current] + graph_cost(current, next_box)
            if next_box not in cost_so_far or new_cost < cost_so_far[next_box]:
                cost_so_far[next_box] = new_cost
                priority = new_cost
                frontier[next_box] = priority
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
    detail_points = {}
    source_box = None
    destination_box = None

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

    if breadth_first_search(neighbors, source_box, destination_box, boxes):
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
