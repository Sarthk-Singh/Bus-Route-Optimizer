import heapq
import networkx as nx

"""Dijkstra algorithm to find shortest path between stop and university."""
def find_shortest_distance(Graph, start_node, end_node):
    try:
        if start_node not in Graph or end_node not in Graph: # incase stop or university is not present in Graph, return infinite distance and no path
            return float('inf'),[]
        dist={node: float('inf') for node in Graph.nodes} # set reaching weight of each stop to infinite
        dist[start_node]=0; # set weight of starting node to 0
        parent={node: None for node in Graph.nodes} # parent array to keep track of parent node to later re construct the path
        queue=[(0,start_node)] # push starting node to queue with 0 weight

        while queue:
            curr_dist,curr_node=heapq.heappop(queue) # pop least weight and node (using min heap)

            if(curr_node==end_node): # when we reach our destination, reconstruct path by pushing current node and then visiting its parent until None is reached 
                path=[]
                while curr_node is not None:
                    path.append(curr_node)
                    curr_node=parent[curr_node]
                path.reverse() # since path will be constructed in reversed order, reverse the list
                return dist[end_node],path # return minimum distance and path

            if curr_dist > dist[curr_node]: # in case distance was previously updated, then skip if the current distence is greater
                continue

            for u in Graph.neighbors(curr_node): # visit all neighbours of current node
                weight=Graph[curr_node][u].get('weight') # get the wright of that node and calculate the new weight 
                new=weight+curr_dist
                if (new<dist[u]): # Relaxing of nodes
                    dist[u]=new # if the new weight is less than current weight, update the weight and parent and then push the new set of weight,ndoe to min heap
                    parent[u]=curr_node
                    heapq.heappush(queue,(new,u))

        return float('inf'),[] # return infinite distance and empty path
    
    except nx.NetworkXNoPath: # is some edge appear to be missing, assume edge path does not exist there, so return infinte distence and no path 
        return float('inf'),[]