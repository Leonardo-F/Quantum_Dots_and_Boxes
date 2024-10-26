import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import random

class DotsAndBoxes:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.graph = nx.Graph()
        self.edges = []
        self.num_edges = (rows + 1) * cols + (cols + 1) * rows
        self.draw_dots_and_boxes()


    def draw_dots_and_boxes(self):
        fig, ax = plt.subplots()
        for i in range(self.rows + 1):
            for j in range(self.cols + 1):
                ax.plot(j, -i, 'bo')
        ax.set_xlim(-0.5, self.cols + 0.5)
        ax.set_ylim(-self.rows - 0.5, 0.5)
        ax.axis('off')
        self.fig, self.ax = fig, ax

    def draw_edge_red(self, start, end):
        x_values = [start[1], end[1]]
        y_values = [-start[0], -end[0]]
        self.ax.plot(x_values, y_values, 'r-')
        
    def draw_edge_green(self, start, end):
        x_values = [start[1], end[1]]
        y_values = [-start[0], -end[0]]
        self.ax.plot(x_values, y_values, 'g-')

    def add_edge_red(self, start, end):
        # print(f'Called it 🌸 red thread')
        self.edges.append((start, end, 'red'))
        self.graph.add_edge(start, end)
        
    def add_edge_green(self, start, end):
        # print(f'Called it 🌸 green thread')
        self.edges.append((start, end, 'green'))
        self.graph.add_edge(start, end)


    
    def edge_vector(self):
        total_edges = (self.rows + 1) * self.cols + (self.cols + 1) * self.rows
        edge_vector = np.zeros(total_edges, dtype=int)
        
        edge_index = 0
        for i in range(self.rows + 1):
            for j in range(self.cols):
                if ((i, j), (i, j + 1)) in [(e[0], e[1]) for e in self.edges] or ((i, j + 1), (i, j)) in [(e[0], e[1]) for e in self.edges]:
                    edge_vector[edge_index] = 1
                edge_index += 1
        
        for j in range(self.cols + 1):
            for i in range(self.rows):
                if ((i, j), (i + 1, j)) in [(e[0], e[1]) for e in self.edges] or ((i + 1, j), (i, j)) in [(e[0], e[1]) for e in self.edges]:
                    edge_vector[edge_index] = 1
                edge_index += 1
        
        return edge_vector
    
                
    def count_cycles_with_vector(self, vector):
        n = int(np.sqrt(len(vector)))
        adj_matrix = vector.reshape((n, n))
        graph = nx.from_numpy_array(adj_matrix)
        cycles = nx.cycle_basis(graph)
        return len(cycles)
    
    

    def count_boxes(self,edge_vector):
        box_num = 0
        boxes = [
            np.array([1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0]),
            np.array([0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0]),
            np.array([0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0]),
            np.array([0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0]),
            np.array([0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0]),
            np.array([0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1])
        ]
        for i, box in enumerate(boxes, start=1):
            exists = np.all((edge_vector == box) | (box == 0))
            #print(f"Does box {i} exist in edge-vector: {exists}")
            if exists == True:
                box_num+=1
        return box_num
                
                
    def get_boxes_position(self, edge_vector):
        graph = nx.Graph()
        edge_index = 0
        for i in range(self.rows + 1):
            for j in range(self.cols):
                if edge_vector[edge_index] == 1:
                    graph.add_edge((i, j), (i, j + 1))
                edge_index += 1

        for j in range(self.cols + 1):
            for i in range(self.rows):
                if edge_vector[edge_index] == 1:
                    graph.add_edge((i, j), (i + 1, j))
                edge_index += 1

        # Find all loops of 4 edges and return their vertices
        boxes = self.get_boxes(graph)
        return boxes

    def get_boxes(self, graph):
        cycles = nx.cycle_basis(graph)
        boxes = []
        for cycle in cycles:
            if len(cycle) == 4:
                # Check if a square has been formed
                if self.is_square(cycle):
                    boxes.append(cycle)
        return boxes
    
    def fill_box(self, box_corners,turn):
        x1, y1 = box_corners[0]
        x2, y2 = box_corners[1]
        x3, y3 = box_corners[2]
        x4, y4 = box_corners[3]
        box_id = self.canvas.create_polygon(x1, y1, x2, y2, x3, y3, x4, y4, fill=self.current_turn, stipple='gray50')
        self.canvas.tag_lower(box_id)  # Move the filled squares to the bottom layer
        self.boxes.append(box_corners)
        if self.turn == 'Red':
            self.red_score += 1
        else:
            self.green_score += 1
        self.score_label.config(text=f"Red score: {self.red_score} Green score: {self.green_score}")
            # Update the filled squares in game objects
        self.game.count_boxes(self.game.edge_vector())  # Update the grid count in game objects

    def draw_game(self, save_path=None):
        # 强制重新绘制图形和坐标轴
        self.draw_dots_and_boxes()

        for start, end, color in self.edges:
            if color == 'red':
                self.draw_edge_red(start, end)
            elif color == 'green':
                self.draw_edge_green(start, end)
        
        if save_path:
            plt.savefig(save_path) 
        plt.show()
        plt.clf() 

        
        
    def search_next_step(self,edge_vector:np.array):
        next_plain_steps = [] # The next step cannot form a new box
        next_good_steps = [] # The next step is to form a new box
        for i in range(len(edge_vector)):
            num_boxes_before = self.count_boxes(edge_vector=edge_vector)
            if edge_vector[i] == 0:
                new_vector = edge_vector.copy()
                new_vector[i] = 1
                num_boxes_after = self.count_boxes(edge_vector=new_vector)
                if num_boxes_after != num_boxes_before:
                    #print(f'Form a new box!: {new_vector}')
                    next_good_steps.append(new_vector)
                else:
                    #print(f'No new box has been formed: {new_vector}')
                    next_plain_steps.append(new_vector)
        # The return is the next good choice and the general choice
        return next_plain_steps,next_good_steps
    
    def decision_maker(self,current_state:np.array):
        # search for whether your next step can form a new box
        print('Called the decision function!')
        finnal_choice = []
        plain_steps,good_steps=self.search_next_step(current_state)
        if len(good_steps)>0:
            print(f'There are steps that can form a box!')
            return good_steps
        print('There are no steps that can form a box!')

        for each in plain_steps:
            second_plain_steps,second_good_steps=self.search_next_step(each)
            if len(second_good_steps) >0:
                pass
                #print(f'This step is not allowed! The opponent can play good chess!{each}')
            else:
                #print(f'This step is possible! The opponent is also slightly inferior!{each}')
                finnal_choice.append(each)
        
        #print(f'The final reasonable number of choices is:{len(finnal_choice)}')
        if len(finnal_choice)==0:
            if len(plain_steps)==0:
                return None
            else:
                finnal_choice = [random.choice(plain_steps)]
        
        #print(f'The final choice for return is:{finnal_choice}')
                
        return finnal_choice
    
    def draw_game_from_vector(self, edge_vector):
        # initialize graphics and coordinate axes
        fig, ax = plt.subplots()
        for i in range(self.rows + 1):
            for j in range(self.cols + 1):
                ax.plot(j, -i, 'bo')
        ax.set_xlim(-0.5, self.cols + 0.5)
        ax.set_ylim(-self.rows - 0.5, 0.5)
        ax.axis('off')

        # draw edges based on edge_vector
        edge_index = 0
        connections = []
        for i in range(self.rows + 1):
            for j in range(self.cols):
                if edge_vector[edge_index] == 1:
                    x_values = [j, j + 1]
                    y_values = [-i, -i]
                    ax.plot(x_values, y_values, 'r-')
                    connections.append(((i, j), (i, j + 1)))
                edge_index += 1

        for j in range(self.cols + 1):
            for i in range(self.rows):
                if edge_vector[edge_index] == 1:
                    x_values = [j, j]
                    y_values = [-i, -(i + 1)]
                    ax.plot(x_values, y_values, 'r-')
                    connections.append(((i, j), (i + 1, j)))
                edge_index += 1

        plt.show()
        return connections
        
        
    def convert_edge_vector_to_connections(self, edge_vector):
        connections = []
        edge_index = 0
        for i in range(self.rows + 1):
            for j in range(self.cols):
                if edge_vector[edge_index] == 1:
                    connections.append(((i, j), (i, j + 1)))
                edge_index += 1

        for j in range(self.cols + 1):
            for i in range(self.rows):
                if edge_vector[edge_index] == 1:
                    connections.append(((i, j), (i + 1, j)))
                edge_index += 1

        return connections
    
    def is_square(self, cycle):
        if len(cycle) != 4:
            return False

        # Calculate the coordinate difference of four vertices to ensure the formation of a square
        cycle_sorted = sorted(cycle)  
        x_coords = [x for x, y in cycle_sorted]
        y_coords = [y for x, y in cycle_sorted]

        # For a square, the x and y coordinates should each contain only two different values
        if len(set(x_coords)) == 2 and len(set(y_coords)) == 2:
            return True
        return False

