import tkinter as tk
import tkinter.ttk as ttk

from english_words import english_words_lower_set
from tkinter.messagebox import askyesno, showerror, showinfo

from game import Game, GuessResult

MAX_GUESSES = 10
ALPHABET = 'abcdefghijklmnopqrstuvwxyz'


class GUI(object):
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('Fauxdle')
        self.window.resizable(False, False)
        self.main_frame = ttk.Frame(master=self.window)
        self.main_frame.pack(anchor='nw', fill=tk.BOTH)
        style = ttk.Style(self.main_frame)
        style.theme_use('classic')
        style.configure('.', font=('Arial', 20))

        self._cursor_row = self._cursor_col = 0
        self._word_buffer = ''
        self._num_letters = 5

        self._add_num_letters_components()

        new_game_button = ttk.Button(
            master=self.main_frame, text='New Game', command=self._new_game
        )
        new_game_button.grid(row=MAX_GUESSES + 3, column=4, columnspan=2, sticky='se')

        self.require_real_words = tk.BooleanVar(value=True)
        real_word_checkbox = ttk.Checkbutton(
            self.main_frame, text='Require real words', variable=self.require_real_words,
            onvalue=True, offvalue=False
        )
        real_word_checkbox.grid(row=MAX_GUESSES + 2, column=0, columnspan=3, sticky='ne', padx=20)

        self._add_used_letters_pane()

        self._grid = None
        self._grid_labels = None

        self._new_game()

        self.window.bind("<Key>", self._handle_keypress)
        self.window.mainloop()

    def _add_used_letters_pane(self) -> None:
        used_letters_pane = ttk.Frame(self.main_frame)
        used_letters_pane.grid(row=MAX_GUESSES, column=0, rowspan=2, columnspan=5)

        self._letters_labels = []

        for i, letter in enumerate(ALPHABET):
            label = ttk.Label(
                master=used_letters_pane, text=letter, background=GuessResult.NOT_GUESSED.color,
                font=('Arial', 28), justify='center', anchor=tk.CENTER
            )
            label.grid(row=i // 13, column=i % 13, sticky='nsew', padx=3, pady=3)
            self._letters_labels.append(label)

    def _add_num_letters_components(self) -> None:
        self._num_letters_frame = ttk.Frame(master=self.main_frame, height=75, width=75 * 3)
        self._num_letters_frame.grid(column=0, row=MAX_GUESSES + 3, columnspan=3, sticky='sw')
        self._num_letters_label = ttk.Label(
            master=self._num_letters_frame, text=f'{self._num_letters}', anchor='center', width=50,
            font=('Arial', 18)
        )
        num_letters_title_label = ttk.Label(
            master=self._num_letters_frame, text='Number of letters:', font=('Arial', 20),
            anchor='center'
        )
        decrease_button = ttk.Button(
            master=self._num_letters_frame, text='-', command=self._decrease_word_length
        )
        increase_button = ttk.Button(
            master=self._num_letters_frame, text='+', command=self._increase_word_length
        )
        decrease_button.place(x=20, y=25, width=75, height=50)
        increase_button.place(x=145, y=25, width=75, height=50)
        num_letters_title_label.place(x=20, y=0)
        self._num_letters_label.place(x=95, y=25, width=50, height=50)

    def _initialize_word_grid(self) -> None:
        if self._grid is not None:
            for row in self._grid:
                for component in row:
                    if component is not None:
                        component.destroy()

        self._grid = [[None] * self._num_letters for _ in range(MAX_GUESSES)]
        self._grid_labels = [[None] * self._num_letters for _ in range(MAX_GUESSES)]

        self.main_frame.rowconfigure(list(range(MAX_GUESSES + 4)), minsize=75)
        self.main_frame.columnconfigure(list(range(max(self._num_letters, 6))), minsize=75)

        for y in range(MAX_GUESSES):
            for x in range(self._num_letters):
                frame = self._grid[y][x] = ttk.Frame(
                    master=self.main_frame, relief=tk.RIDGE, borderwidth=5
                )
                frame.grid(row=y, column=x, sticky='nsew')
                label = self._grid_labels[y][x] = ttk.Label(
                    master=frame, text='', font=('Arial', 52), justify='center', anchor=tk.CENTER
                )
                label.pack(fill=tk.BOTH)

    def _new_game(self) -> None:
        try:
            self.game = Game(self._num_letters)
            self._initialize_word_grid()
            self._cursor_row = self._cursor_col = 0
            self._word_buffer = ''
            self._update_used_letter_colors()

            width = max((self._num_letters + 1) * 75, 6 * 75) + 5
            height = 75 * (MAX_GUESSES + 4)
            self.window.geometry(f'{width}x{height}')
        except ValueError:
            showerror(
                'Error', f'There are no words of length {self._num_letters}. Please change' +
                ' the word length before creating a new game.'
            )

    def _increase_word_length(self) -> None:
        self._update_word_length(self._num_letters + 1)

    def _decrease_word_length(self) -> None:
        self._update_word_length(self._num_letters - 1)

    def _update_word_length(self, new_length: int) -> None:
        if Game.words_df.word_length.max() >= new_length > 2:
            self._num_letters = new_length
            self._num_letters_label['text'] = f'{new_length}'

            start_new_game = askyesno(
                title='New Game?', message='Word length changed. Do you want to start a new game?'
            )
            if start_new_game:
                self._new_game()

    def _handle_keypress(self, event: tk.Event) -> None:
        if event.keysym == 'BackSpace':
            self._cursor_col = max(self._cursor_col - 1, 0)
            self._grid_labels[self._cursor_row][self._cursor_col]['text'] = ''
            self._word_buffer = self._word_buffer[:-1]
        elif event.keysym == 'Escape':
            self.window.destroy()
        elif (key := event.char.lower()).isalpha() and len(self._word_buffer) < self._num_letters:
            self._word_buffer += key
            self._grid_labels[self._cursor_row][self._cursor_col]['text'] = key
            self._cursor_col += 1
        elif event.keysym == 'Return' and len(self._word_buffer) == self._num_letters:
            valid_guess = (
                    self._word_buffer in english_words_lower_set or
                    not self.require_real_words.get()
            )
            if valid_guess:
                guess_results = self.game.guess(self._word_buffer)

                self._update_used_letter_colors()

                self._word_buffer = ''

                for column, result in enumerate(guess_results):
                    self._grid_labels[self._cursor_row][column]['background'] = result.color

                self._cursor_col = 0
                self._cursor_row += 1

                if self.game.won:
                    showinfo('Victory!', 'Congratulations, you won!')
                elif self._cursor_row == MAX_GUESSES:
                    showinfo(
                        'Game Over',
                        f'Sorry, you lost. The word was {self.game.word}. Better luck next time!'
                    )
            else:
                showerror(
                    'Invalid Guess', 'Please either guess real words or uncheck the checkbox.'
                )

    def _update_used_letter_colors(self) -> None:
        for letter, label in zip(ALPHABET, self._letters_labels):
            label['background'] = self.game.guessed_letters[letter].color


if __name__ == '__main__':
    GUI()
