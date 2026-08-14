import os
import json
import random
import webbrowser

from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.metrics import dp

from kivy.uix.screenmanager import (
    ScreenManager,
    Screen,
    NoTransition
)

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup


# ============================================================
# SETTINGS
# ============================================================

APP_NAME = "FOOTBALL TRIVIA"

MAKER_PASSWORD = "mike8418"

BASE_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)

QUESTION_FILE = os.path.join(
    BASE_FOLDER,
    "football_questions.json"
)

MUSIC_FILES = [
    "football_music.mp3",
    "football_music.wav",
    "football_music.ogg",
    "music.mp3",
    "music.wav",
    "music.ogg"
]


# ============================================================
# COLORS
# ============================================================

BACKGROUND = (0.02, 0.10, 0.045, 1)
GREEN = (0.02, 0.42, 0.16, 1)
DARK_GREEN = (0.01, 0.22, 0.08, 1)
RED = (0.65, 0.05, 0.05, 1)
WHITE = (1, 1, 1, 1)
BLACK = (0, 0, 0, 1)


# ============================================================
# QUESTION DATABASE
# ============================================================

def load_questions():

    if not os.path.exists(QUESTION_FILE):
        return []

    try:

        with open(
            QUESTION_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

    except Exception:
        pass

    return []


def save_questions(questions):

    try:

        with open(
            QUESTION_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                questions,
                file,
                indent=2,
                ensure_ascii=False
            )

        return True

    except Exception:
        return False


# ============================================================
# MAIN APP
# ============================================================

class FootballTrivia(App):

    def build(self):

        Window.clearcolor = BACKGROUND

        self.questions = load_questions()

        self.player_name = ""

        self.quiz_questions = []

        self.current_question = 0

        self.score = 0

        self.current_answered = False

        self.music = None

        self.music_playing = False

        # ----------------------------------------------------
        # PROPER SCREEN MANAGER
        # ----------------------------------------------------

        self.sm = ScreenManager(
            transition=NoTransition()
        )

        self.sm.add_widget(
            HomeScreen(
                name="home"
            )
        )

        self.sm.add_widget(
            QuizSetupScreen(
                name="quiz_setup"
            )
        )

        self.sm.add_widget(
            QuizScreen(
                name="quiz"
            )
        )

        self.sm.add_widget(
            ResultsScreen(
                name="results"
            )
        )

        self.sm.add_widget(
            MakerLoginScreen(
                name="maker_login"
            )
        )

        self.sm.add_widget(
            MakerScreen(
                name="maker"
            )
        )

        self.sm.add_widget(
            AddQuestionsScreen(
                name="add_questions"
            )
        )

        self.sm.add_widget(
            ManageQuestionsScreen(
                name="manage_questions"
            )
        )

        self.sm.current = "home"

        self.start_music()

        return self.sm


    # ========================================================
    # MUSIC
    # ========================================================

    def start_music(self):

        for filename in MUSIC_FILES:

            path = os.path.join(
                BASE_FOLDER,
                filename
            )

            if not os.path.exists(path):
                continue

            try:

                self.music = SoundLoader.load(
                    path
                )

                if self.music:

                    self.music.loop = True

                    self.music.volume = 0.30

                    self.music.play()

                    self.music_playing = True

                    return

            except Exception:
                pass


    def toggle_music(self):

        if not self.music:

            self.message(
                "Music",
                "Music was not found.\n\n"
                "Put football_music.mp3 in the "
                "same folder as this Python file."
            )

            return

        try:

            if self.music_playing:

                self.music.stop()

                self.music_playing = False

            else:

                self.music.play()

                self.music_playing = True

        except Exception:
            pass


    # ========================================================
    # MESSAGE POPUP
    # ========================================================

    def message(
        self,
        title,
        text
    ):

        layout = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(8)
        )

        label = Label(
            text=text,
            color=BLACK,
            halign="center",
            valign="middle"
        )

        label.bind(
            size=lambda obj, value:
            setattr(
                obj,
                "text_size",
                (obj.width, None)
            )
        )

        layout.add_widget(label)

        ok = Button(
            text="OK",
            size_hint_y=None,
            height=dp(45)
        )

        layout.add_widget(ok)

        popup = Popup(
            title=title,
            content=layout,
            size_hint=(0.88, 0.48)
        )

        ok.bind(
            on_release=popup.dismiss
        )

        popup.open()


    # ========================================================
    # NAVIGATION
    # ========================================================

    def go(self, screen_name):

        self.sm.current = screen_name


    # ========================================================
    # HOME
    # ========================================================

    def home(self):

        self.sm.current = "home"


    # ========================================================
    # QUIZ SETUP
    # ========================================================

    def prepare_quiz(self):

        screen = self.sm.get_screen(
            "quiz_setup"
        )

        name = screen.name_input.text.strip()

        if not name:

            self.message(
                "Name Required",
                "Please enter your name first."
            )

            return

        self.player_name = name

        amount = int(
            screen.number_spinner.text
        )

        level = screen.level_spinner.text

        if level == "All Levels":

            available = list(
                self.questions
            )

        else:

            available = [
                q for q in self.questions
                if q.get(
                    "level",
                    ""
                ).lower()
                ==
                level.lower()
            ]

        if len(available) < amount:

            self.message(
                "Not Enough Questions",
                "You selected "
                + str(amount)
                + " questions.\n\n"
                "Only "
                + str(len(available))
                + " suitable questions "
                "are available."
            )

            return

        # random.sample prevents repeated
        # questions during this quiz.
        self.quiz_questions = random.sample(
            available,
            amount
        )

        self.current_question = 0

        self.score = 0

        self.show_quiz_question()


    # ========================================================
    # SHOW QUESTION
    # ========================================================

    def show_quiz_question(self):

        screen = self.sm.get_screen(
            "quiz"
        )

        screen.build_question()

        self.sm.current = "quiz"


    # ========================================================
    # ANSWER
    # ========================================================

    def answer_question(
        self,
        selected
    ):

        if self.current_answered:
            return

        self.current_answered = True

        question = self.quiz_questions[
            self.current_question
        ]

        correct = question.get(
            "answer",
            ""
        )

        screen = self.sm.get_screen(
            "quiz"
        )

        for button in screen.answer_buttons:

            button.disabled = True

        if selected == correct:

            self.score += 1

            screen.feedback.text = (
                "✓ CORRECT!\n\n"
                + question.get(
                    "description",
                    ""
                )
            )

        else:

            screen.feedback.text = (
                "✗ INCORRECT\n\n"
                "Correct answer: "
                + correct
                + "\n\n"
                + question.get(
                    "description",
                    ""
                )
            )

        screen.continue_button.disabled = False


    # ========================================================
    # NEXT QUESTION
    # ========================================================

    def next_question(self):

        self.current_question += 1

        if (
            self.current_question
            >= len(self.quiz_questions)
        ):

            self.show_results()

        else:

            self.show_quiz_question()


    # ========================================================
    # RESULTS
    # ========================================================

    def show_results(self):

        screen = self.sm.get_screen(
            "results"
        )

        screen.show_result()

        self.sm.current = "results"


    # ========================================================
    # SAVE MANY QUESTIONS
    # ========================================================

    def save_bulk_questions(
        self,
        text
    ):

        lines = text.splitlines()

        added = 0

        errors = []

        for line_number, line in enumerate(
            lines,
            start=1
        ):

            line = line.strip()

            if not line:
                continue

            parts = [
                x.strip()
                for x in line.split("|")
            ]

            if len(parts) != 8:

                errors.append(
                    "Line "
                    + str(line_number)
                    + ": must contain 8 sections."
                )

                continue

            question = parts[0]

            options = [
                parts[1],
                parts[2],
                parts[3],
                parts[4]
            ]

            correct = parts[5]

            description = parts[6]

            level = parts[7].capitalize()

            if level not in [
                "Easy",
                "Medium",
                "Hard"
            ]:

                errors.append(
                    "Line "
                    + str(line_number)
                    + ": level must be "
                    "Easy, Medium or Hard."
                )

                continue

            if not question:

                errors.append(
                    "Line "
                    + str(line_number)
                    + ": question is empty."
                )

                continue

            if any(
                not option
                for option in options
            ):

                errors.append(
                    "Line "
                    + str(line_number)
                    + ": all four options "
                    "are required."
                )

                continue

            if correct not in options:

                errors.append(
                    "Line "
                    + str(line_number)
                    + ": correct answer must "
                    "exactly match one option."
                )

                continue

            if not description:

                errors.append(
                    "Line "
                    + str(line_number)
                    + ": description is empty."
                )

                continue

            self.questions.append(
                {
                    "question": question,
                    "options": options,
                    "answer": correct,
                    "description": description,
                    "level": level
                }
            )

            added += 1

        save_questions(
            self.questions
        )

        return added, errors


    # ========================================================
    # SEARCH
    # ========================================================

    def search_question(
        self,
        query
    ):

        query = query.strip()

        if not query:

            self.message(
                "Search",
                "Please enter something to search."
            )

            return

        for question in self.questions:

            if query.lower() in question.get(
                "question",
                ""
            ).lower():

                screen = self.sm.get_screen(
                    "search_result"
                ) if self.sm.has_screen(
                    "search_result"
                ) else None

                self.show_search_result(
                    question
                )

                return

        try:

            webbrowser.open(
                "https://www.google.com/search?q="
                + query.replace(
                    " ",
                    "+"
                )
            )

        except Exception:

            self.message(
                "Search",
                "Google could not be opened."
            )


    def show_search_result(
        self,
        question
    ):

        screen = SearchResultScreen(
            name="search_result"
        )

        screen.question_data = question

        if self.sm.has_screen(
            "search_result"
        ):

            self.sm.remove_widget(
                self.sm.get_screen(
                    "search_result"
                )
            )

        self.sm.add_widget(screen)

        self.sm.current = "search_result"


    # ========================================================
    # DELETE QUESTION
    # ========================================================

    def delete_question(
        self,
        index
    ):

        if index < 0:
            return

        if index >= len(self.questions):
            return

        del self.questions[index]

        save_questions(
            self.questions
        )

        screen = self.sm.get_screen(
            "manage_questions"
        )

        screen.refresh()


    # ========================================================
    # STOP
    # ========================================================

    def on_stop(self):

        try:

            if self.music:
                self.music.stop()

        except Exception:
            pass


