import tkinter as tk
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import copy
import pickle
import random
import math
from DotsandBoxes import DotsAndBoxes
from Grover_tool import Grover

class DotsAndBoxesGUI:
    def __init__(self, root, rows, cols):
        self.root = root
        self.rows = rows
        self.cols = cols
        self.canvas = tk.Canvas(root, width=300, height=300)
        self.canvas.pack()
        self.turn = 'Red'
        self.ai_turn = 'Green'
        self.ai_end = True
        self.current_turn = '#ffa3ed'
        self.edge_color = '#ff0099'
        self.edges = []
        self.game = DotsAndBoxes(rows, cols)
        self.grover_history=[]
        self.boxes = []
        self.dot_positions = {}
        self.dot_ids = {}
        self.turn_label = tk.Label(root, text=f"Current player: Red (human)", font=("Arial", 14))
        self.turn_label.pack()
        self.red_score = 0
        self.current_boxconners=[]
        self.green_score = 0
        self.current_boxs = []
        
        self.current_boxs_index=[]
        self.score_label = tk.Label(root, text=f"Red score: {self.red_score} Green scores: {self.green_score}", font=("Arial", 14))
        self.score_label.pack()
        self.draw_dots()
        self.Quantum_label_flag=False
        self.canvas.bind("<Button-1>", self.click_event)
        self.canvas.bind("<Motion>", self.hover_event)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        
        self.current_boxs_num = 0
        
        # Game history preservation!
        
        self.game_history = []   # Collect images of each step
        self.game_log = []       # Collect logs for each step
        self.game_step ={}       # Collect the status of each step
        self.general_step = 0
        
    def on_closing(self):
        self.save_game()
        self.root.destroy()

    def draw_dots(self):
        for i in range(self.rows + 1):
            for j in range(self.cols + 1):
                x = 50 + j * 50
                y = 50 + i * 50
                dot_id = self.canvas.create_oval(x-5, y-5, x+5, y+5, fill='blue')
                self.dot_positions[(i, j)] = (x, y)
                self.dot_ids[(i, j)] = dot_id


    def click_event(self, event):
        if self.ai_end is False:
            print('The intelligent agent has not finished!')
            return 
        x, y = event.x, event.y
        closest_dot = min(self.dot_positions.keys(), key=lambda k: (self.dot_positions[k][0] - x)**2 + (self.dot_positions[k][1] - y)**2)
        if hasattr(self, 'start_dot'):
            self.end_dot = closest_dot
            if self.is_valid_edge(self.start_dot, self.end_dot):
                self.draw_edge(self.start_dot, self.end_dot,turn='Red')
                self.add_edge(self.start_dot, self.end_dot)
                print(f'edge = {self.game.edge_vector()}')
                self.game_step['Red'+str(len(self.game.edges))] = copy.deepcopy(self.game)
                after_vetor  = self.game.edge_vector()
                
                if self.check_boxes() is False:  # if no new cells are added, switch objects
                    print('No new box, switch roles')
                    self.switch_turn()
                else:  # if a new box is formed, do not switch objects
                    print(f'Detected 🌟 box generation!!! A round of {self. turn}')
                    self.turn_label.config(text=f"Current player: {self.turn} (extra turn)")
                # self.check_game_over()
            del self.start_dot
        else:
            self.start_dot = closest_dot


    def is_valid_edge(self, start, end):
        if start == end:
            return False
        if (start, end) in self.edges or (end, start) in self.edges:
            return False
        if abs(start[0] - end[0]) + abs(start[1] - end[1]) != 1:
            return False
        return True
    
    def check_new_box(self, start, end):
        new_box_formed = False
        x1, y1 = start
        x2, y2 = end
        if abs(x1 - x2) == 1:  # Vertical line
            for dy in [-1, 1]:
                if (x1, y1 + dy) in self.dot_positions and (x2, y2 + dy) in self.dot_positions:
                    if ((x1, y1 + dy), (x2, y2 + dy)) in self.edges or ((x2, y2 + dy), (x1, y1 + dy)) in self.edges:
                        if ((x1, y1), (x1, y1 + dy)) in self.edges or ((x1, y1 + dy), (x1, y1)) in self.edges:
                            if ((x2, y2), (x2, y2 + dy)) in self.edges or ((x2, y2 + dy), (x2, y2)) in self.edges:
                                # self.fill_box([(x1, y1), (x2, y2), (x2, y2 + dy), (x1, y1 + dy)])
                                new_box_formed = True
        elif abs(y1 - y2) == 1:  # Horizontal line
            for dx in [-1, 1]:
                if (x1 + dx, y1) in self.dot_positions and (x2 + dx, y2) in self.dot_positions:
                    if ((x1 + dx, y1), (x2 + dx, y2)) in self.edges or ((x2 + dx, y2), (x1 + dx, y1)) in self.edges:
                        if ((x1, y1), (x1 + dx, y1)) in self.edges or ((x1 + dx, y1), (x1, y1)) in self.edges:
                            if ((x2, y2), (x2 + dx, y2)) in self.edges or ((x2 + dx, y2), (x2, y2)) in self.edges:
                                # self.fill_box([(x1, y1), (x2, y2), (x2 + dx, y2), (x1 + dx, y1)])
                                new_box_formed = True
        if new_box_formed:
            self.turn_label.config(text=f"Current player: {self.turn} (extra turn))")
        return new_box_formed

    # Check if there are any new box generated!
    def check_added_boxes(self,edger_vector_before,edge_vector_after):
        if self.game.count_boxes(edge_vector=edger_vector_before)!=self.game.count_boxes(edge_vector_after):
            return True
        else:
            return False
        
    def draw_edge(self, start, end, turn:str):
        x1, y1 = self.dot_positions[start]
        x2, y2 = self.dot_positions[end]
        
        if turn == 'Red':
            self.edge_color = "#ff0099"
            self.game.draw_edge_red(start, end)
            self.game.add_edge_red(start=start,end=end)
            #self.game.edge_vector()
        if turn == 'Green':
            self.edge_color = '#13ff00'
            self.game.draw_edge_green(start, end)
            self.game.add_edge_green(start=start,end=end)
            #self.game.edge_vector()
            
        self.canvas.create_line(x1, y1, x2, y2, fill=self.edge_color, width=2)

    def add_edge(self, start, end):
        self.edges.append((start, end))


    def check_boxes(self):
        edge_vector = self.game.edge_vector()
        edge_vector = np.array(edge_vector)
        print(f'😰😰😞Checking the number of boxes | The current edge vector is:{edge_vector}')
        box_num = 0
        box_index = []
        boxes = [
            np.array([1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0]),
            np.array([0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0]),
            np.array([0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0]),
            np.array([0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0]),
            np.array([0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0]),
            np.array([0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1])
        ]
        positions=[
            [(1, 0), (0, 0), (0, 1), (1, 1)],
            [(1, 1), (0, 1), (0, 2), (1, 2)],
            [(1, 2), (0, 2), (0, 3), (1, 3)],
            [(2, 0), (1, 0), (1, 1), (2, 1)],
            [(2, 1), (1, 1), (1, 2), (2, 2)],
            [(2, 2), (1, 2), (1, 3), (2, 3)]
        ]
        for i, box in enumerate(boxes, start=1):
            exists = np.all((edge_vector == box) | (box == 0))
            print(f"Does box {i} exist in edge-vector: {exists}")
            if exists == True:
                box_num+=1
                box_index.append(i)
                
                print(f'😞Detected the {i}-th box! box_num={box_num}')
                
        print(f'A total of {box_num} boxes are generated!')
        if box_num!=self.current_boxs_num:
            new_box_index = [i for i in box_index if i not in self.current_boxs_index]
            for each_index in new_box_index:
                self.fill_box(positions[each_index-1])
            
            self.current_boxs_num = box_num
            self.current_boxs_index = box_index
            return True
        else:
            return False
            

    
    
    
    def fill_box(self, box_corners):
        # Obtain the coordinates of vertices
        points = [self.dot_positions[corner] for corner in box_corners]

        # Calculate the center of mass
        cx = sum(x for x, y in points) / len(points)
        cy = sum(y for x, y in points) / len(points)

        # Calculate the angle of each vertex relative to the centroid
        def angle_from_center(point):
            x, y = point
            return math.atan2(y - cy, x - cx)

        # Sort vertices by angle
        sorted_points = sorted(points, key=angle_from_center)

        # Expand the point list and pass it to creat_polygon
        box_id = self.canvas.create_polygon(*[coord for point in sorted_points for coord in point], fill=self.current_turn, stipple='gray50')
        self.canvas.tag_lower(box_id)  # Move the filled squares to the bottom layer
        self.boxes.append(box_corners)
        if self.turn == 'Red':
            self.red_score += 1
        else:
            self.green_score += 1
        self.score_label.config(text=f"Red: {self.red_score} Green: {self.green_score}")
        # update the box count in game objects
        self.game.count_boxes(self.game.edge_vector()) 

    def switch_turn(self):
        #print('Switch roles!')
        if self.turn == 'Red':
            self.turn = 'Green'
            self.edge_color = '#13ff00'
            self.current_turn = '#a9ff87'
        else:
            self.turn = 'Red'
            self.edge_color = '#ff0099'
            self.current_turn = '#ffa3ed'

        self.turn_label.config(text=f"Current player: {self.turn}")
        self.general_step+=1
        
        if self.turn == self.ai_turn:
            self.ai_step()

        
    
    def ai_step(self):
        #print('AI is thinking ...')
        self.turn_label.config(text="Current player: green (quantum intelligent agent)")
        #self.check_and_fill_existing_boxes()
        edge_vector = self.game.edge_vector()
        before_position  = self.game.convert_edge_vector_to_connections(edge_vector=edge_vector)
        if self.Quantum_label_flag is True:
            self.Quantum_label.pack_forget()
        #current_box_num = self.game.count_boxes(edge_vector)
        possible_moves = self.game.decision_maker(edge_vector)
        empty_edge = np.count_nonzero(edge_vector==0)
        # print(f'current number of remaining edges: {empty_ edge}')
        
        
        if possible_moves:
            if empty_edge>2:
                self.grover = Grover(initial_state=edge_vector,good_states=possible_moves)
                self.grover_history.append(self.grover)
                self.Quantum_label = tk.Label(root, text=f"The success probability of the Grover algorithm:{self.grover.probability_win:.3f}", font=("Arial", 14))
                self.Quantum_label.pack()
                self.Quantum_label_flag = True
                if self.grover.num_qbits_activate>10 or self.grover.num_qbits_activate<=3:
                    best_move = random.choice(possible_moves)
                else:
                    best_move =self.grover.give_real_choice() # The answer obtained by Grover search algorithm
            else:
                best_move = random.choice(possible_moves)
                
                
            added_vector = [b_i - a_i for a_i, b_i in zip(edge_vector, best_move)]  
            postion = self.game.convert_edge_vector_to_connections(added_vector)
            current_postion = self.game.convert_edge_vector_to_connections(best_move)
            
            new_pos = list(set(current_postion) - set(before_position))[0]

            self.turn = 'Green'
            current_turn = self.turn
            self.root.after(2000, lambda:self.draw_edge(new_pos[0],new_pos[1],turn='Green'))
            self.root.after(2200, self.check_after_ai_move)
        else:
            # #self.check_and_fill_existing_boxes()
            # self.check_boxes()
            
            print('Game over!')
            return None
        
    def check_after_ai_move(self):
        self.game_step['Green'+str(len(self.game.edges))] =copy.deepcopy(self.game)
        self.general_step+=1
        if self.check_boxes():
            print('AI has formed a new box! Reward one step!')
            self.root.after(1000, self.ai_step)
        else:
            print('AI has not formed a new box!')
            self.root.after(1000, self.switch_turn)
        

    def reset_game(self):
        self.canvas.delete("all")
        self.edges = []
        self.boxes = []
        self.turn = 'Red'
        self.red_score = 0
        self.green_score = 0
        self.turn_label.config(text=f"Current player: {self.turn}")
        self.score_label.config(text=f"Red: {self.red_score} Green: {self.green_score}")
        self.draw_dots()

    def hover_event(self, event):
        x, y = event.x, event.y
        closest_dot = min(self.dot_positions.keys(), key=lambda k: (self.dot_positions[k][0] - x)**2 + (self.dot_positions[k][1] - y)**2)
        for dot in self.dot_ids.values():
            self.canvas.itemconfig(dot, fill='blue')
        self.canvas.itemconfig(self.dot_ids[closest_dot], fill='purple')

    def check_game_over(self):
        total_boxes = self.rows * self.cols
        if len(self.boxes) == total_boxes:
            winner = "Red" if self.red_score > self.green_score else "Green" if self.green_score > self.red_score else "It ends in a draw"
            self.turn_label.config(text=f"Game over! Winner:{winner}")
            
            
    def save_game(self):
        obj = {'game':self.game,'grover_history':self.grover_history,'game_step':self.game_step}
        with open('./game_state.pkl', 'wb') as f:
            pickle.dump(obj, f)
        print('Save game status to game_state.pkl when exiting')
    
    @staticmethod
    def sort_corners(corners):
    # Calculation center point
        cx = sum(x for x, y in corners) / 4
        cy = sum(y for x, y in corners) / 4

        # Calculate the angle of each point relative to the center point
        def angle_from_center(corner):
            x, y = corner
            return math.atan2(y - cy, x - cx)

        # Sort points by angle
        sorted_corners = sorted(corners, key=angle_from_center)
        return sorted_corners

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Quantum Dots and Boxes")
    game = DotsAndBoxesGUI(root, 2, 3)

    root.mainloop()