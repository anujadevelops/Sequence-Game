from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QGridLayout, QDialog, QLineEdit, QCheckBox, QComboBox, QDialogButtonBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QTextEdit
from PySide6.QtWidgets import QScrollArea, QWidget
import random
import sys

class SequenceGameGUI(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.setWindowTitle("🎯 Sequence Game")

        self.scores = [0, 0]
        self.players = settings['players']
        self.vs_ai = settings['vs_ai']
        self.ai_difficulty = settings['ai_difficulty']
        self.win_label = None
        self.loss_label = None
        self.draw_label = None
        self.board_layout = self.generate_random_board()

        self.corner_positions = {(0, 0), (0, 9), (9, 0), (9, 9)}
        self.current_player = 0
        self.deck = []
        for _ in range(2):
            for suit in ['♠', '♥', '♦', '♣']:
                for rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']:
                    if rank == 'J':
                        if suit in ['♠', '♥']:
                            self.deck.append("1-Eyed Jack")
                        else:
                            self.deck.append("2-Eyed Jack")
                    else:
                        self.deck.append(f"{rank}{suit}")
        random.shuffle(self.deck)

        self.init_ui()
        self.removal_mode = True
        self.hands = self.deal_cards(2)
        self.selected_card = None
        self.removable_positions = set()
        self.update_hand()
        self.ai_play_if_needed()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)
        self.score_label = QLabel(self.get_score_text())
        self.score_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.score_label)
        self.grid = QGridLayout()
        self.board_buttons = []
        for r in range(10):
            row_buttons = []
            for c in range(10):
                card = self.board_layout[r][c]
                btn = QPushButton(card)
                btn.setFixedSize(60, 60)
                btn.setFont(QFont("Arial", 10, QFont.Bold))
                btn.clicked.connect(lambda _, row=r, col=c: self.place_marker(row, col))
                if card not in ["Joker", "1-Eyed Jack", "2-Eyed Jack"]:
                    if '♦' in card or '♥' in card:
                        btn.setStyleSheet("color: red;")
                    else:
                        btn.setStyleSheet("color: black;")
                if card == "Joker" or (r, c) in self.corner_positions:
                    btn.setStyleSheet("background-color: lightgreen;")
                    btn.setEnabled(False)

                self.grid.addWidget(btn, r, c)
                row_buttons.append(btn)
            self.board_buttons.append(row_buttons)
        layout.addLayout(self.grid)
            
        self.hand_layout = QHBoxLayout()
        layout.addLayout(self.hand_layout)
        self.turn_label = QLabel()
        self.turn_label.setFont(QFont("Arial", 11))
        layout.addWidget(self.turn_label)

        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        self.deck_label = QLabel()
        layout.addWidget(self.deck_label)

        button_row = QHBoxLayout()
        
        self.restart_button = QPushButton("🔄 Restart Game")
        self.restart_button.setVisible(True)
        self.restart_button.clicked.connect(self.restart_game)
        button_row.addWidget(self.restart_button)

        self.help_button = QPushButton("❓ Help / How to Play")
        self.help_button.clicked.connect(self.show_help)
        button_row.addWidget(self.help_button)

        layout.addLayout(button_row)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def show_help(self):
        help_dialog = HelpDialog()
        help_dialog.exec()

    def get_score_text(self):
        return f"Sequences - {self.players[0]}: {self.scores[0]} | {self.players[1]}: {self.scores[1]}"
  
    def play_status_animation(self, color):
        animation = QPropertyAnimation(self.status_label, b"styleSheet")
        animation.setDuration(1200)
        animation.setStartValue("color: black;")
        animation.setEndValue(f"color: {color}; font-weight: bold; font-size: 18px;")
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start(QPropertyAnimation.DeleteWhenStopped)

    def update_hand(self):
        for i in reversed(range(self.hand_layout.count())):
            self.hand_layout.itemAt(i).widget().deleteLater()
 
        if self.vs_ai and self.current_player == 1:
            for _ in self.hands[self.current_player]:
                btn = QPushButton("🎴")
                btn.setEnabled(False)
                self.hand_layout.addWidget(btn)
        else:
            for idx, card in enumerate(self.hands[self.current_player]):
                btn = QPushButton(card)
                btn.setFont(QFont("Arial", 10, QFont.Bold))
                if '♦' in card or '♥' in card:
                    btn.setStyleSheet("color: red;")
                else:
                    btn.setStyleSheet("color: black;")
                btn.clicked.connect(lambda _, i=idx: self.select_card(i))
                self.hand_layout.addWidget(btn)

        self.turn_label.setText(f"{self.players[self.current_player]}'s Turn")
        self.deck_label.setText(f"Cards left in Deck: {len(self.deck)}")
        self.score_label.setText(self.get_score_text())

    def select_card(self, idx):
        self.selected_card = self.hands[self.current_player][idx]
        self.status_label.setText(f"Selected: {self.selected_card}")
        self.clear_highlights()
        
        if self.selected_card == "1-Eyed Jack":
            self.highlight_removable_chips()
            self.removal_mode = True  # Enter removal mode
        else:
            self.removal_mode = False  # Normal mode
    def check_possible_sequence(self, row, col, chip):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            sequence_positions = [(row, col)]
            r, c = row + dr, col + dc
            while 0 <= r < 10 and 0 <= c < 10 and (
                self.board_buttons[r][c].text() in [chip, '🔴'] or (r, c) in self.corner_positions
            ):
                sequence_positions.append((r, c))
                r += dr
                c += dc

            r, c = row - dr, col - dc
            while 0 <= r < 10 and 0 <= c < 10 and (
               self.board_buttons[r][c].text() in [chip, '🔴'] or (r, c) in self.corner_positions
            ):
                
                sequence_positions.append((r, c))
                r -= dr
                c -= dc

            if len(sequence_positions) >= 4:  # Not 5 because AI is testing a future move
                return True
        return False

    def place_marker(self, row, col):

        button = self.board_buttons[row][col]
        board_card = self.board_layout[row][col]
        chip = '🔵' if self.current_player == 0 else '🟢'
        opponent_chip = '🟢' if self.current_player == 0 else '🔵'
        
        if self.removal_mode:
            if (row, col) in self.removable_positions:
                self.perform_removal(row, col)
            else:
                self.status_label.setText("Select a highlighted chip to remove.")
            return

        if not self.selected_card:
            self.status_label.setText("Select a card first.")
            return
       
        if not button.isEnabled() and (row, col) not in self.corner_positions:
            self.status_label.setText("Spot already taken or locked.")
            return
        
        if self.selected_card == "2-Eyed Jack":
            button.setText(chip)
            button.setEnabled(False)
            self.check_sequence(chip, row, col)
            self.end_turn()

        elif self.selected_card == board_card:
            button.setText(chip)
            button.setEnabled(False)
            self.check_sequence(chip, row, col)
            self.end_turn()
        else:
            self.status_label.setText("Card doesn't match this space.")
    
    def makeRandomMove(self):
        hand = self.hands[self.current_player]
        opponent_chip = '🟢' if self.current_player == 0 else '🔵'
        
        while hand:
            card = random.choice(hand)
            
            if card == "1-Eyed Jack":
                removable = []
                for r in range(10):
                    for c in range(10):
                        opponent_chip = '🟢' if self.current_player == 0 else '🔵'
                        if self.board_buttons[r][c].text() == opponent_chip and (r, c) not in self.corner_positions:
                            removable.append((r, c))
                if removable:
                           r, c = random.choice(removable)
                           self.selected_card = card
                           self.highlight_removable_chips()
                           self.removal_mode = True
                           self.place_marker(r, c)
                           return True
                                
            elif card == "2-Eyed Jack":
                for r in range(10):
                    for c in range(10):
                        btn = self.board_buttons[r][c]
                        if btn.isEnabled():
                            self.selected_card = card
                            self.place_marker(r, c)
                            return True
                return True

            else:
                for r in range(10):
                    for c in range(10):
                        btn = self.board_buttons[r][c]
                        if btn.isEnabled() and self.board_layout[r][c] == card:
                            self.selected_card = card
                            self.place_marker(r, c)
                            return True

            hand.remove(card)
            if self.deck:
                hand.append(self.deck.pop())

        return True

    def check_sequence(self, chip, row, col):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for dr, dc in directions:
            sequence_positions = [(row, col)]

            r, c = row + dr, col + dc
            while 0 <= r < 10 and 0 <= c < 10 and (
                self.board_buttons[r][c].text() in [chip, '🔴'] or (r, c) in self.corner_positions
            ):
                sequence_positions.append((r, c))
                r += dr
                c += dc

            r, c = row - dr, col - dc
            while 0 <= r < 10 and 0 <= c < 10 and (
                self.board_buttons[r][c].text() in [chip, '🔴']  or (r, c) in self.corner_positions
            ):
                sequence_positions.append((r, c))
                r -= dr
                c -= dc

            if len(sequence_positions) >= 5:
                sequence_positions.sort()
                for i in range(len(sequence_positions) - 4):
                    five = sequence_positions[i:i+5]
                    red_count = sum(
                        1 for r, c in five if self.board_buttons[r][c].text() == '🔴'
                    )
                    if red_count <= 1:
                        for r, c in five:
                            if (r, c) not in self.corner_positions:
                                self.board_buttons[r][c].setText('🔴')
                        self.scores[self.current_player] += 1
                        self.status_label.setText(f"{self.players[self.current_player]} completed a sequence!")
                        self.play_status_animation("blue")

                        if self.scores[self.current_player] >= 2:
                            self.status_label.setText(f"🏆 {self.players[self.current_player]} wins the game!")
                            self.play_status_animation("green")
                            self.play_win_animation()
                            self.play_loss_animation(loser=1 - self.current_player)
                            self.disable_all_buttons()
                        return 

    def play_loss_animation(self, loser):
        if self.loss_label is not None:
            self.loss_label.deleteLater()
        self.loss_label = QLabel(f"💔 {self.players[loser]} Lost! 💔")
        self.loss_label.setFont(QFont("Arial", 22, QFont.Bold))
        self.loss_label.setStyleSheet("color: red; background-color: white;")
        self.loss_label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.loss_label)

    def play_win_animation(self):
        if self.win_label is not None:
            self.win_label.deleteLater()
        self.win_label = QLabel(f"🏆 {self.players[self.current_player]} Wins! 🏆")
        self.win_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.win_label.setStyleSheet("color: gold; background-color: white;")
        self.win_label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget( self.win_label)

    def deal_cards(self, num_players):
        cards_per_player = {2: 7}
        total_needed = num_players * cards_per_player.get(num_players, 6)

        if len(self.deck) < total_needed:
            self.status_label.setText("♻️ Deck too small. Regenerating...")
            self.play_status_animation("orange")
            self.regenerate_full_deck()

        fallback_count = cards_per_player.get(num_players, 6)
        hands = []
        for _ in range(num_players):
            hands.append([self.deck.pop() for _ in range(fallback_count)])
        return hands


    def disable_all_buttons(self):
        for row in self.board_buttons:
            for button in row:
                button.setEnabled(False)
        self.restart_button.setVisible(True)
   
    def generate_random_board(self):
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Q', 'K', 'A']  # No Jacks here
        deck = []
        for _ in range(2):  # Two decks
            for suit in suits:
                for rank in ranks:
                    deck.append(f"{rank}{suit}")
        random.shuffle(deck)

        board_layout = [['' for _ in range(10)] for _ in range(10)]

        corners = [(0, 0), (0, 9), (9, 0), (9, 9)]
        for r, c in corners:
            board_layout[r][c] = 'Joker'

        deck_index = 0
        for r in range(10):
            for c in range(10):
                if (r, c) in corners:
                    continue
                board_layout[r][c] = deck[deck_index]
                deck_index += 1

        return board_layout
  
    def restart_game(self):
        self.scores = [0, 0]
        self.deck = []
        for _ in range(2):
            for suit in ['♠', '♥', '♦', '♣']:
                for rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']:
                    if rank == 'J':
                        if suit in ['♠', '♥']:
                            self.deck.append("1-Eyed Jack")
                        else:
                            self.deck.append("2-Eyed Jack")
                    else:
                        self.deck.append(f"{rank}{suit}")
        random.shuffle(self.deck)

        self.board_layout = self.generate_random_board()
        for r in range(10):
            for c in range(10):
                card = self.board_layout[r][c]
                btn = self.board_buttons[r][c]
                btn.setText(card)
                is_corner = (r, c) in self.corner_positions
                is_joker = card == "Joker"
                btn.setEnabled(not is_corner and not is_joker)
                style = ""
                if '♦' in card or '♥' in card:
                    style += "color: red;"
                else:
                    style += "color: black;"

                if is_joker or is_corner:
                    style += " background-color: lightgreen;"

                btn.setStyleSheet(style)
        if self.win_label:
            self.win_label.deleteLater()
            self.win_label = None
        if self.loss_label:
            self.loss_label.deleteLater()
            self.loss_label = None
        if self.draw_label:
            self.draw_label.deleteLater()
            self.draw_label = None

        self.hands = self.deal_cards(2)
        self.current_player = 0
        self.selected_card = None
        self.removal_mode = False
        self.status_label.setText("")
        self.restart_button.setVisible(True)
        self.help_button.setVisible(True)
        self.update_hand()
        self.ai_play_if_needed()

    def highlight_removable_chips(self):
        self.removable_positions.clear()
        opponent_chip = '🟢' if self.current_player == 0 else '🔵'
        for r in range(10):
            for c in range(10):
                btn = self.board_buttons[r][c]
                if btn.text() == opponent_chip and (r, c) not in self.corner_positions:
                    btn.setStyleSheet(btn.styleSheet() + "border: 2px solid yellow;")
                    btn.setEnabled(True)
                    self.removable_positions.add((r, c))

    def clear_highlights(self):
        for r in range(10):
            for c in range(10):
                btn = self.board_buttons[r][c]
                btn.setStyleSheet(btn.styleSheet().replace("border: 2px solid yellow;", ""))
                if btn.text() in ['🔵', '🟢']:
                    btn.setEnabled(False)
        self.removable_positions.clear()

    def end_turn(self):
        self.hands[self.current_player].remove(self.selected_card)
        self.selected_card = None
        if self.deck:
            self.hands[self.current_player].append(self.deck.pop())
            self.current_player = 1 - self.current_player
            self.update_hand()
            self.ai_play_if_needed()
        else:
            if self.draw_label is None:
               self.play_draw_animation()
   
    def play_draw_animation(self):
        if self.draw_label is not None:
            self.draw_label.deleteLater()
        self.draw_label = QLabel("🤝 Match Drawn 🤝")
        self.draw_label.setFont(QFont("Arial", 22, QFont.Bold))
        self.draw_label.setStyleSheet("color: orange; background-color: black;")
        self.draw_label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.draw_label)

    def ai_play_if_needed(self):
        if self.vs_ai and self.current_player == 1:
            QTimer.singleShot(700, self.ai_take_turn)

    def ai_take_turn(self):
        hand = self.hands[self.current_player]
        
        if self.ai_difficulty == "Easy":
            random.shuffle(hand)
        elif self.ai_difficulty == "Medium":
            hand.sort()
            
        if self.ai_difficulty == "Hard":
        # Try smart move first
            for card in hand:
                for r in range(10):
                    for c in range(10):
                        button = self.board_buttons[r][c]
                        board_card = self.board_layout[r][c]
                        if card == "2-Eyed Jack" or card == board_card:
                            if button.isEnabled() and self.check_possible_sequence(r, c, '🟢'):
                                self.selected_card = card
                                self.place_marker(r, c)
                                return

            for card in hand:
                if card == "1-Eyed Jack":
                    removable = []
                    for r in range(10):
                        for c in range(10):
                            btn = self.board_buttons[r][c]
                            opponent_chip = '🔵'
                            if btn.text() == opponent_chip and (r, c) not in self.corner_positions:
                                removable.append((r, c))
                    if removable:
                        r, c = random.choice(removable)
                        self.selected_card = card
                        self.perform_removal(r, c)
                        return

    # Fallback normal move for all difficulties (common logic)
        for card in hand:
            for r in range(10):
                for c in range(10):
                    button = self.board_buttons[r][c]
                    board_card = self.board_layout[r][c]
                    if not button.isEnabled() and (r, c) not in self.corner_positions:
                        continue
                    if card == "2-Eyed Jack" or card == board_card:
                        self.selected_card = card
                        self.place_marker(r, c)
                        return
                    if card == "1-Eyed Jack":
                        removable = []
                        for i in range(10):
                            for j in range(10):
                                btn = self.board_buttons[i][j]
                                opponent_chip = '🔵'
                                if btn.text() == opponent_chip and (i, j) not in self.corner_positions:
                                    removable.append((i, j))
                        if removable:
                            r, c = random.choice(removable)
                            self.selected_card = card
                            self.perform_removal(r, c)
                            return

        if not self.makeRandomMove():
            self.current_player = 1 - self.current_player
            self.update_hand()

    def perform_removal(self, row, col):
        button = self.board_buttons[row][col]
        original_card = self.board_layout[row][col]
        button.setText(original_card)

        if '♦' in original_card or '♥' in original_card:
            button.setStyleSheet("color: red;")
        else:
            button.setStyleSheet("color: black;")
            
        button.setEnabled(True)  # Make it playable again

        self.hands[self.current_player].remove(self.selected_card)
        self.selected_card = None
        self.removal_mode = False
        self.clear_highlights()
        self.status_label.setText(f"{self.players[self.current_player]} removed opponent's chip!")

        if self.deck:
            self.hands[self.current_player].append(self.deck.pop())
        self.current_player = 1 - self.current_player
        self.update_hand()
        self.ai_play_if_needed()

    def has_valid_moves(self, player_index):
        hand = self.hands[player_index]
        opponent_chip = '🔵' if player_index == 1 else '🟢'
        for card in hand:
            for r in range(10):
                for c in range(10):
                    button = self.board_buttons[r][c]
                    board_card = self.board_layout[r][c]
                    if card == "2-Eyed Jack" and button.isEnabled():
                        return True
                    if card == "1-Eyed Jack" and button.text() == opponent_chip and (r, c) not in self.corner_positions:
                        return True
                    if card == board_card and button.isEnabled():
                        return True
        return False

    def regenerate_full_deck(self):
        self.deck = []
        for _ in range(2):  # Two full decks
            for suit in ['♠', '♥', '♦', '♣']:
                for rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']:
                    if rank == 'J':
                        if suit in ['♠', '♥']:
                            self.deck.append("1-Eyed Jack")
                        else:
                            self.deck.append("2-Eyed Jack")
                    else:
                        self.deck.append(f"{rank}{suit}")
        random.shuffle(self.deck)


