import numpy as np
import random
import matplotlib.pyplot as plt
from flask import Flask, request, render_template
import io
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import base64
from flask import make_response
from flask import url_for

app = Flask(__name__)

def ant_colony_optimization(coordinates, start_node, num_ants, num_iterations, evaporation_rate, alpha, beta):
    num_nodes = len(coordinates)
    distances = np.zeros((num_nodes, num_nodes))
    #nodes = np.arange(0,num_nodes)

    # Calculate distances between nodes using Euclidean distance
    for i in range(num_nodes):
        for j in range(i, num_nodes):
            dist = np.sqrt((coordinates[i][0] - coordinates[j][0])**2 + (coordinates[i][1] - coordinates[j][1])**2)
            distances[i][j] = dist
            distances[j][i] = dist

    #print(distances)
    # Initialize pheromone matrix
    pheromone = np.ones((num_nodes, num_nodes))

    # Initialize best path and distance
    best_path = []
    best_distance = float('inf')
    #start_node = np.random.choice(nodes)

    #iteration loop - runs n times
    for iteration in range(num_iterations):
        # Initialize ants
        ants = [[] for _ in range(num_ants)]
        for ant in ants:
            ant.append(start_node)

        # Ants construct solutions
        for i in range(num_nodes-1):
            for ant in ants:
                current_node = ant[-1]
                unvisited_nodes = [node for node in range(num_nodes) if node not in ant]
                probabilities = [np.power(pheromone[current_node][j], alpha) * np.power(1/distances[current_node][j], beta) for j in unvisited_nodes]
                probabilities = probabilities / np.sum(probabilities)
                next_node = np.random.choice(unvisited_nodes, p=probabilities)
                ant.append(next_node)


        # Update pheromone
        for i in range(num_ants):
            path_distance = 0
            for j in range(num_nodes-1):
                current_node = ants[i][j]
                next_node = ants[i][j+1]
                path_distance += distances[current_node][next_node]

            if path_distance < best_distance:
                best_distance = path_distance
                best_path = ants[i]

            for j in range(num_nodes-1):
                current_node = ants[i][j]
                next_node = ants[i][j+1]
                pheromone[current_node][next_node] = (1-evaporation_rate) * pheromone[current_node][next_node] + evaporation_rate / path_distance

        # Reset ants
        ants = [[] for _ in range(num_ants)]
        for ant in ants:
            ant.append(start_node)

#     print(best_path[num_nodes-1])
#     print(distances[num_nodes-1][start_node])
    #best_distance += distances[num_nodes-1][start_node]
    best_path.append(start_node)

    return best_path, best_distance


# # Flask App UI

# app1 = Flask(__name__, static_url_path='/static')

@app.route('/', methods=['GET'])
def index():
    # If it's a GET request, render the form
    return render_template('index.html')


@app.route('/plot', methods=['POST'])
def plot():
    # Get the city coordinates from the uploaded file
    file = request.files['file']
    city_coords = []
    # Read the file line by line
    for line in file:
        # Split the line into its components
        components = line.strip().split()
        # Convert the components to integers and floats as necessary
        node_num = int(components[0])
        x_coord = float(components[1])
        y_coord = float(components[2])
        # Create a tuple with the coordinates and append it to the list
        city_coords.append((x_coord, y_coord))

    # Run the ACO algorithm to get the best path

    start_node = 0
    num_ants = 10
    num_iterations = 100
    evaporation_rate = 0.5
    alpha = 1
    beta = 3

    best_path, best_path_length = ant_colony_optimization(
        city_coords, start_node, num_ants, num_iterations,
        evaporation_rate, alpha, beta
    )

    # Generate the plot as before
    plt.rcParams['figure.figsize'] = [10, 10]
    for i in range(len(city_coords)):
        plt.scatter(city_coords[i][0], city_coords[i][1], marker='.', color='black')
        plt.text(city_coords[i][0], city_coords[i][1], str(i), fontsize=7)

    for i in range(len(best_path)-1):
        plt.plot([city_coords[best_path[i]][0], city_coords[best_path[i+1]][0]], [city_coords[best_path[i]][1], city_coords[best_path[i+1]][1]], 'r-', linewidth=0.5)

    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format='png')
    img_bytes.seek(0)

    path_str = '[' + ', '.join(str(x) for x in best_path) + ']'
    distance = str(best_path_length)
    img_data = base64.b64encode(img_bytes.read()).decode('utf-8')

    
    return render_template('plot.html', path=path_str, distance=distance, img_data=img_data)


@app.route('/static/styles.css')
def styles():
    return app.send_static_file('styles.css')

if __name__ == '__main__':
    app.run()
