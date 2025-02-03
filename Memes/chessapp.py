import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
import base64
from pathlib import Path
import time

# Chess Table Class
class Pawn():
    def __init__(self):
        self.name = 'Pawn'
    def eligible_move(self, start, end, color):
        if start[1] == end[1]:
            if start[0] == 1 and color:
                return end[0] - start[0] <= 2
            elif start[0] == 6 and not(color):
                return end[0] - start[0] >= -2
            else:
                return end[0] - start[0] == 1 if color else end[0] - start[0] == -1
        return False

class Bishop():
    def __init__(self):
        self.name = 'Bishop'
    def eligible_move(self, start, end, color):
        if abs(start[0]-end[0]) == abs(start[1]-end[1]):
            return True
        return False

class Rook():
    def __init__(self):
        self.name = 'Rook'
    def eligible_move(self, start, end, color):
        if start[0] == end[0] or start[1] == end[1]:
            return True
        return False

class Queen():
    def __init__(self):
        self.name = 'Queen'
    def eligible_move(self, start, end, color):
        if abs(start[0]-end[0]) == abs(start[1]-end[1]) or start[0] == end[0] or start[1] == end[1]:
            return True
        return False

class King():
    def __init__(self):
        self.name = 'King'
    def eligible_move(self, start, end, color):
        if abs(start[0]-end[0]) <= 1 and abs(start[1]-end[1]) <= 1:
            return True
        return False

class Knight():
    def __init__(self):
        self.name = 'Knight'
    def eligible_move(self, start, end, color):
        if abs(start[0]-end[0]) == 2 and abs(start[1]-end[1]) == 1:
            return True
        if abs(start[0]-end[0]) == 1 and abs(start[1]-end[1]) == 2:
            return True
        return False

class ChessTable():
    #The board has integers positive for white and negative for black, zeros for empty squares.
    def __init__(self):
        self.table = []
        self.turn = 'W'
        self.positions = {(chr(j+ord('a')), i+1): (i,j) for i in range(8) for j in range(8)}
        self.piece_names = {1: Pawn(), 2: Rook(), 3: Knight(), 4:Bishop(), 5: Queen(), 6: King()}
        self.colors = {1: 'W', -1: 'B'}
        self.whites_left = 16
        self.blacks_left = 16


    def set(self):
        self.table = np.zeros((8,8), dtype=int)
        for i in range(8):
            self.table[1,i] = 1
        for i in range(3):
            self.table[0,i] = self.table[0,-(i+1)] = i + 2
        self.table[0,3] = 5
        self.table[0,4] = 6
        self.table[-2:] = -self.table[:2][::-1]
        
    def display_table(self):
        screen = pd.DataFrame(np.zeros((8,8), dtype=str))
        screen.columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        screen.index = range(8,0,-1)
        for i in range(8):
            for j in range(8):
                if self.table[i,j] == 0:
                    screen.iloc[7-i,j] = ' '
                else:
                    screen.iloc[7-i,j] = self.colors[np.sign(self.table[i,j])] + self.piece_names[abs(self.table[i,j])].name
        return screen
        
    def update_count(self, color, target):
            if color and not(target):
                self.blacks_left -= 1
            elif not(color) and not(target):
                self.whites_left -= 1
    
    def checking_game_over(self):
        if 6 not in self.table:
            print('Blacks won.')
            return True
        if -6 not in self.table:
            print('Whites won.')
            return True
        return False

    
    def move(self, start, end):
        if self.checking_game_over():
            return 
        start, end = self.positions[start], self.positions[end]
        sign = np.sign(self.table[start])
        color = (1 + sign)/2
        if color == 0.5:
            return 'This square is empty.'
        
        elif self.turn != self.colors[sign]:
            return 'You cannot move your opponents pieces.'
        
        current_piece = self.piece_names[abs(self.table[start])]
        
        if start == end:
            return 'You must move the piece.'
        
        elif np.sign(self.table[start]) == np.sign(self.table[end]):
            return 'You cannot move to a square with a piece of the same color.'
        
        elif current_piece.name == 'Pawn':
            target = self.table[end]
            if sign * np.sign(self.table[end]) == -1: #Pawn is of opposite color to the one at end.
                if sign == 1:
                    if end[1] - start[1] == 1 and abs(end[0] - start[0]) == 1:
                        self.table[end] = self.table[start]
                        self.table[start] = 0
                        self.turn = 'B'
                        self.update_count(color, target)
                        return 'Move done.'
                else:
                    if end[1] - start[1] == -1 and abs(end[0] - start[0]) == 1:
                        self.table[end] = self.table[start]
                        self.table[start] = 0
                        self.turn = 'W'
                        self.update_count(color, target)
                        return 'Move done.'
            elif current_piece.eligible_move(start, end, color):
                target = self.table[end]
                self.table[end] = self.table[start]
                self.table[start] = 0
                self.turn = 'B' if self.turn == 'W' else 'W'
                return 'Move done.'
            return current_piece.name + ' is not allowed to do this move.'
        
        elif current_piece.eligible_move(start, end, color):
            target = self.table[end]
            self.table[end] = self.table[start]
            self.table[start] = 0
            self.turn = 'B' if self.turn == 'W' else 'W'
            self.update_count(color, target)
            return 'Move done.'
        else:
            return current_piece.name + ' is not allowed to do this move.'
        
