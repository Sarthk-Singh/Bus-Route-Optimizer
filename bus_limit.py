"""Split the route on the basis of bus capacity using student count to start a new bus from that point onwards."""
def assign_new_bus(path, graph, bus_capacity=100):
    bus_route=[] # dictionary to keep track of all buses used in that route
    curr_bus={"route":[],"cap":0} # dictionary for keeping record of a single bus

    for stop in path: # visit all stops in path 
        student_count=graph.nodes[stop].get("studentcount") # extract student count of each stop

        if curr_bus["cap"]+student_count>bus_capacity: # if student count exceeds the bus capacity, ad da new bus
            bus_route.append(curr_bus)
            curr_bus={"route": [stop],"cap":student_count}

        else:
            curr_bus["route"].append(stop) # if count does not exceed, add student count to same bus a before
            curr_bus["cap"]+=student_count

    if curr_bus["route"]: # if last bus have students, add it to buses going through that path
        bus_route.append(curr_bus)

    return bus_route