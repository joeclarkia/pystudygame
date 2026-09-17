
import sys
import csv
import random
import multiprocessing

import pygame
import pyttsx3


# ============================================================
# Configuration
# ============================================================

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 650
FPS = 60

BACKGROUND = (245, 245, 245)
TEXT_COLOR = (30, 30, 30)
INPUT_BACKGROUND = (255, 255, 255)
INPUT_BORDER = (80, 80, 80)

GREEN = (40, 150, 70)
RED = (190, 50, 50)
BLUE = (60, 110, 190)
GRAY = (120, 120, 120)
LIGHT_GRAY = (220, 220, 220)
DARK_GRAY = (70, 70, 70)

BUTTON_WIDTH = 150
BUTTON_HEIGHT = 48


# ============================================================
# TEXT-TO-SPEECH
# ============================================================
#
# A separate process is used for every speech request.
#
# This avoids problems that pyttsx3 can have when a single
# engine is repeatedly stopped and restarted on Windows.
#
# A new round uses speak_word_and_sentence(), which explicitly
# waits for the word to finish before speaking the sentence.
#
# Button presses use speak(), which speaks a single item.
# ============================================================

speech_process = None


def speak_worker(text):
    """
    Speak one piece of text.
    """

    try:

        engine = pyttsx3.init()

        engine.setProperty(
            "rate",
            165
        )

        engine.setProperty(
            "volume",
            1.0
        )

        engine.say(text)

        engine.runAndWait()

        engine.stop()

    except Exception as e:

        print(
            "Text-to-speech error:",
            e
        )


def speak_word_and_sentence_worker(
    word,
    sentence
):
    """
    Speak the word first, wait for it to finish,
    then speak the sentence.
    """

    try:

        engine = pyttsx3.init()

        engine.setProperty(
            "rate",
            165
        )

        engine.setProperty(
            "volume",
            1.0
        )

        # ----------------------------------------------------
        # Speak the word by itself.
        # ----------------------------------------------------

        engine.say(word)

        engine.runAndWait()

        # ----------------------------------------------------
        # The word has now finished.
        #
        # Give the speech system a tiny pause before starting
        # the sentence.
        # ----------------------------------------------------

        # A small pause makes the separation especially clear.
        import time
        time.sleep(0.35)

        # ----------------------------------------------------
        # Now speak the sentence.
        # ----------------------------------------------------

        engine.say(sentence)

        engine.runAndWait()

        engine.stop()

    except Exception as e:

        print(
            "Text-to-speech error:",
            e
        )


def stop_speech():
    """
    Stop any currently running speech process.
    """

    global speech_process

    if speech_process is not None:

        if speech_process.is_alive():

            try:

                speech_process.terminate()

                speech_process.join(
                    timeout=0.5
                )

            except Exception:
                pass

        speech_process = None


def speak(text):
    """
    Speak a single piece of text.
    """

    global speech_process

    stop_speech()

    speech_process = multiprocessing.Process(
        target=speak_worker,
        args=(text,)
    )

    speech_process.daemon = True

    speech_process.start()


def speak_word_and_sentence(
    word,
    sentence
):
    """
    Speak the word, then the sentence.
    """

    global speech_process

    stop_speech()

    speech_process = multiprocessing.Process(
        target=speak_word_and_sentence_worker,
        args=(
            word,
            sentence
        )
    )

    speech_process.daemon = True

    speech_process.start()


# ============================================================
# Load input file
# ============================================================

def load_words(filename):

    words = []

    try:

        with open(
            filename,
            "r",
            encoding="utf-8",
            newline=""
        ) as f:

            reader = csv.reader(f)

            for line_number, row in enumerate(
                reader,
                start=1
            ):

                if not row:
                    continue

                if len(row) < 2:

                    print(
                        f"Warning: line {line_number} "
                        f"does not contain a word and sentence."
                    )

                    continue

                word = row[0].strip()
                sentence = row[1].strip()

                if not word:
                    continue

                words.append({
                    "word": word,
                    "sentence": sentence
                })

    except FileNotFoundError:

        print(
            f"Error: Could not find input file: {filename}"
        )

        sys.exit(1)

    except Exception as e:

        print(
            f"Error reading input file: {e}"
        )

        sys.exit(1)

    if not words:

        print(
            "Error: No valid words were found."
        )

        sys.exit(1)

    return words


# ============================================================
# Drawing functions
# ============================================================

