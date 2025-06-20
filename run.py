import os
import psycopg2
import networkx as nx
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from collections import OrderedDict
from algos.bus_limit import assign_new_bus
from algos.shortest_path import find_shortest_distance

# Load environment variables from .env file
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

app = Flask(__name__)

def connect_db():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def fetch_all_stops_with_coordinates():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT stop_name, latitude, longitude FROM bus_stop_coordinates")
        stops = cursor.fetchall()
        cursor.close()
        conn.close()
        return [{"name": name.strip().title(), "latitude": float(lat), "longitude": float(lng)} for name, lat, lng in stops]
    except Exception as e:
        print(f"Error fetching coordinates: {e}")
        return []

def build_graph_from_database():
    G = nx.Graph()
    bus_stops = OrderedDict()

    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Get student counts
        cursor.execute("SELECT stop_name, students FROM bus_stop_coordinates")
        student_data = cursor.fetchall()
        student_counts = {stop.strip().title(): int(count) for stop, count in student_data}

        # Get edges
        cursor.execute("SELECT destination_stop, source_stop, distance_km FROM bus_data")
        route_data = cursor.fetchall()

        for source, dest, distance in route_data:
            source = source.strip().title()
            dest = dest.strip().title()

            G.add_node(source, studentcount=student_counts.get(source, 0))
            G.add_node(dest, studentcount=student_counts.get(dest, 0))
            G.add_edge(source, dest, weight=float(distance))

            bus_stops[source] = None
            bus_stops[dest] = None

        cursor.close()
        conn.close()
        return G, list(bus_stops.keys())

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return nx.Graph(), []
    except Exception as e:
        print(f"Error: {e}")
        return nx.Graph(), []

def print_all_stops_from_database():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        cursor.execute("SELECT stop_name, latitude, longitude, students FROM bus_stop_coordinates")
        rows = cursor.fetchall()

        print("\n📍 All Bus Stops from 'bus_stop_coordinates':\n")
        for row in rows:
            stop_name, lat, lng, students = row
            print(f"🛑 {stop_name} | 🧭 ({lat}, {lng}) | 🎒 {students} students")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error printing stops: {e}")

def print_all_graph_edges(G):
    print("\n🔗 All Edges in the Graph:\n")
    for u, v, data in G.edges(data=True):
        distance = data.get('weight', '?')
        print(f"{u} ↔ {v} | Distance: {distance} km")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/stops_with_coords")
def get_stops_with_coords():
    return jsonify(fetch_all_stops_with_coordinates())

@app.route("/api/stops")
def get_stop_names():
    _, stops = build_graph_from_database()
    return jsonify({"stops": stops})

@app.route("/api/optimize", methods=["POST"])
def optimize_route():
    data = request.get_json()
    start_stop = data.get("start", "").strip().title()
    bus_capacity = int(data.get("capacity", 100))
    G, all_stops = build_graph_from_database()

    if start_stop not in all_stops:
        return jsonify({"error": "Invalid start stop selected."})

    end_stop = "Geu"
    distance, path = find_shortest_distance(G, start_stop, end_stop)

    if distance == float("inf"):
        return jsonify({"error": f"No path found from {start_stop} to {end_stop}."})

    buses = assign_new_bus(path, G, bus_capacity)

    return jsonify({
        "path": path,
        "distance": round(distance, 1),
        "buses": buses
    })

@app.route("/api/map_key")
def get_map_key():
    return jsonify({"key": os.getenv("GOOGLE_MAPS_API_KEY")})

if __name__ == "__main__":
    G, _ = build_graph_from_database()                
    print_all_stops_from_database()                   
    print_all_graph_edges(G)                          
    app.run(debug=True)
