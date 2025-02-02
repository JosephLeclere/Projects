import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
import base64
from pathlib import Path
import time

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

# Chess Table Class
class ChessTable():
    def __init__(self):
        self.table = np.zeros((8, 8), dtype=int)
        self.turn = 'W'
        self.positions = {(chr(j + ord('a')), i + 1): (i, j) for i in range(8) for j in range(8)}
        self.piece_names = {1: 'Pawn', 2: 'Rook', 3: 'Knight', 4: 'Bishop', 5: 'Queen', 6: 'King'}
        self.colors = {1: 'W', -1: 'B'}
        self.whites_left = 16
        self.blacks_left = 16
        self.set()

    def set(self):
        self.table.fill(0)
        for i in range(8):
            self.table[1, i] = 1
        for i in range(3):
            self.table[0, i] = self.table[0, -(i+1)] = i + 2
        self.table[0, 3] = 5
        self.table[0, 4] = 6
        self.table[-2:] = -self.table[:2][::-1]

    def display_table(self):
        screen = pd.DataFrame(np.full((8, 8), ' '))
        screen.columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        screen.index = range(8, 0, -1)
        for i in range(8):
            for j in range(8):
                if self.table[i, j] != 0:
                    piece = self.colors[np.sign(self.table[i, j])] + self.piece_names[abs(self.table[i, j])]
                    screen.iloc[7-i, j] = piece
        return screen

    def move(self, start, end):
        if self.whites_left == 0:
            return 'Blacks already won.'
        if self.blacks_left == 0:
            return 'Whites already won.'

        start, end = self.positions[start], self.positions[end]
        sign = np.sign(self.table[start])
        if sign == 0:
            return 'This square is empty.'
        if self.turn != self.colors[sign]:
            return 'You cannot move your opponent’s pieces.'
        if self.table[end] * sign > 0:
            return 'You cannot capture your own piece.'

        self.table[end] = self.table[start]
        self.table[start] = 0
        self.turn = 'B' if self.turn == 'W' else 'W'
        return 'Move done.'

# Initialize session state
if "chess_table" not in st.session_state:
    st.session_state.chess_table = ChessTable()

if "selected_cell" not in st.session_state:
    st.session_state.selected_cell = None

if "waiting_for_move" not in st.session_state:
    st.session_state.waiting_for_move = False

# Display the game
st.title("Chess Game")
st.write(f"Current Turn: {st.session_state.chess_table.turn}")

# Create a container to hold the chessboard
chessboard_container = st.container()

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