# ============================================================
# BASE SCREEN
# ============================================================

class BaseScreen(Screen):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.make_layout()


    def make_layout(self):

        self.scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True
        )

        self.content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(5),
            padding=(
                dp(8),
                dp(3),
                dp(8),
                dp(10)
            )
        )

        self.content.bind(
            minimum_height=
            self.content.setter(
                "height"
            )
        )

        self.scroll.add_widget(
            self.content
        )

        self.add_widget(
            self.scroll
        )


    def clear(self):

        self.content.clear_widgets()


    def title(
        self,
        text,
        size=22,
        height=45
    ):

        label = Label(
            text=text,
            font_size=dp(size),
            bold=True,
            color=WHITE,
            size_hint_y=None,
            height=dp(height),
            halign="center",
            valign="middle"
        )

        label.bind(
            size=lambda obj, value:
            setattr(
                obj,
                "text_size",
                (obj.width - dp(10), None)
            )
        )

        self.content.add_widget(label)

        return label


    def label(
        self,
        text,
        size=13,
        height=40
    ):

        label = Label(
            text=text,
            font_size=dp(size),
            color=WHITE,
            bold=True,
            size_hint_y=None,
            height=dp(height),
            halign="center",
            valign="middle"
        )

        label.bind(
            size=lambda obj, value:
            setattr(
                obj,
                "text_size",
                (obj.width - dp(10), None)
            )
        )

        self.content.add_widget(label)

        return label


    def button(
        self,
        text,
        height=50
    ):

        button = Button(
            text=text,
            font_size=dp(14),
            bold=True,
            color=WHITE,
            background_normal="",
            background_color=GREEN,
            size_hint_y=None,
            height=dp(height)
        )

        self.content.add_widget(
            button
        )

        return button


    def input(
        self,
        hint="",
        height=48,
        multiline=False
    ):

        field = TextInput(
            hint_text=hint,
            multiline=multiline,
            font_size=dp(15),
            foreground_color=BLACK,
            background_color=WHITE,
            size_hint_y=None,
            height=dp(height),
            padding=dp(8)
        )

        self.content.add_widget(
            field
        )

        return field