def draw_text(
    surface,
    text,
    font,
    color,
    x,
    y,
    center=False
):

    rendered = font.render(
        text,
        True,
        color
    )

    if center:

        rect = rendered.get_rect(
            center=(x, y)
        )

    else:

        rect = rendered.get_rect(
            topleft=(x, y)
        )

    surface.blit(
        rendered,
        rect
    )

    return rect


def draw_button(
    surface,
    rect,
    text,
    font,
    mouse_pos,
    focused=False
):
    """
    Draw a button.

    If focused=True, draw a blue focus outline so the user
    can see that pressing ENTER will activate this button.
    """

    if rect.collidepoint(mouse_pos):

        color = (180, 200, 230)

    else:

        color = LIGHT_GRAY

    pygame.draw.rect(
        surface,
        color,
        rect,
        border_radius=8
    )

    pygame.draw.rect(
        surface,
        DARK_GRAY,
        rect,
        2,
        border_radius=8
    )

    # Keyboard focus indicator.
    if focused:

        focus_rect = rect.inflate(
            8,
            8
        )

        pygame.draw.rect(
            surface,
            BLUE,
            focus_rect,
            3,
            border_radius=10
        )

    draw_text(
        surface,
        text,
        font,
        TEXT_COLOR,
        rect.centerx,
        rect.centery,
        center=True
    )


# ============================================================
# Main game
# ============================================================

