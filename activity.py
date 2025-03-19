from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ActivityToolbarButton
from gi.repository import Gtk, Gdk
import gi
gi.require_version('Gtk', '3.0')
from gettext import gettext as _

import random
import os
import sys
# Add parent directory to Python path to find shared modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from dictionary_manager import DictionaryManager
from sentences import SENTENCES

class WordFillActivity(activity.Activity):
    def __init__(self, handle):
        super(WordFillActivity, self).__init__(handle)
        
        # Initialize dictionary manager
        self.dict_manager = DictionaryManager()
        
        # Set up the toolbar
        self.max_participants = 1
        toolbar_box = ToolbarBox()
        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, 0)
        activity_button.show()

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()

        self.set_toolbar_box(toolbar_box)
        toolbar_box.show()

        # Main container
        self.vbox = Gtk.VBox(spacing=10)
        self.vbox.set_border_width(20)
        self.set_canvas(self.vbox)

        # Welcome screen
        self.welcome_label = Gtk.Label()
        self.welcome_label.set_markup("<b><big>WordFill Game</big></b>")
        self.vbox.pack_start(self.welcome_label, False, False, 0)

        self.start_button = Gtk.Button(label="Start Game")
        self.start_button.connect("clicked", self.start_game)
        self.start_button.set_halign(Gtk.Align.CENTER)
        self.vbox.pack_start(self.start_button, False, False, 10)

        # Game screen components
        self.sentence_label = Gtk.Label()
        self.sentence_label.set_line_wrap(True)
        self.sentence_label.set_justify(Gtk.Justification.CENTER)
        self.vbox.pack_start(self.sentence_label, False, False, 20)

        # Options container
        self.options_box = Gtk.VBox(spacing=10)
        self.options_box.set_halign(Gtk.Align.CENTER)
        self.vbox.pack_start(self.options_box, True, True, 0)

        # New game button
        self.new_game_button = Gtk.Button(label="New Game")
        self.new_game_button.connect("clicked", self.show_welcome_screen)
        self.new_game_button.set_halign(Gtk.Align.CENTER)
        self.vbox.pack_start(self.new_game_button, False, False, 10)

        # Dictionary button
        self.dictionary_button = Gtk.Button(label="📖")
        self.dictionary_button.set_tooltip_text("Open Dictionary")
        self.dictionary_button.set_halign(Gtk.Align.END)
        self.dictionary_button.set_valign(Gtk.Align.END)
        self.dictionary_button.connect("clicked", self.open_dictionary)
        self.vbox.pack_end(self.dictionary_button, False, False, 0)

        self.show_welcome_screen()
        self.show_all()

    def show_welcome_screen(self, widget=None):
        """Show the welcome screen."""
        self.welcome_label.show()
        self.start_button.show()
        self.sentence_label.hide()
        self.options_box.hide()
        self.new_game_button.hide()

    def start_game(self, widget):
        """Start a new game."""
        self.welcome_label.hide()
        self.start_button.hide()
        
        # Select random sentence
        self.current_question = random.choice(SENTENCES)
        
        # Mark the correct word as seen
        self.dict_manager.mark_word_seen(self.current_question["word"])
        
        # Display sentence
        self.sentence_label.set_markup(
            f"<big>{self.current_question['sentence']}</big>"
        )
        self.sentence_label.show()
        
        # Clear previous options
        for child in self.options_box.get_children():
            self.options_box.remove(child)
        
        # Add option buttons
        for option in self.current_question["options"]:
            button = Gtk.Button(label=option.upper())
            button.connect("clicked", self.check_answer, option)
            self.options_box.pack_start(button, False, False, 0)
        
        self.options_box.show_all()
        self.new_game_button.show()

    def check_answer(self, button, selected_word):
        """Check if the selected answer is correct."""
        correct_word = self.current_question["word"]
        
        # Update button colors
        for child in self.options_box.get_children():
            word = child.get_label().lower()
            if word == correct_word:
                child.get_style_context().add_class("correct")
            else:
                child.get_style_context().add_class("absent")
            child.set_sensitive(False)
        
        # If correct answer, mark as guessed
        if selected_word == correct_word:
            self.dict_manager.mark_word_guessed(correct_word)

    def open_dictionary(self, widget):
        """Open the dictionary window with mastery levels."""
        dictionary_window = Gtk.Window(title="My Word Dictionary")
        dictionary_window.set_default_size(300, 400)

        # Create main container
        main_box = Gtk.VBox(spacing=10)
        main_box.set_border_width(10)

        # Add header with legend
        header_box = Gtk.HBox(spacing=10)
        header_box.set_margin_bottom(10)
        
        # Add legend labels
        legend_labels = [
            ("New", "#787c7e"),
            ("Learnt", "#ff9933"),
            ("Mastered", "#0066cc")
        ]
        
        for text, color in legend_labels:
            label = Gtk.Label()
            label.set_markup(
                f'<span background="{color}" foreground="white" '
                f'weight="bold"> {text} </span>'
            )
            header_box.pack_start(label, False, False, 5)
        
        main_box.pack_start(header_box, False, False, 0)

        # Add word list
        words_box = Gtk.VBox(spacing=5)
        
        try:
            words = self.dict_manager.get_all_words()
            for word in words:
                # Create a horizontal box for each word and its tag
                hbox = Gtk.HBox(spacing=10)
                
                # Word label
                word_label = Gtk.Label(label=word.upper())
                word_label.set_halign(Gtk.Align.START)
                hbox.pack_start(word_label, True, True, 0)
                
                # Mastery level tag
                mastery_level = self.dict_manager.get_mastery_level(word)
                tag_label = Gtk.Label()
                tag_label.set_markup(
                    f'<span background="{self._get_tag_color(mastery_level)}" '
                    f'foreground="white" weight="bold"> {mastery_level} </span>'
                )
                hbox.pack_end(tag_label, False, False, 0)
                
                words_box.pack_start(hbox, False, False, 0)
        except Exception as e:
            error_label = Gtk.Label(label=f"Error loading dictionary: {e}")
            words_box.pack_start(error_label, False, False, 0)

        # Add scrolled window
        scroll = Gtk.ScrolledWindow()
        scroll.add(words_box)
        main_box.pack_start(scroll, True, True, 0)

        dictionary_window.add(main_box)
        dictionary_window.show_all()

    def _get_tag_color(self, mastery_level):
        """Get the color for mastery level tag."""
        colors = {
            "new": "#787c7e",      # Gray
            "learnt": "#ff9933",   # Orange
            "mastered": "#0066cc"  # Blue
        }
        return colors.get(mastery_level, "#787c7e")

# Add this at the end of the file
css = b'''
.correct {
    background-color: #0066cc;
    color: white;
    border-radius: 4px;
    border: 1px solid #0066cc;
}

.absent {
    background-color: #787c7e;
    color: white;
    border-radius: 4px;
    border: 1px solid #787c7e;
}

GtkLabel {
    font-size: 16px;
    padding: 10px;
}

GtkButton {
    font-size: 16px;
    padding: 10px 20px;
    margin: 5px;
}
'''

style_provider = Gtk.CssProvider()
style_provider.load_from_data(css)
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(),
    style_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
) 