# ============================================================
# HOME SCREEN
# ============================================================

class HomeScreen(BaseScreen):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.build()


    def build(self):

        app = App.get_running_app()

        self.title(
            "⚽ FOOTBALL TRIVIA ⚽",
            25,
            48
        )

        self.label(
            "Test your football knowledge",
            13,
            30
        )

        self.label(
            "🔎 SEARCH FOOTBALL",
            13,
            28
        )

        self.search = self.input(
            "Search a football question..."
        )

        search_button = self.button(
            "SEARCH",
            46
        )

        search_button.bind(
            on_release=lambda x:
            app.search_question(
                self.search.text
            )
        )

        self.label(
            "If the question is not in the app, "
            "Google will be opened.",
            10,
            30
        )

        # ----------------------------------------------------
        # THIS BUTTON NOW DIRECTLY USES SCREENMANAGER
        # ----------------------------------------------------

        quiz_button = self.button(
            "🎮 GO TO QUIZ",
            58
        )

        quiz_button.bind(
            on_release=lambda x:
            app.go("quiz_setup")
        )

        # ----------------------------------------------------
        # MAKER BUTTON
        # ----------------------------------------------------

        maker_button = self.button(
            "🔐 MAKER / ADMIN",
            50
        )

        maker_button.bind(
            on_release=lambda x:
            app.go("maker_login")
        )

        music_button = self.button(
            "🎵 MUSIC ON / OFF",
            45
        )

        music_button.bind(
            on_release=lambda x:
            app.toggle_music()
        )

        self.label(
            "Questions stored: "
            + str(len(app.questions)),
            11,
            28
        )


