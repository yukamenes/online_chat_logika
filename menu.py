from customtkinter import *


class MainMenu(CTk):
    def __init__(self):
        super().__init__()

        self.name = None
        self.port = None
        self.host = None

        self.title("Agario Launcher")
        self.geometry("500x400")

        self.window_title = CTkLabel(
            self,
            text="Connect to server:",
            font=("Comic Sans MS", 20, "bold")
        )
        self.window_title.pack(pady=15)

        self.name_entry = CTkEntry(
            self,
            placeholder_text="Enter your name:",
            height=50,
            font=("Comic Sans MS", 20, "bold")
        )
        self.name_entry.pack(pady=15)

        self.host_entry = CTkEntry(
            self,
            placeholder_text="Enter your host:",
            height=50,
            font=("Comic Sans MS", 20, "bold")
        )
        self.host_entry.pack(pady=15)

        self.port_entry = CTkEntry(
            self,
            placeholder_text="Enter your port:",
            height=50,
            font=("Comic Sans MS", 20, "bold")
        )
        self.port_entry.pack(pady=15)

        self.connect_btn = CTkButton(
            self,
            text="Connect",
            height=50,
            font=("Comic Sans MS", 20, "bold"),
            command=self.open_game
        )
        self.connect_btn.pack()

    def open_game(self):
        self.name = self.name_entry.get() or "Player"
        self.host = self.host_entry.get() or "localhost"
        try:
            self.port = int(self.port_entry.get() or "8080")
        except ValueError:
            self.port = 8080
        self.destroy()
