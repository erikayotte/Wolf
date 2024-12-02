import streamlit as st
import random

# Define game states
ASK_NUM_PLAYERS = "ask_num_players"
ASK_PLAYER_NAMES = "ask_player_names"
WAIT_READY = "wait_ready"
CHOOSE_PARTNER = "choose_partner"
ASK_WIN = "ask_win"
SHOW_RESULTS = "show_results"

# Initialize session state variables
if "state" not in st.session_state:
    st.session_state.state = ASK_NUM_PLAYERS
if "num_players" not in st.session_state:
    st.session_state.num_players = 0
if "players" not in st.session_state:
    st.session_state.players = []
if "turn" not in st.session_state:
    st.session_state.turn = 1
if "wolf_index" not in st.session_state:
    st.session_state.wolf_index = -1

# Game logic functions
def calculate_scores(players, wolf_index, partner_choice, won):
    wolf = players[wolf_index]
    rest3 = [player for idx, player in enumerate(players) if idx != wolf_index and player['number'] != partner_choice]

    if partner_choice == wolf['number']:
        if won:
            wolf['score'] += 4
        else:
            for player in rest3:
                player['score'] += 1
    else:
        partner = players[partner_choice - 1]
        if won:
            wolf['score'] += 2
            partner['score'] += 2
        else:
            for player in rest3:
                player['score'] += 2

def cycle_wolf(players):
    players.insert(0, players.pop())
    for idx, player in enumerate(players):
        player['number'] = idx + 1
    players[-1]['wolf'] = True
    for player in players[:-1]:
        player['wolf'] = False

def get_winners(players):
    max_score = max(p["score"] for p in players)
    return [p for p in players if p["score"] == max_score]

# Main logic
if st.session_state.state == ASK_NUM_PLAYERS:
    st.title("Disc Golf Wolf Game")
    st.session_state.num_players = st.number_input("How many players?", min_value=2, step=1)
    if st.button("Next"):
        st.session_state.players = []
        st.session_state.state = ASK_PLAYER_NAMES

elif st.session_state.state == ASK_PLAYER_NAMES:
    st.title("Enter Player Names")
    for i in range(1, st.session_state.num_players + 1):
        name = st.text_input(f"Player {i} Name:", key=f"player_name_{i}")
        if len(st.session_state.players) < st.session_state.num_players:
            st.session_state.players.append({"number": i, "name": name, "score": 0, "wolf": False})
    if st.button("Start Game"):
        random.shuffle(st.session_state.players)
        st.session_state.players[-1]['wolf'] = True
        st.session_state.state = WAIT_READY

elif st.session_state.state == WAIT_READY:
    st.title("Ready to Start")
    st.write("Players:")
    for player in st.session_state.players:
        st.write(f"{player['number']}. {player['name']} (Score: {player['score']})")
    if st.button("Ready"):
        st.session_state.state = CHOOSE_PARTNER

elif st.session_state.state == CHOOSE_PARTNER:
    st.title(f"Hole {st.session_state.turn}")
    wolf = [p for p in st.session_state.players if p['wolf']][0]
    st.write(f"The Wolf is: {wolf['name']}")
    partner_choice = st.number_input(
        f"Choose a partner (1-{st.session_state.num_players})", min_value=1, max_value=st.session_state.num_players
    )
    if st.button("Submit"):
        st.session_state.partner_choice = partner_choice
        st.session_state.state = ASK_WIN

elif st.session_state.state == ASK_WIN:
    won = st.radio("Did the Wolf succeed?", options=["Yes", "No"])
    if st.button("Submit"):
        calculate_scores(
            st.session_state.players,
            st.session_state.num_players - 1,
            st.session_state.partner_choice,
            won == "Yes"
        )
        st.session_state.turn += 1
        if st.session_state.turn > 9:
            st.session_state.state = SHOW_RESULTS
        else:
            cycle_wolf(st.session_state.players)
            st.session_state.state = CHOOSE_PARTNER

elif st.session_state.state == SHOW_RESULTS:
    st.title("Game Results")
    winners = get_winners(st.session_state.players)
    if winners:
        st.write("Congratulations to the winner(s):")
        for winner in winners:
            st.write(f"{winner['name']} with {winner['score']} points!")
    else:
        st.write("No winners this time!")
    if st.button("Play Again"):
        st.session_state.state = ASK_NUM_PLAYERS
        st.session_state.turn = 1
        st.session_state.players = []