def main():

    if len(sys.argv) != 2:

        print(
            "Usage:"
        )

        print(
            "    python spelling_game.py words.csv"
        )

        sys.exit(1)

    filename = sys.argv[1]

    words = load_words(
        filename
    )

    pygame.init()

    screen = pygame.display.set_mode(
        (
            WINDOW_WIDTH,
            WINDOW_HEIGHT
        )
    )

    pygame.display.set_caption(
        "Spelling Game"
    )

    clock = pygame.time.Clock()

    # ========================================================
    # Fonts
    # ========================================================

    title_font = pygame.font.Font(
        None,
        38
    )

    large_font = pygame.font.Font(
        None,
        32
    )

    normal_font = pygame.font.Font(
        None,
        25
    )

    small_font = pygame.font.Font(
        None,
        20
    )

    # ========================================================
    # Randomize word order
    #
    # Every word will be presented exactly once.
    # ========================================================

    word_order = list(
        range(len(words))
    )

    random.shuffle(
        word_order
    )

    current_position = 0

    current_item = None

    # ========================================================
    # Results
    # ========================================================

    correct_words = []
    incorrect_words = []

    # ========================================================
    # Input
    # ========================================================

    user_input = ""

    input_active = True

    # ========================================================
    # Game state
    # ========================================================

    game_state = "spelling"

    result_message = ""
    result_color = TEXT_COLOR

    # ========================================================
    # Keyboard focus
    #
    # Possible values:
    #
    #   "input"
    #   "continue"
    #   None
    #
    # ========================================================

    keyboard_focus = "input"

    # ========================================================
    # Buttons
    # ========================================================

    speak_word_button = pygame.Rect(
        40,
        500,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )

    speak_sentence_button = pygame.Rect(
        205,
        500,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )

    give_up_button = pygame.Rect(
        370,
        500,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )

    continue_button = pygame.Rect(
        535,
        500,
        BUTTON_WIDTH,
        BUTTON_HEIGHT
    )

    # ========================================================
    # Input box
    # ========================================================

    input_rect = pygame.Rect(
        200,
        350,
        500,
        60
    )

    # ========================================================
    # Select next word
    # ========================================================

    def select_next_word():

        nonlocal current_position
        nonlocal current_item
        nonlocal user_input
        nonlocal game_state
        nonlocal result_message
        nonlocal result_color
        nonlocal input_active
        nonlocal keyboard_focus

        if current_position >= len(word_order):

            game_state = "finished"

            keyboard_focus = None

            return

        index = word_order[
            current_position
        ]

        current_item = words[index]

        current_position += 1

        user_input = ""

        result_message = ""

        result_color = TEXT_COLOR

        game_state = "spelling"

        # ----------------------------------------------------
        # New round always starts with input focused.
        # ----------------------------------------------------

        input_active = True

        keyboard_focus = "input"

        # ----------------------------------------------------
        # Speak word by itself, then sentence.
        # ----------------------------------------------------

        speak_word_and_sentence(
            current_item["word"],
            current_item["sentence"]
        )

    # ========================================================
    # Start first round
    # ========================================================

    select_next_word()

    # ========================================================
    # Main loop
    # ========================================================

    running = True

    while running:

        mouse_pos = pygame.mouse.get_pos()

        # ====================================================
        # Events
        # ====================================================

        for event in pygame.event.get():

            # ------------------------------------------------
            # Window closed
            # ------------------------------------------------

            if event.type == pygame.QUIT:

                running = False

            # ------------------------------------------------
            # Keyboard
            # ------------------------------------------------

            elif event.type == pygame.KEYDOWN:

                # =================================================
                # ENTER
                # =================================================

                if event.key == pygame.K_RETURN:

                    # ---------------------------------------------
                    # Continue has keyboard focus
                    # ---------------------------------------------

                    if (
                        game_state == "result"
                        and keyboard_focus == "continue"
                    ):

                        if (
                            current_position
                            >= len(word_order)
                        ):

                            game_state = "finished"

                            keyboard_focus = None

                        else:

                            select_next_word()

                        continue

                    # ---------------------------------------------
                    # Input has keyboard focus
                    # ---------------------------------------------

                    if (
                        game_state == "spelling"
                        and keyboard_focus == "input"
                    ):

                        if user_input.strip() == "":
                            continue

                        answer = current_item["word"]

                        # -----------------------------------------
                        # Correct answer
                        # -----------------------------------------

                        if (
                            user_input.strip().lower()
                            == answer.lower()
                        ):

                            if answer not in correct_words:

                                correct_words.append(
                                    answer
                                )

                            result_message = (
                                "Correct!"
                            )

                            result_color = GREEN

                            game_state = "result"

                            # -------------------------------------
                            # Give Continue keyboard focus.
                            # -------------------------------------

                            keyboard_focus = "continue"

                            input_active = False

                            # Stop any speech that might still
                            # be playing.
                            stop_speech()

                        # -----------------------------------------
                        # Incorrect answer
                        # -----------------------------------------

                        else:

                            if answer not in incorrect_words:

                                incorrect_words.append(
                                    answer
                                )

                            result_message = (
                                "Not quite. Try again."
                            )

                            result_color = RED

                            # Keep focus on the spelling box.
                            keyboard_focus = "input"

                            input_active = True

                            user_input = ""

                        continue

                # =================================================
                # BACKSPACE
                # =================================================

                if (
                    event.key == pygame.K_BACKSPACE
                    and game_state == "spelling"
                    and keyboard_focus == "input"
                ):

                    user_input = (
                        user_input[:-1]
                    )

                    continue

                # =================================================
                # ESCAPE
                # =================================================

                if event.key == pygame.K_ESCAPE:

                    running = False

                    continue

                # =================================================
                # CHARACTER INPUT
                # =================================================

                if (
                    game_state == "spelling"
                    and keyboard_focus == "input"
                ):

                    if event.unicode:

                        user_input += (
                            event.unicode
                        )

            # ------------------------------------------------
            # Mouse
            # ------------------------------------------------

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button != 1:
                    continue

                # =================================================
                # HEAR WORD
                # =================================================

                if speak_word_button.collidepoint(
                    event.pos
                ):

                    if current_item is not None:

                        speak(
                            current_item["word"]
                        )

                # =================================================
                # HEAR SENTENCE
                # =================================================

                elif speak_sentence_button.collidepoint(
                    event.pos
                ):

                    if current_item is not None:

                        speak(
                            current_item["sentence"]
                        )

                # =================================================
                # GIVE UP
                # =================================================

                elif give_up_button.collidepoint(
                    event.pos
                ):

                    if game_state == "spelling":

                        answer = current_item["word"]

                        if answer not in incorrect_words:

                            incorrect_words.append(
                                answer
                            )

                        result_message = (
                            f"The word was: {answer}"
                        )

                        result_color = RED

                        game_state = "result"

                        # Give Continue keyboard focus.
                        keyboard_focus = "continue"

                        input_active = False

                        stop_speech()

                # =================================================
                # CONTINUE
                # =================================================

                elif continue_button.collidepoint(
                    event.pos
                ):

                    if game_state == "result":

                        if (
                            current_position
                            >= len(word_order)
                        ):

                            game_state = "finished"

                            keyboard_focus = None

                        else:

                            select_next_word()

                # =================================================
                # INPUT BOX
                # =================================================

                elif input_rect.collidepoint(
                    event.pos
                ):

                    if game_state == "spelling":

                        input_active = True

                        keyboard_focus = "input"

        # ====================================================
        # DRAW
        # ====================================================

        screen.fill(
            BACKGROUND
        )

        # ====================================================
        # FINISHED SCREEN
        # ====================================================

        if game_state == "finished":

            draw_text(
                screen,
                "Spelling Game Complete!",
                title_font,
                TEXT_COLOR,
                WINDOW_WIDTH // 2,
                60,
                center=True
            )

            draw_text(
                screen,
                f"Correct: {len(correct_words)}",
                large_font,
                GREEN,
                150,
                140
            )

            draw_text(
                screen,
                f"Incorrect: {len(incorrect_words)}",
                large_font,
                RED,
                550,
                140
            )

            # ------------------------------------------------
            # Correct words
            # ------------------------------------------------

            draw_text(
                screen,
                "Correct Words",
                normal_font,
                GREEN,
                150,
                210
            )

            y = 255

            for word in correct_words:

                draw_text(
                    screen,
                    word,
                    small_font,
                    TEXT_COLOR,
                    170,
                    y
                )

                y += 30

                if y > 580:
                    break

            # ------------------------------------------------
            # Incorrect words
            # ------------------------------------------------

            draw_text(
                screen,
                "Incorrect Words",
                normal_font,
                RED,
                550,
                210
            )

            y = 255

            for word in incorrect_words:

                draw_text(
                    screen,
                    word,
                    small_font,
                    TEXT_COLOR,
                    570,
                    y
                )

                y += 30

                if y > 580:
                    break

        # ====================================================
        # GAME SCREEN
        # ====================================================

        else:

            draw_text(
                screen,
                "Spelling Game",
                title_font,
                TEXT_COLOR,
                WINDOW_WIDTH // 2,
                45,
                center=True
            )

            draw_text(
                screen,
                f"Word {current_position} of {len(words)}",
                small_font,
                GRAY,
                WINDOW_WIDTH // 2,
                90,
                center=True
            )

            draw_text(
                screen,
                "Listen to the word and sentence,",
                normal_font,
                TEXT_COLOR,
                WINDOW_WIDTH // 2,
                145,
                center=True
            )

            draw_text(
                screen,
                "then type the word:",
                normal_font,
                TEXT_COLOR,
                WINDOW_WIDTH // 2,
                180,
                center=True
            )

            # ------------------------------------------------
            # Input box
            # ------------------------------------------------

            if keyboard_focus == "input":

                border_color = BLUE

            else:

                border_color = INPUT_BORDER

            pygame.draw.rect(
                screen,
                INPUT_BACKGROUND,
                input_rect,
                border_radius=6
            )

            pygame.draw.rect(
                screen,
                border_color,
                input_rect,
                3,
                border_radius=6
            )

            draw_text(
                screen,
                user_input,
                large_font,
                TEXT_COLOR,
                input_rect.x + 15,
                input_rect.y + 12
            )

            # ------------------------------------------------
            # Result message
            # ------------------------------------------------

            if result_message:

                draw_text(
                    screen,
                    result_message,
                    normal_font,
                    result_color,
                    WINDOW_WIDTH // 2,
                    430,
                    center=True
                )

            # ------------------------------------------------
            # Buttons
            # ------------------------------------------------

            draw_button(
                screen,
                speak_word_button,
                "Hear Word",
                small_font,
                mouse_pos
            )

            draw_button(
                screen,
                speak_sentence_button,
                "Hear Sentence",
                small_font,
                mouse_pos
            )

            draw_button(
                screen,
                give_up_button,
                "Give Up",
                small_font,
                mouse_pos
            )

            if game_state == "result":

                draw_button(
                    screen,
                    continue_button,
                    "Continue",
                    small_font,
                    mouse_pos,
                    focused=(
                        keyboard_focus
                        == "continue"
                    )
                )

            # ------------------------------------------------
            # Instructions
            # ------------------------------------------------

            if game_state == "spelling":

                draw_text(
                    screen,
                    "Press ENTER to check your spelling.",
                    small_font,
                    GRAY,
                    WINDOW_WIDTH // 2,
                    580,
                    center=True
                )

            elif game_state == "result":

                draw_text(
                    screen,
                    "Press ENTER or click Continue.",
                    small_font,
                    GRAY,
                    WINDOW_WIDTH // 2,
                    580,
                    center=True
                )

        pygame.display.flip()

        clock.tick(FPS)

    # ========================================================
    # Cleanup
    # ========================================================

    stop_speech()

    pygame.quit()


# ============================================================
# Windows multiprocessing support
# ============================================================

if __name__ == "__main__":

    multiprocessing.freeze_support()

    main()