# ============================================================
# QUIZ SETUP
# ============================================================

class QuizSetupScreen(BaseScreen):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.build()


    def build(self):

        app = App.get_running_app()

        self.title(
            "QUIZ SETUP",
            23,
            45
        )

        self.label(
            "PLAYER NAME",
            12,
            26
        )

        self.name_input = self.input(
            "Enter your name"
        )

        self.label(
            "LEVEL",
            12,
            26
        )

        self.level_spinner = Spinner(
            text="All Levels",
            values=[
                "All Levels",
                "Easy",
                "Medium",
                "Hard"
            ],
            size_hint_y=None,
            height=dp(47),
            font_size=dp(15)
        )

        self.content.add_widget(
            self.level_spinner
        )

        self.label(
            "NUMBER OF QUESTIONS",
            12,
            26
        )

        self.number_spinner = Spinner(
            text="5",
            values=[
                "5",
                "10",
                "15",
                "20"
            ],
            size_hint_y=None,
            height=dp(47),
            font_size=dp(15)
        )

        self.content.add_widget(
            self.number_spinner
        )

        self.start_button = self.button(
            "▶ START PLAY",
            58
        )

        self.start_button.disabled = True

        self.name_input.bind(
            text=self.check_name
        )

        self.start_button.bind(
            on_release=lambda x:
            app.prepare_quiz()
        )

        back = self.button(
            "BACK",
            43
        )

        back.bind(
            on_release=lambda x:
            app.go("home")
        )


    def check_name(
        self,
        instance,
        value
    ):

        self.start_button.disabled = not bool(
            value.strip()
        )


# ============================================================
# QUIZ SCREEN
# ============================================================

class QuizScreen(BaseScreen):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)


    def build_question(self):

        app = App.get_running_app()

        self.clear()

        app.current_answered = False

        question = app.quiz_questions[
            app.current_question
        ]

        self.title(
            "⚽ FOOTBALL TRIVIA",
            20,
            38
        )

        self.label(
            "Score: "
            + str(app.score)
            + "     Question "
            + str(app.current_question + 1)
            + " / "
            + str(len(app.quiz_questions)),
            12,
            30
        )

        # ----------------------------------------------------
        # QUESTION
        # ----------------------------------------------------

        self.question_scroll = ScrollView(
            size_hint_y=None,
            height=dp(125),
            do_scroll_x=False
        )

        question_label = Label(
            text=question.get(
                "question",
                ""
            ),
            font_size=dp(18),
            bold=True,
            color=WHITE,
            size_hint_y=None,
            height=dp(115),
            halign="center",
            valign="middle"
        )

        question_label.bind(
            size=lambda obj, value:
            setattr(
                obj,
                "text_size",
                (obj.width - dp(10), None)
            )
        )

        self.question_scroll.add_widget(
            question_label
        )

        self.content.add_widget(
            self.question_scroll
        )

        # ----------------------------------------------------
        # FOUR ANSWERS
        # ----------------------------------------------------

        options = list(
            question.get(
                "options",
                []
            )
        )

        random.shuffle(options)

        self.answer_buttons = []

        for option in options:

            button = self.button(
                option,
                48
            )

            button.bind(
                on_release=lambda
                btn,
                selected=option:
                app.answer_question(
                    selected
                )
            )

            self.answer_buttons.append(
                button
            )

        # ----------------------------------------------------
        # FEEDBACK
        # ----------------------------------------------------

        self.feedback_scroll = ScrollView(
            size_hint_y=None,
            height=dp(115),
            do_scroll_x=False
        )

        self.feedback = Label(
            text="Choose an answer.",
            font_size=dp(13),
            bold=True,
            color=WHITE,
            size_hint_y=None,
            height=dp(105),
            halign="center",
            valign="middle"
        )

        self.feedback.bind(
            size=lambda obj, value:
            setattr(
                obj,
                "text_size",
                (obj.width - dp(10), None)
            )
        )

        self.feedback_scroll.add_widget(
            self.feedback
        )

        self.content.add_widget(
            self.feedback_scroll
        )

        self.continue_button = self.button(
            "CONTINUE",
            48
        )

        self.continue_button.disabled = True

        self.continue_button.bind(
            on_release=lambda x:
            app.next_question()
        )


