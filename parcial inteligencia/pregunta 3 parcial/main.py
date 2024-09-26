import os
import base64
from io import BytesIO
from PIL import Image, ImageDraw

# Definición de clases Nodo y Frontera
class Node():
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action

class StackFrontier():
    def __init__(self):
        self.frontier = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[-1]
            self.frontier = self.frontier[:-1]
            return node

class QueueFrontier(StackFrontier):
    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node

# Definición de clase Laberinto
class Maze():
    def __init__(self, filename):
        # Leer el archivo y establecer altura y ancho del laberinto
        with open(filename) as f:
            contents = f.read()

        # Validar puntos de inicio y meta
        if contents.count("A") != 1:
            raise Exception("El laberinto debe tener exactamente un punto de inicio")
        if contents.count("B") != 1:
            raise Exception("El laberinto debe tener exactamente un punto de meta")

        # Establecer altura y ancho del laberinto
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        # Registrar las paredes
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

        self.solution = None

    # Imprimir el laberinto con la solución (si existe)
    def print(self):
        solution = self.solution[1] if self.solution is not None else None
        print()
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()
        print()

    # Obtener vecinos (posibles movimientos)
    def neighbors(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result

    # Resolver el laberinto utilizando DFS o BFS
    def solve(self, algorithm="dfs"):
        self.num_explored = 0

        # Inicializar la frontera
        start = Node(state=self.start, parent=None, action=None)
        if algorithm == "dfs":
            frontier = StackFrontier()
        elif algorithm == "bfs":
            frontier = QueueFrontier()
        else:
            raise ValueError("Algoritmo inválido. Elija 'dfs' o 'bfs'.")

        frontier.add(start)
        self.explored = set()

        # Ciclo de búsqueda
        while True:
            if frontier.empty():
                raise Exception("No hay solución")

            node = frontier.remove()
            self.num_explored += 1

            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            self.explored.add(node.state)

            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action)
                    frontier.add(child)

    # Generar una imagen del laberinto
    def output_image(self, filename, show_solution=True, show_explored=False):
        cell_size = 50
        cell_border = 2

        # Crear una imagen en blanco
        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )
        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution is not None else None

        # Dibujar el laberinto
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                fill = "white" if not col else "black"
                draw.rectangle(
                    [
                        (j * cell_size + cell_border, i * cell_size + cell_border),
                        ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)
                    ],
                    fill=fill
                )

                # Dibujar la solución
                if show_solution and solution is not None and (i, j) in solution:
                    draw.rectangle(
                        [
                            (j * cell_size + cell_border, i * cell_size + cell_border),
                            ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)
                        ],
                        fill="green"
                    )

        img.save(filename)

        # Guardar la imagen como base64
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        print(f"<img src='data:image/png;base64,{img_str}' alt='{filename}' />")

# Función para resolver y comparar
def solve_and_compare(maze_file, algorithm):
    m = Maze(maze_file)
    print(f"Solving {maze_file} with {algorithm.upper()}...")
    m.solve(algorithm)
    print("States Explored:", m.num_explored)
    m.output_image(f"{maze_file[:-4]}_{algorithm}.png", show_explored=True)
    return m.num_explored, len(m.solution[0]) if m.solution else None

# Resolver los laberintos
maze_files = ["maze1.txt", "maze2.txt"]
algorithms = ["dfs", "bfs"]
results = {}

for maze in maze_files:
    results[maze] = {}
    for alg in algorithms:
        states_explored, path_length = solve_and_compare(maze, alg)
        results[maze][alg] = {"states_explored": states_explored, "path_length": path_length}

# Imprimir resultados
for maze in maze_files:
    print(f"\nResults for {maze}:")
    for alg in algorithms:
        print(f"  {alg.upper()}:")
        print(f"    States explored: {results[maze][alg]['states_explored']}")
        print(f"    Path length: {results[maze][alg]['path_length']}")