from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QComboBox,
    QPushButton, QStackedLayout, QWidget
)
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt

class HelpDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📖 How to Play - Sequence Game")
        self.setFixedSize(500, 600)

        layout = QVBoxLayout()

        guide = """
🎯 WELCOME TO SEQUENCE - THE STRATEGIC CARD & CHIPS GAME! 🎯

🧩 OBJECTIVE:
Your mission is to form 2 separate sequences(each with 5 chips in a row) before your opponent does.

Each sequence can be made horizontally, vertically, or diagonally. Think like a mix of cards + tic-tac-toe + chess!


🎮 HOW TO PLAY - YOUR TURN:
1️⃣ Choose a card from your hand (you get 7 at the start).
2️⃣ Find a matching card on the board and place your chip there.
3️⃣ The spot gets locked and cannot be used again.

💡 Don’t worry — each card appears twice on the board!

🎴 SPECIAL JACK CARDS:
🃏 Two-Eyed Jack → Wildcard! Place your chip on ANY open space.
🃏 One-Eyed Jack → Sneaky! Remove an opponent’s chip from the board.

✨ Pro Tip: Use these wisely to build your sequences or block your rival!


🏆 HOW TO WIN:
✅ First player to complete two 5-chip sequences wins the game.
🤝 If no valid moves remain for both players, it's a draw.


🃏 ABOUT THE BOARD:
- Corners (marked as “Joker”) are wild — they count for both players.
- Each card on the board is from a double deck (excluding Jacks).

🟦 Player 1 uses: 🔵 Blue chips  
🟩 Player 2 / AI uses: 🟢 Green chips  
🔴 Red chips represent completed sequences  
🎴 AI cards are hidden


🧠 AI DIFFICULTY LEVELS:
• Easy: Makes random moves — perfect for beginners.
• Medium: Picks better options, still casual.
• Hard: Thinks ahead, makes smart plays, tries to block & win.


💡 STRATEGY TIPS:

🎯 1. Control the Center:
• Owning center spaces gives you the most flexibility to build sequences in any direction.
• It also helps block your opponent's potential sequences.

🧠 2. Think Ahead:
• Don’t just play your card — plan your next 2–3 moves in advance.
• Always ask: “Does this move help me or help block my opponent?”

🚫 3. Block Aggressively:
• Notice your opponent forming a line of 2 or 3 chips?
Use a One-Eyed Jack to remove their chip or place yours to interrupt their pattern.

🃏 4. Use Jacks Wisely:
• Two-Eyed Jack can be your winning move — save it for the perfect moment.
• One-Eyed Jack is best used when your opponent is close to completing a sequence.

🔁 5. Use Duplicates to Your Advantage:
• Each board card exists twice. If one is taken, try for the other!
• Also, try placing where both copies** of a card are still available to maximize flexibility.

👀 6. Watch for Overlaps:
• You can share chips between two sequences.
• A great move is one that contributes to two different lines at once.

🧱 7. Don't Waste Good Cards:
• Just because you can play a card doesn’t mean you should. 
• Sometimes it’s smarter to wait and block instead.

🎴 8. Adapt to the AI:
• Easy AI makes random plays — go aggressive.
• Medium AI blocks sometimes — play balanced.
• Hard AI is smart — mix offense with defense, and use Jacks tactically.

👫 9. Learn Your Opponent:
• Human players may follow patterns. If they always go for the corners first, stop them.
• Watch what cards they don’t play — they may be saving a Jack!

🏁 10. Finish Strong:
• Don’t get distracted by small plays near the end.
• Focus on completing sequences quickly once you're close.

🧩 Bonus Tip:
• Practice! The more you play, the better you’ll recognize patterns and trap opportunities.


🚀 GOOD LUCK, HAVE FUN, AND PLAY SMART!
"""
        text = QTextEdit()
        text.setReadOnly(True)
        text.setPlainText(guide)
        text.setFont(QFont("Arial", 11))
        layout.addWidget(text)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)
