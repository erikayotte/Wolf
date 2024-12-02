import streamlit as st

# Define constants for game states
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
if "current_player" not in st.session_state:
    st.session_state.current_player = 1
if "players" not in st.session_state:
    st.session_state.players = []
if "turn" not in st.session_state:
    st.session_state.turn = 1
if "partner_choice" not in st.session_state:
    st.session_state.partner_choice = None

def calculate_scores(players, wolf_index, partner_choice, won):
    wolf = players[wolf_index]
    rest3 = [player for idx, player in enumerate(players) if idx != wolf_index and player['number'] != partner_choice]

    if partner_choice == wolf['number']:
        # Wolf plays alone
        if won:
            wolf['score'] += 4  # Wolf gets 4 points if they win alone
        else:
            for player in rest3:
                player['score'] += 1  # Other players get 1 point each if wolf loses alone
    else:
        # Wolf chooses a partner
        partner = players[partner_choice - 1]
        if won:
            wolf['score'] += 2  # Wolf gets 2 points if they win with a partner
            partner['score'] += 2  # Partner gets 2 points
        else:
            for player in rest3:
                if player != partner:
                    player['score'] += 2  # Other players get 2 points each if wolf and partner lose

def cycle_wolf(players):
    players.insert(0, players.pop())  # Move the last player to the first position
    for idx, player in enumerate(players):
        player['number'] = idx + 1
    players[-1]['wolf'] = True  # Assign the last player as the new Wolf
    for player in players[:-1]:
        player['wolf'] = False

def get_winners(players):
    if not players:
        return []
    max_score = max(p["score"] for p in players)
    return [p for p in players if p["score"] == max_score]

# Main game loop
if st.session_state.state == ASK_NUM_PLAYERS:
    st.title("Disc Golf Wolf")
    st.session_state.num_players = st.selectbox("Select number of players:", list(range(1, 9)))
    if st.button("Next"):
        st.session_state.state = ASK_PLAYER_NAMES
        st.session_state.players = []
        st.session_state.current_player = 1

elif st.session_state.state == ASK_PLAYER_NAMES:
    st.title("Enter Player Names")
    if st.session_state.current_player <= st.session_state.num_players:
        name = st.text_input(f"Enter name for player {st.session_state.current_player}:")
        if st.button("Submit"):
            st.session_state.players.append({
                "number": st.session_state.current_player,
                "name": name,
                "score": 0,
                "wolf": False,
            })
            st.session_state.current_player += 1
    else:
        st.session_state.players[-1]["wolf"] = True  # Last player starts as Wolf
        st.session_state.state = WAIT_READY

elif st.session_state.state == WAIT_READY:
    st.title("Players Ready")
    st.write("Players:")
    for player in st.session_state.players:
        st.write(f"{player['number']}: {player['name']} (Score: {player['score']})")
    if st.button("Start Game"):
        st.session_state.state = CHOOSE_PARTNER

elif st.session_state.state == CHOOSE_PARTNER:
    st.title(f"Hole {st.session_state.turn}")
    wolf = [p for p in st.session_state.players if p['wolf']][0]
    st.write(f"The Wolf is: {wolf['name']}")

    # Dropdown to choose a partner by name
    partner_choice = st.selectbox(
        "Choose a partner (or yourself):",
        options=[player['name'] for player in st.session_state.players],
        index=st.session_state.players.index(wolf)  # Default to the wolf themselves
    )

    if st.button("Submit"):
        # Find the selected partner's number from their name
        partner_index = next(
            (idx for idx, player in enumerate(st.session_state.players) if player['name'] == partner_choice), 
            None
        )
        st.session_state.partner_choice = partner_index + 1  # Store the partner's number
        st.session_state.state = ASK_WIN

elif st.session_state.state == ASK_WIN:
    st.title("Did the Wolf Win?")
    won = st.radio("Select the outcome:", ["Yes", "No"])
    if st.button("Submit"):
        wolf_index = next(idx for idx, player in enumerate(st.session_state.players) if player["wolf"])
        calculate_scores(st.session_state.players, wolf_index, st.session_state.partner_choice, won == "Yes")
        st.session_state.turn += 1
        if st.session_state.turn > 9:  # End after 9 holes
            st.session_state.state = SHOW_RESULTS
        else:
            cycle_wolf(st.session_state.players)
            st.session_state.state = CHOOSE_PARTNER

elif st.session_state.state == SHOW_RESULTS:
    st.title("Game Over")
    winners = get_winners(st.session_state.players)
    if winners:
        if len(winners) == 1:
            st.write(f"Congratulations, {winners[0]['name']}! You won!")
        else:
            winner_names = ", ".join([winner["name"] for winner in winners])
            st.write(f"Congratulations, {winner_names}! You all won!")
    else:
        st.write("No winners this time.")
    if st.button("Play Again"):
        st.session_state.state = ASK_NUM_PLAYERS
        st.session_state.turn = 1
        for player in st.session_state.players:
            player["score"] = 0
