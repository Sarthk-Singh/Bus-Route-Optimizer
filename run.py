import psycopg2
import networkx as nx
import os
from dotenv import load_dotenv
from collections import OrderedDict

# Load .env
load_dotenv()

# DB details
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


def build_graph_from_database():
    """
    Build a graph from bus route data and attach student counts to nodes.
    """
    G = nx.Graph()
    bus_stops = OrderedDict()

    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        # fetching student counts from bus_stop_coordinates table
        cursor.execute("SELECT busstop, studentcount FROM bus_stop_coordinates")
        student_data = cursor.fetchall()
        student_counts = {stop.strip().capitalize(): int(count) for stop, count in student_data}

        # Fetch routes in the order they appear in DB
        cursor.execute("SELECT fromstop, tostop, distance_km FROM bus_data")
        route_data = cursor.fetchall()

        for from_stop, to_stop, distance in route_data:
            from_stop = from_stop.strip().title()
            to_stop = to_stop.strip().title()


            G.add_node(from_stop, studentcount=student_counts.get(from_stop, 0))
            G.add_node(to_stop, studentcount=student_counts.get(to_stop, 0))

            G.add_edge(from_stop, to_stop, weight=float(distance))
            G.add_edge(to_stop, from_stop, weight=float(distance))

            bus_stops[from_stop] = None
            bus_stops[to_stop] = None

        cursor.close()
        conn.close()

        return G, list(bus_stops.keys())
    
    #handing if database is not connected
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return nx.Graph(), []
    except Exception as e:
        print(f"Error: {e}")
        return nx.Graph(), []



def main():
    # Building graph
    G, all_stops = build_graph_from_database()

    # Displaying Bus stops 
    print("Available Bus Stops:")
    for i, stop in enumerate(all_stops, 1):
        print(f"{i}. {stop}")

    # Get user input
    while True:
        try:
            choice = int(input("\nEnter the number of your starting stop: "))
            if 1 <= choice <= len(all_stops):
                start_stop = all_stops[choice - 1]
                break
            else:
                print(f"Enter a number between 1 and {len(all_stops)}")
        except ValueError:
            print("Please enter a valid number.")

    # fixed university stop
    end_stop = "Graphic Era"

    # Get shortest route
    distance, path = find_shortest_distance(G, start_stop, end_stop)

    if distance == float('inf'):
        print(f"\nNo path found from {start_stop} to {end_stop}")
        return

    print(f"\nShortest path from {start_stop} to {end_stop}:")
    print(f"Total distance: {distance:.1f} km")
    print("Route: " + " → ".join(path))

    # Bus capacity system
    bus_capacity = 100
    buses = split_route_by_capacity(path, G, bus_capacity)

    print(f"\n Bus Planning (Capacity = {bus_capacity} students):")
    for i, bus in enumerate(buses, 1):
        print(f"\n Bus {i}")
        print(f"Route: {' → '.join(bus['route'])}")
        print(f"Students on board: {bus['load']} / {bus_capacity}")


if __name__ == "__main__":
    main()