class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sequence Game")
        self.setFixedSize(350, 450)  # Compact size

        self.stack = QStackedLayout()

        self.init_welcome_page()
        self.init_setup_page()

        container = QWidget()
        container.setLayout(self.stack)
        main_layout = QVBoxLayout()
        main_layout.addWidget(container)
        self.setLayout(main_layout)

    def init_welcome_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        image = QLabel()
        pixmap = QPixmap("sequencebanner.png")  
        if not pixmap.isNull():
            image.setPixmap(pixmap.scaledToWidth(300))
            image.setPixmap(pixmap.scaled(image.width(), image.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            image.setPixmap(pixmap) 
        else:
            image.setText("Image not found.")
        image.setAlignment(Qt.AlignCenter)
        layout.addWidget(image)

        # Play button
        play_button = QPushButton("🎮 Play")
        play_button.setFont(QFont("Arial", 12, QFont.Bold))
        play_button.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        layout.addWidget(play_button)

        page.setLayout(layout)
        self.stack.addWidget(page)

    def init_setup_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        self.p1_name = QLineEdit()
        self.p1_name.setPlaceholderText("Player 1 Name")
        layout.addWidget(QLabel("Player 1 Name:"))
        layout.addWidget(self.p1_name)

        self.ai_checkbox = QCheckBox("Play vs AI?")
        self.ai_checkbox.stateChanged.connect(self.toggle_ai_fields)
        layout.addWidget(self.ai_checkbox)

        self.p2_name = QLineEdit()
        self.p2_name.setPlaceholderText("Player 2 Name")
        layout.addWidget(QLabel("Player 2 Name:"))
        layout.addWidget(self.p2_name)

        self.difficulty = QComboBox()
        self.difficulty.addItems(["Easy", "Medium", "Hard"])
        layout.addWidget(QLabel("AI Difficulty:"))
        layout.addWidget(self.difficulty)

        start_button = QPushButton("🚀 Start Game")
        start_button.clicked.connect(self.accept)
        layout.addWidget(start_button)

        page.setLayout(layout)
        self.stack.addWidget(page)

        self.toggle_ai_fields()  # Initial state

    def toggle_ai_fields(self):
        ai_enabled = self.ai_checkbox.isChecked()
        self.p2_name.setEnabled(not ai_enabled)
        self.difficulty.setEnabled(ai_enabled)

    def get_settings(self):
        p1 = self.p1_name.text() or "Player 1"
        p2 = "AI" if self.ai_checkbox.isChecked() else (self.p2_name.text() or "Player 2")
        return {
            'players': [p1, p2],
            'vs_ai': self.ai_checkbox.isChecked(),
            'ai_difficulty': self.difficulty.currentText()
        }

def main():
    app = QApplication(sys.argv)
    settings_dialog = SettingsDialog()
    if settings_dialog.exec():
        settings = settings_dialog.get_settings()
        game = SequenceGameGUI(settings)
        game.show()
        sys.exit(app.exec())

if __name__ == '__main__':
    main()
