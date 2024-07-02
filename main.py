import pygame
import sys
import random
import asyncio


pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Disc Golf Wolf Game")
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)
big_font = pygame.font.Font(None, 56)
clock = pygame.time.Clock()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Game states
ASK_NUM_PLAYERS = "ask_num_players"
ASK_PLAYER_NAMES = "ask_player_names"
WAIT_READY = "wait_ready"
SELECT_WOLF = "select_wolf"
CHOOSE_PARTNER = "choose_partner"
ASK_WIN = "ask_win"
SHOW_RESULTS = "show_results"






# Questions
question_num_players = "How many players?"
question_player_name = lambda player: f"What is the name of player {player}?"
question_ready = "              Are you ready? Press Enter!"
question_choose_partner = "Wolf choose a partner or yourself (number 1 to {num_players}) "
question_won = "Did the Wolf succeed? (Y/N)"
question_replay = "Play again ? (Y/N)"



def display_question(screen, question, user_input, show_cursor):
    #screen.fill(WHITE)
    question_surface = font.render(question, True, BLACK)
    input_surface = font.render(user_input + ('|' if show_cursor else ''), True, BLACK)
    screen.blit(question_surface, (50, 50))
    screen.blit(input_surface, (50, 100))
    pygame.display.flip()

def display_players(screen, players):
    #screen.fill(WHITE)
    header_surface = font.render(f"{'Number':<10}{'Name':<20}{'Score':<10}", True, BLACK)
    screen.blit(header_surface, (250, 100))

    y_offset = 150
    for player in players:
        number_surface = font.render(str( player['number']), True, RED)
        screen.blit(number_surface, (150, y_offset))

        player_surface = font.render(player['name'], True, BLACK)
        screen.blit(player_surface, (250, y_offset))

        score_surface = font.render(str(player['score'])+("         *WOLF*     " if player['wolf'] else ""), True, BLACK)
        screen.blit(score_surface, (550, y_offset))

        y_offset += 40

    pygame.display.flip()

def capture_input(event, user_input):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN:
            return user_input, True
        elif event.key == pygame.K_BACKSPACE:
            user_input = user_input[:-1]
        else:
            user_input += event.unicode
    return user_input, False

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
    # Move the last player to the first position and shift others down by one
    players.insert(0, players.pop())
    for idx, player in enumerate(players):
        player['number'] = idx + 1
    players[-1]['wolf'] = True  # Assign last player as Wolf
    for player in players[:-1]:
        player['wolf'] = False

def get_winners(players): # verify if there is a tie in between players
    if not players:
        return []

    max_score = max(p["score"] for p in players)
    winners = [p for p in players if p["score"] == max_score]
    return winners

def display_turn(screen, turn):
    turn_surface = small_font.render(f"Hole: {turn}", True, BLACK)
    screen.blit(turn_surface, (10, 10))

async def main():
    # Initial state
    state = ASK_NUM_PLAYERS

    # Initialize variables
    num_players = 0
    current_player = 1
    players = []
    turn = 1
    user_input = ""
    show_cursor = True
    cursor_time = 0
    done = False # if True the game ends
    input_complete = False # if True the user hit enter to finish his input
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            
            if state == ASK_NUM_PLAYERS:
                screen.fill(WHITE)
                display_question(screen, question_num_players, user_input, show_cursor)
                user_input, input_complete = capture_input(event, user_input)
                if input_complete:
                    num_players = int(user_input)
                    input_complete = False
                    state = ASK_PLAYER_NAMES
                    user_input = ""  # Clear user_input after saving
                    players = []
                    current_player = 1

            elif state == ASK_PLAYER_NAMES:
                screen.fill(WHITE)
                display_question(screen, question_player_name(current_player), user_input, show_cursor)
                user_input, input_complete = capture_input(event, user_input)
                if input_complete:
                    players.append({'number': current_player, 'name': user_input,'score': 0, 'wolf': False,'partner' : True })
                    user_input = ""  # Clear user_input after saving
                    input_complete = False
                    current_player += 1
                    if current_player > num_players:
                        random.shuffle(players)  # Randomize player order
                        players[-1]['wolf'] = True  # Assign last player as Wolf
                        # Assign numbers after shuffle
                        for idx, player in enumerate(players):
                            player['number'] = idx + 1
                        state = WAIT_READY

            elif state == WAIT_READY:
                screen.fill(WHITE)
                display_players(screen, players)
                display_question(screen, question_ready, "", show_cursor)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    state = CHOOSE_PARTNER
                    user_input = ""  # Clear user_input before next question

            elif state == CHOOSE_PARTNER:
                screen.fill(WHITE)
                display_turn(screen, turn)
                display_players(screen, players)
                display_question(screen, question_choose_partner.format(num_players=num_players), user_input, show_cursor)
                user_input, input_complete = capture_input(event, user_input)
                if input_complete:
                    partner_choice = int(user_input)
                    user_input = ""  # Clear user_input after saving
                    state = ASK_WIN
                    input_complete = False

            elif state == ASK_WIN:
                screen.fill(WHITE)
                display_players(screen, players)
                display_question(screen, question_won, user_input, show_cursor)
                user_input, input_complete = capture_input(event, user_input)
                if input_complete:
                    won = user_input.lower() == "y"
                    calculate_scores(players, num_players - 1, partner_choice, won)  # Always use last player as the wolf
                    user_input = ""
                    input_complete = False
                    turn += 1
                    if turn > 9:  # Assume 9 holes, adjust as needed
                        state = SHOW_RESULTS
                    else:
                        cycle_wolf(players)
                        state = CHOOSE_PARTNER
            elif state == SHOW_RESULTS:
                screen.fill(WHITE)
                
                winners = get_winners(players)
                
                if winners:
                    if len(winners) == 1:
                        Congrats_winner = f"Congratulations {winners[0]['name']}!"
                    else:
                        winner_names = ", ".join([winner['name'] for winner in winners])
                        Congrats_winner = f"Congratulations {winner_names}!"
                else:
                    Congrats_winner = "No players to display."
                
                display_players(screen, players)
                
                congrats_surface = big_font.render(Congrats_winner, True, RED)
                screen.blit(congrats_surface, (50, 450)) #congrats the winner(s)

                display_question(screen, question_replay, user_input, show_cursor) #ask for another game
                user_input, input_complete = capture_input(event, user_input)
                if input_complete:
                    if user_input.lower() == "y":
                        state = ASK_NUM_PLAYERS
                        user_input = ""
                    else:
                        done = True

        cursor_time += clock.get_time()
        if cursor_time >= 500:  # Toggle cursor every 500ms
            show_cursor = not show_cursor
            cursor_time = 0
            
        pygame.display.flip()
        clock.tick(30)
    await asyncio.sleep(0)

    pygame.quit()
    sys.exit()
    

asyncio.run(main())
