"""Split the route on the basis of bus capacity using student count to start a new bus from that point onwards."""
def assign_new_bus(path, graph, bus_capacity=100):
    bus_route=[] # dictionary to keep track of all buses used in that route
    curr_bus={"route":[],"cap":0} # dictionary for keeping record of a single bus

    for stop in path: # visit all stops in path 
        student_count=graph.nodes[stop].get("studentcount") # extract student count of each stop

        while student_count>0:
            available_space=bus_capacity-curr_bus["cap"]

            if available_space==0:
                bus_route.append(curr_bus)
                curr_bus={"route":[],"cap":0}
                continue

            if not curr_bus["route"] or curr_bus["route"][-1] != stop:
                curr_bus["route"].append(stop)

            if student_count <= available_space:
                curr_bus["cap"] += student_count
                student_count = 0
            else:
                curr_bus["cap"]+=available_space
                student_count-=available_space
                bus_route.append(curr_bus)
                curr_bus = {"route":[],"cap":0}

    if curr_bus["route"]: # if last bus have students, add it to buses going through that path
        bus_route.append(curr_bus)

    return bus_route