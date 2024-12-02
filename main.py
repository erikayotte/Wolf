import streamlit as st

# Define constants for game states
MENU = "menu"
RULES = "rules"
ASK_NUM_PLAYERS = "ask_num_players"
ASK_PLAYER_NAMES = "ask_player_names"
WAIT_READY = "wait_ready"
CHOOSE_PARTNER = "choose_partner"
ASK_WIN = "ask_win"
SHOW_RESULTS = "show_results"

# Initialize session state variables
if "state" not in st.session_state:
    st.session_state.state = MENU
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

# After player registration is complete, display scores:
def display_scores():
    st.write("### Scores:")
    for player in st.session_state.players:
        if "name" in player and player["name"]:  # Ensure player names are valid
            st.write(f"# {player['name']}: {player['score']}")
        else:
            st.write(f"# Joueurs # {player['number']}: Inconnu (Score: {player['score']})")
            
# Main game loop
if st.session_state.state == MENU:
    st.title("Disc Golf Wolf")
    choice = st.radio("Choisir une option :", ["Enregistrer les joueurs", "Réglements"])
    if st.button("Débuter"):
        if choice == "Enregistrer les joueurs":
            st.session_state.state = ASK_NUM_PLAYERS
        elif choice == "Réglements":
            st.session_state.state = RULES

elif st.session_state.state == RULES:
    st.title("Réglements")
    st.write("Les réglements seront expliqués ici !")
    if st.button("Retour au menu"):
        st.session_state.state = MENU

elif st.session_state.state == ASK_NUM_PLAYERS:
    st.title("Disc Golf Wolf")
    st.session_state.num_players = st.selectbox("Choisir le nombre de joueurs :", list(range(1, 9)))
    if st.button("Suivant"):
        st.session_state.state = ASK_PLAYER_NAMES
        st.session_state.players = []
        st.session_state.current_player = 1

elif st.session_state.state == ASK_PLAYER_NAMES:
    st.title("Entrer le nom des joueurs")
    
    if st.session_state.current_player <= st.session_state.num_players:
        # Text input for the current player's name
        name = st.text_input(
            f"Entrer le nom du joueur #{st.session_state.current_player}:",
            key=f"name_input_{st.session_state.current_player}"  # Unique key for each player
        )
        
        # Submit button for each player
        if st.button("Soumettre", key=f"submit_button_{st.session_state.current_player}"):
            if name.strip():  # Ensure name is not empty
                st.session_state.players.append({
                    "number": st.session_state.current_player,
                    "name": name,
                    "score": 0,
                    "wolf": False,
                })
                st.session_state.current_player += 1  # Move to the next player
            else:
                st.warning("Entrer un nom valide.")
    
    # Once all players are registered, assign the last player as the wolf and move to WAIT_READY
    if st.session_state.current_player > st.session_state.num_players:
        # Assign the last player as the initial wolf
        st.session_state.players[-1]["wolf"] = True
        # Set state to WAIT_READY so that the Start Game button is shown
        st.session_state.state = WAIT_READY

elif st.session_state.state == WAIT_READY:
    st.title("Joueurs prêts")
    
    # Show the start button only once all players are ready
    if st.button("Démarrer le jeu"):
        st.session_state.state = CHOOSE_PARTNER

elif st.session_state.state == CHOOSE_PARTNER:
    st.title(f"Trous # {st.session_state.turn}")
    wolf = [p for p in st.session_state.players if p['wolf']][0]
    st.write(f"Le wolf est : {wolf['name']}")

    partner_choice = st.selectbox(
        "Choisissez un partenaire ou vous-même :",
        options=[player['name'] for player in st.session_state.players],
        index=st.session_state.players.index(wolf)  # Default to the wolf themselves
    )

    if st.button("Soumettre"):
        partner_index = next(
            (idx for idx, player in enumerate(st.session_state.players) if player['name'] == partner_choice), 
            None
        )
        st.session_state.partner_choice = partner_index + 1  # Store the partner's number
        st.session_state.state = ASK_WIN

elif st.session_state.state == ASK_WIN:
    st.title("Est-ce que le Wolf a réussi ?")
    won = st.radio("Select the outcome:", ["Oui", "Non"])
    if st.button("Soumettre"):
        wolf_index = next(idx for idx, player in enumerate(st.session_state.players) if player["wolf"])
        calculate_scores(st.session_state.players, wolf_index, st.session_state.partner_choice, won == "Oui")
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
            st.write(f"Félicitations, {winners[0]['name']}, vous avez gagné !")
        else:
            winner_names = ", ".join([winner["name"] for winner in winners])
            st.write(f"Félicitations, {winner_names}! vous avez gagnés !")
    else:
        st.write("Aucun gagnant !? incroyable")
    if st.button("Jouez encore ?"):
        st.session_state.state = MENU
        st.session_state.turn = 1
        for player in st.session_state.players:
            player["score"] = 0

# Display scores after all players are registered
if st.session_state.state not in {MENU, RULES, ASK_NUM_PLAYERS, ASK_PLAYER_NAMES, WAIT_READY}:
    display_scores()