# ============================================================
# RESULTS
# ============================================================

class ResultsScreen(BaseScreen):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)


    def show_result(self):

        app = App.get_running_app()

        self.clear()

        total = len(
            app.quiz_questions
        )

        percentage = int(
            app.score * 100 / total
        )

        self.title(
            "🏆 QUIZ COMPLETE 🏆",
            25,
            55
        )

        self.label(
            "Well done, "
            + app.player_name
            + "!",
            17,
            42
        )

        self.label(
            "Score: "
            + str(app.score)
            + " / "
            + str(total),
            24,
            55
        )

        self.label(
            str(percentage) + "%",
            25,
            50
        )

        again = self.button(
            "PLAY AGAIN",
            55
        )

        again.bind(
            on_release=lambda x:
            app.go("quiz_setup")
        )

        home = self.button(
            "HOME",
            45
        )

        home.bind(
            on_release=lambda x:
            app.go("home")
        )


# ============================================================
# MAKER LOGIN
# ============================================================

class MakerLoginScreen(BaseScreen):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.build()


    def build(self):

        app = App.get_running_app()

        self.title(
            "🔐 MAKER / ADMIN",
            22,
            45
        )

        self.label(
            "Only the Maker can add or delete "
            "questions.",
            12,
            45
        )

        self.password = self.input(
            "Enter Maker password"
        )

        self.password.password = True

        login = self.button(
            "LOGIN",
            53
        )

        def login_now(instance):

            if self.password.text == MAKER_PASSWORD:

                self.password.text = ""

                app.go("maker")

            else:

                app.message(
                    "Wrong Password",
                    "Incorrect Maker password."
                )

        login.bind(
            on_release=login_now
        )

        back = self.button(
            "BACK",
            43
        )

        back.bind(
            on_release=lambda x:
            app.go("home")
        )


# ============================================================
# MAKER PANEL
# ============================================================

class MakerScreen(BaseScreen):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.build()


    def build(self):

        app = App.get_running_app()

        self.title(
            "⚽ MAKER PANEL",
            23,
            45
        )

        self.label(
            "Questions stored: "
            + str(len(app.questions)),
            12,
            30
        )

        add = self.button(
            "➕ ADD MANY QUESTIONS",
            55
        )

        add.bind(
            on_release=lambda x:
            app.go("add_questions")
        )

        manage = self.button(
            "📋 VIEW / DELETE QUESTIONS",
            53
        )

        manage.bind(
            on_release=lambda x:
            app.go("manage_questions")
        )

        back = self.button(
            "LOG OUT / HOME",
            45
        )

        back.bind(
            on_release=lambda x:
            app.go("home")
        )


# ============================================================
# ADD QUESTIONS
# ============================================================