# Convert images to Base64
def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    return base64.b64encode(img_bytes).decode()

def create_image_button(img_path, key):
    img_base64 = img_to_bytes(img_path)
    html_code = f"""
    <button style="border:none; background:none; padding:0; cursor:pointer;" 
            onclick="document.getElementById('{key}').click()">
        <img src="data:image/png;base64,{img_base64}" style="width:60px; height:60px;">
    </button>
    <input type="hidden" id="{key}" onclick="window.parent.postMessage('{key}', '*')">
    """
    return html_code

# Initialize Chess Pieces Images
@st.cache_resource
def load_piece_images():
    piece_paths = {
        'WPawn': 'Pieces/WPawn.png',
        'WRook': 'Pieces/WRook.png',
        'WKnight': 'Pieces/WKnight.png',
        'WBishop': 'Pieces/WBishop.png',
        'WQueen': 'Pieces/WQueen.png',
        'WKing': 'Pieces/WKing.png',
        'BPawn': 'Pieces/BPawn.png',
        'BRook': 'Pieces/BRook.png',
        'BKnight': 'Pieces/BKnight.png',
        'BBishop': 'Pieces/BBishop.png',
        'BQueen': 'Pieces/BQueen.png',
        'BKing': 'Pieces/BKing.png',
    }
    return {name: img_to_bytes(path) for name, path in piece_paths.items()}

piece_images = load_piece_images()

# Initialize session state
if "chess_table" not in st.session_state:
    st.session_state.chess_table = ChessTable()
    st.session_state.chess_table.set()

if "selected_cell" not in st.session_state:
    st.session_state.selected_cell = None

if "waiting_for_move" not in st.session_state:
    st.session_state.waiting_for_move = False

# Display the game
st.title("Chess Game")
st.write(f"Current Turn: {st.session_state.chess_table.turn}")

# Create a container to hold the chessboard
chessboard_container = st.container(border=1)

# Adjust the display to fit inside a square layout
with chessboard_container:
    cols = st.columns(8)
    for i in range(8):
        for j in range(8):
            with cols[j]:
                piece_label = st.session_state.chess_table.display_table().iloc[i, j].strip()
                button_key = f"cell_{i}_{j}"
                
                # Render piece button or empty cell
                if piece_label in piece_images:
                    button_html = create_image_button(f"Pieces/{piece_label}.png", button_key)
                else:
                    button_html = f"""<button id="{button_key}" style="width:60px; height:60px; border:none; background:none;"></button>"""
                st.markdown(button_html, unsafe_allow_html=True)

                # Handle button clicks
                if st.button("", key=button_key):
                    if st.session_state.selected_cell is None:
                        st.session_state.selected_cell = (i, j)
                    else:
                        if not st.session_state.waiting_for_move:
                            st.session_state.waiting_for_move = True
                            start = (chr(st.session_state.selected_cell[1] + ord('a')), 8 - st.session_state.selected_cell[0])
                            end = (chr(j + ord('a')), 8 - i)
                            result = st.session_state.chess_table.move(start, end)
                            
                            # Update the board after move is done
                            st.session_state.selected_cell = None
                            st.session_state.waiting_for_move = False
                            st.write(result)