class AddQuestionsScreen(BaseScreen):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.build()


    def build(self):

        app = App.get_running_app()

        self.title(
            "➕ ADD MANY QUESTIONS",
            20,
            42
        )

        self.label(
            "ONE QUESTION PER LINE",
            12,
            26
        )

        self.label(
            "Question | Option 1 | Option 2 | "
            "Option 3 | Option 4 | Correct Answer | "
            "Description | Level",
            10,
            55
        )

        self.label(
            "Example:\n"
            "Who won the 2022 World Cup? | "
            "Argentina | France | Brazil | Germany | "
            "Argentina | Argentina won the final. | Easy",
            10,
            85
        )

        self.bulk_input = TextInput(
            hint_text=(
                "Paste many questions here.\n"
                "One question on each line."
            ),
            multiline=True,
            font_size=dp(13),
            foreground_color=BLACK,
            background_color=WHITE,
            size_hint_y=None,
            height=dp(330),
            padding=dp(8)
        )

        self.content.add_widget(
            self.bulk_input
        )

        save = self.button(
            "💾 SAVE ALL QUESTIONS",
            55
        )

        save.bind(
            on_release=lambda x:
            self.save()
        )

        back = self.button(
            "BACK TO MAKER",
            43
        )

        back.bind(
            on_release=lambda x:
            app.go("maker")
        )


    def save(self):

        app = App.get_running_app()

        text = self.bulk_input.text.strip()

        if not text:

            app.message(
                "No Questions",
                "Please enter at least one question."
            )

            return

        added, errors = app.save_bulk_questions(
            text
        )

        result = (
            str(added)
            + " question(s) added successfully."
        )

        if errors:

            result += (
                "\n\nErrors:\n"
                + "\n".join(errors[:8])
            )

        self.bulk_input.text = ""

        app.message(
            "Import Complete",
            result
        )


# ============================================================
# MANAGE QUESTIONS
# ============================================================

class ManageQuestionsScreen(BaseScreen):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(**kwargs)

        self.build()


    def build(self):

        app = App.get_running_app()

        self.title(
            "📋 QUESTIONS",
            21,
            43
        )

        self.refresh()


    def refresh(self):

        app = App.get_running_app()

        # Keep title but remove everything below it.
        while len(self.content.children) > 1:

            self.content.remove_widget(
                self.content.children[0]
            )

        # Kivy stores children in reverse order.
        # Rebuild screen cleanly instead.
        self.clear()

        self.title(
            "📋 QUESTIONS",
            21,
            43
        )

        if not app.questions:

            self.label(
                "No questions have been added.",
                14,
                55
            )

        else:

            for index, question in enumerate(
                app.questions
            ):

                row = BoxLayout(
                    orientation="horizontal",
                    size_hint_y=None,
                    height=dp(72),
                    spacing=dp(5)
                )

                text = Label(
                    text=(
                        question.get(
                            "question",
                            ""
                        )
                        + "\n["
                        + question.get(
                            "level",
                            ""
                        )
                        + "]"
                    ),
                    font_size=dp(10),
                    color=WHITE,
                    halign="left",
                    valign="middle"
                )

                text.bind(
                    size=lambda obj, value:
                    setattr(
                        obj,
                        "text_size",
                        (obj.width, None)
                    )
                )

                delete = Button(
                    text="DELETE",
                    size_hint_x=None,
                    width=dp(75),
                    background_normal="",
                    background_color=RED
                )

                delete.bind(
                    on_release=lambda
                    button,
                    number=index:
                    app.delete_question(
                        number
                    )
                )

                row.add_widget(text)

                row.add_widget(delete)

                self.content.add_widget(row)

        back = self.button(
            "BACK TO MAKER",
            43
        )

        back.bind(
            on_release=lambda x:
            app.go("maker")
        )


# ============================================================
# SEARCH RESULT
# ============================================================

class SearchResultScreen(BaseScreen):

    def __init__(
        self,
        **kwargs
    ):

        self.question_data = {}

        super().__init__(**kwargs)


    def on_pre_enter(self, *args):

        self.build_result()


    def build_result(self):

        app = App.get_running_app()

        self.clear()

        question = self.question_data

        self.title(
            "QUESTION FOUND",
            21,
            45
        )

        self.label(
            question.get(
                "question",
                ""
            ),
            17,
            110
        )

        self.feedback = self.label(
            "Try the question first.",
            12,
            80
        )

        for option in question.get(
            "options",
            []
        ):

            button = self.button(
                option,
                48
            )

            button.bind(
                on_release=lambda
                btn,
                selected=option:
                self.answer_search(
                    selected
                )
            )

        back = self.button(
            "BACK",
            43
        )

        back.bind(
            on_release=lambda x:
            app.go("home")
        )


    def answer_search(
        self,
        selected
    ):

        question = self.question_data

        correct = question.get(
            "answer",
            ""
        )

        if selected == correct:

            self.feedback.text = (
                "✓ CORRECT!\n\n"
                + question.get(
                    "description",
                    ""
                )
            )

        else:

            self.feedback.text = (
                "✗ INCORRECT\n\n"
                "Correct answer: "
                + correct
                + "\n\n"
                + question.get(
                    "description",
                    ""
                )
            )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    FootballTrivia().run()