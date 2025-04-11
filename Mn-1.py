import customtkinter as ctk
from tkinter import filedialog
import pygame
import os
from mutagen.mp3 import MP3
from mutagen.flac import FLAC as FLAC_MUTAGEN
import time
import random
import threading
import numpy as np
from pydub import AudioSegment # Requires ffmpeg/ffprobe in PATH or specified location
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import traceback # For detailed error printing

# --- Theme Color Definitions ---
# Define colors for the themes
COLOR_BLACK = "#000000"
COLOR_WHITE = "#FFFFFF"
COLOR_DEEP_RED = "#8B0000" # Deep Red (Accent / Red Theme BG)
COLOR_LIGHT_RED_HOVER = "#A52A2A" # Lighter red for hover in red theme
COLOR_SILVER = "#C0C0C0" # Silver color (Secondary Dark / Light Grey Text)
COLOR_DARK_GRAY = "#333333" # Dark Gray (e.g., for light theme hover)
COLOR_LIGHT_GRAY = "#D3D3D3" # Light Gray (e.g., for light theme slider bg, light waveform)
COLOR_MID_GRAY = "#404040"  # Medium Grey background
COLOR_DARKER_MID_GRAY = "#505050" # Slightly darker grey for elements (No longer used for button BG)
COLOR_LIGHTER_MID_GRAY = "#666666" # Lighter grey for hover

# --- Theme Palettes ---
THEMES = {
    "dark": {
        "root_bg": COLOR_BLACK,
        "frame_bg": COLOR_BLACK,
        "label_bg": COLOR_BLACK,
        "label_fg": COLOR_WHITE,
        "button_fg": COLOR_BLACK,       # Button bg matches frame
        "button_text": COLOR_WHITE,
        "button_hover": COLOR_DEEP_RED, # Hover color stands out
        "slider_bg": COLOR_BLACK,
        "slider_progress": COLOR_DEEP_RED,
        "slider_button": COLOR_SILVER,
        "slider_button_hover": COLOR_SILVER,
        "plot_bg": COLOR_BLACK,
        "plot_wave_main": COLOR_WHITE,
        "plot_wave_indicator": COLOR_DEEP_RED,
        "plot_osc_main": COLOR_DEEP_RED,
        "plot_spine": COLOR_WHITE,
        "plot_text": COLOR_WHITE,
        "list_bg": COLOR_BLACK,
        "list_fg": COLOR_WHITE,
        "list_selected_fg": COLOR_DEEP_RED,
        "list_scrollbar": COLOR_DEEP_RED,
        "list_scrollbar_hover": COLOR_WHITE,
        "muted_fg": COLOR_DEEP_RED,
        "active_button_fg": COLOR_DEEP_RED,
        "inactive_button_fg": COLOR_WHITE,
        "theme_toggle_fg": COLOR_WHITE, # Specific color for theme button text
    },
    "light": {
        "root_bg": COLOR_WHITE,
        "frame_bg": COLOR_WHITE,
        "label_bg": COLOR_WHITE,
        "label_fg": COLOR_BLACK,
        "button_fg": COLOR_WHITE,       # Button bg matches frame
        "button_text": COLOR_BLACK,
        "button_hover": COLOR_LIGHT_GRAY, # Hover color stands out (slightly)
        "slider_bg": COLOR_LIGHT_GRAY,
        "slider_progress": COLOR_DEEP_RED,
        "slider_button": COLOR_BLACK,
        "slider_button_hover": COLOR_DARK_GRAY,
        "plot_bg": COLOR_WHITE,
        "plot_wave_main": COLOR_LIGHT_GRAY,
        "plot_wave_indicator": COLOR_DEEP_RED,
        "plot_osc_main": COLOR_DEEP_RED,
        "plot_spine": COLOR_BLACK,
        "plot_text": COLOR_BLACK,
        "list_bg": COLOR_WHITE,
        "list_fg": COLOR_BLACK,
        "list_selected_fg": COLOR_DEEP_RED,
        "list_scrollbar": COLOR_DEEP_RED,
        "list_scrollbar_hover": COLOR_BLACK,
        "muted_fg": COLOR_DEEP_RED,
        "active_button_fg": COLOR_DEEP_RED,
        "inactive_button_fg": COLOR_BLACK,
        "theme_toggle_fg": COLOR_BLACK, # Specific color for theme button text
    },
    "grey": {
        "root_bg": COLOR_MID_GRAY,
        "frame_bg": COLOR_MID_GRAY,
        "label_bg": COLOR_MID_GRAY,
        "label_fg": COLOR_SILVER,
        "button_fg": COLOR_MID_GRAY,    # Button bg matches frame
        "button_text": COLOR_WHITE,
        "button_hover": COLOR_LIGHTER_MID_GRAY, # Hover color stands out
        "slider_bg": COLOR_DARKER_MID_GRAY, # Keep slider track slightly different
        "slider_progress": COLOR_DEEP_RED,
        "slider_button": COLOR_SILVER,
        "slider_button_hover": COLOR_WHITE,
        "plot_bg": COLOR_MID_GRAY,
        "plot_wave_main": COLOR_SILVER,
        "plot_wave_indicator": COLOR_DEEP_RED,
        "plot_osc_main": COLOR_DEEP_RED,
        "plot_spine": COLOR_SILVER,
        "plot_text": COLOR_SILVER,
        "list_bg": COLOR_MID_GRAY,
        "list_fg": COLOR_SILVER,
        "list_selected_fg": COLOR_WHITE,
        "list_scrollbar": COLOR_DEEP_RED,
        "list_scrollbar_hover": COLOR_WHITE,
        "muted_fg": COLOR_DEEP_RED,
        "active_button_fg": COLOR_DEEP_RED,
        "inactive_button_fg": COLOR_WHITE,
        "theme_toggle_fg": COLOR_WHITE, # Specific color for theme button text
    },
    "red": {
        "root_bg": COLOR_DEEP_RED,
        "frame_bg": COLOR_DEEP_RED,
        "label_bg": COLOR_DEEP_RED,
        "label_fg": COLOR_WHITE,
        "button_fg": COLOR_DEEP_RED,    # Button bg matches frame
        "button_text": COLOR_WHITE,
        "button_hover": COLOR_LIGHT_RED_HOVER, # Hover color stands out
        "slider_bg": COLOR_BLACK,
        "slider_progress": COLOR_WHITE,
        "slider_button": COLOR_WHITE,
        "slider_button_hover": COLOR_LIGHT_GRAY,
        "plot_bg": COLOR_DEEP_RED,
        "plot_wave_main": COLOR_WHITE,
        "plot_wave_indicator": COLOR_WHITE,
        "plot_osc_main": COLOR_WHITE,
        "plot_spine": COLOR_WHITE,
        "plot_text": COLOR_WHITE,
        "list_bg": COLOR_DEEP_RED,
        "list_fg": COLOR_WHITE,
        "list_selected_fg": COLOR_BLACK,
        "list_scrollbar": COLOR_WHITE,
        "list_scrollbar_hover": COLOR_BLACK,
        "muted_fg": COLOR_WHITE,
        "active_button_fg": COLOR_WHITE,
        "inactive_button_fg": COLOR_WHITE,
        "theme_toggle_fg": COLOR_WHITE, # Specific color for theme button text
    }
}

SPINE_LINEWIDTH = 0.8 # Plot border thickness

# --- Main Music Player Class ---
class MN1MusicPlayer:
    def __init__(self, root):
        # Initialize the main window
        self.root = root
        self.root.title("MN-1") # <<< Also updated window title just in case
        self.root.geometry("800x650")
        # Initial background color set via apply_theme later
        self.root.resizable(True, True)

        # Theme control
        self.themes = THEMES
        # Define the order for cycling
        self.theme_cycle = ["dark", "light", "grey", "red"]
        self.current_theme_name = "dark" # Start with dark theme

        # Initialize pygame mixer
        try:
            pygame.mixer.init()
            print("Pygame mixer initialized successfully.")
        except pygame.error as e:
            print(f"FATAL: Error initializing pygame mixer: {e}")
            try:
                import tkinter.messagebox
                tkinter.messagebox.showerror("Pygame Error", f"Could not initialize audio output.\nError: {e}\n\nThe application might not play sound.")
            except: pass # Ignore if messagebox fails

        # Global variables for player state
        self.current_song = ""
        self.songs_list = []
        self.current_song_index = 0
        self.playing_state = False
        self.paused = False
        self.shuffle_state = False # Use self.shuffle_state for logic
        self.loop_state = 0
        self.muted = False
        self.previous_volume = 0.5
        self.stopped_position = 0.0
        self.slider_active = False
        self.waveform_dragging = False
        self.is_generating_waveform = False
        self.is_loading = False
        self.has_error = False

        # Set default volume
        try: pygame.mixer.music.set_volume(0.5)
        except Exception as e: print(f"Warning: Could not set initial volume: {e}")

        # Create fonts
        self.title_font = ("SF Mono", 16, "bold")
        self.normal_font = ("SF Mono", 11)
        self.button_font = ("SF Mono", 13, "bold")

        # --- Matplotlib Setup ---
        # Figures are created here, but styled in apply_theme
        self.fig_wave, self.ax_wave = plt.subplots(figsize=(5, 1.5))
        self.mpl_canvas_widget_wave = None
        self.position_indicator_line_wave = None

        self.fig_osc, self.ax_osc = plt.subplots(figsize=(5, 0.8))
        self.mpl_canvas_widget_osc = None
        self.ax_osc.set_ylim(-1.1, 1.1) # Keep y-limits

        # --- Waveform/Sample Data Control ---
        self.waveform_peak_data = None
        self.raw_sample_data = None
        self.sample_rate = None
        self.waveform_thread = None
        self.waveform_abort_flag = threading.Event()

        # --- Oscilloscope settings ---
        self.osc_window_seconds = 0.05
        self.osc_downsample_factor = 5

        # --- Time-related ---
        self.song_length = 0.0
        self.song_time = 0.0
        self.time_elapsed = "00:00"
        self.total_time = "00:00"

        # --- Threading ---
        self.update_thread = None
        self.thread_running = False

        # --- UI Variables ---
        self.song_title_var = ctk.StringVar(value="NO SONG LOADED")

        # --- Create UI Elements (Widgets created, styling applied later) ---
        self.create_frames()
        self.create_player_area()
        self.create_waveform_display() # Creates canvas but styling is in apply_theme
        self.create_oscilloscope_display() # Creates canvas but styling is in apply_theme
        self.create_controls()
        self.create_tracklist_area() # Changed name

        # --- Apply Initial Theme ---
        self.apply_theme() # Apply the default theme (dark)

        # --- Initial Plot Placeholders (after theme applied) ---
        # These will now use the initial theme colors
        self.draw_initial_placeholder(self.ax_wave, self.fig_wave, self.themes[self.current_theme_name]['plot_spine'], "LOAD A SONG")
        self.draw_initial_placeholder(self.ax_osc, self.fig_osc, self.themes[self.current_theme_name]['plot_osc_main'], "")


        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        print("UI Initialized with dark theme.")

    def _configure_axes(self, ax, fig, spine_color, bg_color):
        """Helper to configure matplotlib axes appearance based on theme."""
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        ax.tick_params(axis='both', colors=spine_color, labelsize=0, length=0) # Hide ticks
        for spine in ax.spines.values():
            spine.set_color(spine_color) # Set border color
            spine.set_linewidth(SPINE_LINEWIDTH) # Set border thickness
        ax.margins(0); ax.set_yticks([]); ax.set_xticks([]) # Remove margins and axis labels
        try: fig.tight_layout(pad=0.05)
        except Exception:
             # print("Warning: tight_layout failed."); # Less verbose
             fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)

    def create_frames(self):
        """Create the main frames for layout."""
        # Colors set by apply_theme
        self.player_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.player_frame.pack(pady=5, padx=10, fill="both", expand=True)

        self.left_frame = ctk.CTkFrame(self.player_frame, width=500, corner_radius=0)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.right_frame = ctk.CTkFrame(self.player_frame, width=300, corner_radius=0)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.controls_frame = ctk.CTkFrame(self.left_frame, height=80, corner_radius=0)
        self.controls_frame.pack(side="bottom", fill="x", pady=(5,5))

        self.visual_frame = ctk.CTkFrame(self.left_frame, corner_radius=0)
        self.visual_frame.pack(side="top", fill="both", expand=True, pady=(0,5))

    def create_player_area(self):
        """Create widgets within the visual_frame (info, plots, slider)."""
        # Colors set by apply_theme
        self.info_frame = ctk.CTkFrame(self.visual_frame, corner_radius=0)
        self.info_frame.pack(fill="x", pady=(0,5))

        self.song_title_label = ctk.CTkLabel(self.info_frame, textvariable=self.song_title_var, font=self.title_font, anchor="w")
        self.song_title_label.pack(fill="x", padx=10, pady=(0, 2))

        WAVEFORM_HEIGHT = 70
        self.waveform_frame = ctk.CTkFrame(self.visual_frame, corner_radius=0, height=WAVEFORM_HEIGHT)
        self.waveform_frame.pack(fill="x", expand=False, padx=10, pady=(0, 1), ipady=0)

        OSCILLOSCOPE_HEIGHT = 35
        self.oscilloscope_frame = ctk.CTkFrame(self.visual_frame, corner_radius=0, height=OSCILLOSCOPE_HEIGHT)
        self.oscilloscope_frame.pack(fill="x", expand=False, padx=10, pady=(1, 5), ipady=0)

        self.spacer_frame = ctk.CTkFrame(self.visual_frame, height=0) # Color set by apply_theme
        self.spacer_frame.pack(fill="both", expand=True, pady=0, padx=0)

        self.slider_frame = ctk.CTkFrame(self.visual_frame, corner_radius=0)
        self.slider_frame.pack(fill="x", pady=(0,5), padx=10)

        self.song_slider = ctk.CTkSlider(self.slider_frame, from_=0, to=100, command=self.slide_song, variable=ctk.DoubleVar())
        self.song_slider.pack(fill="x", pady=5)
        self.song_slider.bind("<ButtonPress-1>", self.slider_start_scroll)
        self.song_slider.bind("<ButtonRelease-1>", self.slider_stop_scroll)

        self.time_frame = ctk.CTkFrame(self.slider_frame, corner_radius=0)
        self.time_frame.pack(fill="x")
        self.current_time_label = ctk.CTkLabel(self.time_frame, text="00:00", font=self.normal_font)
        self.current_time_label.pack(side="left", padx=(0, 5))
        self.total_time_label = ctk.CTkLabel(self.time_frame, text="00:00", font=self.normal_font)
        self.total_time_label.pack(side="right", padx=(5, 0))

    def create_waveform_display(self):
        """Create the Matplotlib canvas for the static waveform."""
        # Canvas widget styling (bg) is handled by apply_theme indirectly via frame bg
        self.mpl_canvas_widget_wave = FigureCanvasTkAgg(self.fig_wave, master=self.waveform_frame)
        tk_widget = self.mpl_canvas_widget_wave.get_tk_widget()
        tk_widget.pack(fill="both", expand=True)
        # Connect mouse events for seeking
        self.fig_wave.canvas.mpl_connect('button_press_event', self.on_waveform_press)
        self.fig_wave.canvas.mpl_connect('motion_notify_event', self.on_waveform_motion)
        tk_widget.bind('<ButtonRelease-1>', self.on_waveform_release)
        tk_widget.bind('<Leave>', self.on_waveform_leave)

    def create_oscilloscope_display(self):
        """Create the Matplotlib canvas for the oscilloscope."""
        self.mpl_canvas_widget_osc = FigureCanvasTkAgg(self.fig_osc, master=self.oscilloscope_frame)
        tk_widget_osc = self.mpl_canvas_widget_osc.get_tk_widget()
        tk_widget_osc.pack(fill="both", expand=True)

    def draw_initial_placeholder(self, ax, fig, border_color, message="", text_color=None):
        """Draws a placeholder message on a Matplotlib plot area using theme colors."""
        if not ax or not fig or not fig.canvas: return
        try:
            theme = self.themes[self.current_theme_name]
            bg_color = theme['plot_bg']
            if text_color is None: text_color = theme['plot_text'] # Use theme text color if not specified

            ax.clear(); self._configure_axes(ax, fig, border_color, bg_color) # Pass bg_color
            font_size = 7 if fig == self.fig_osc else 9
            if message: ax.text(0.5, 0.5, message, ha='center', va='center', fontsize=font_size, color=text_color, transform=ax.transAxes, fontfamily='SF Mono') # Use text_color
            if ax == self.ax_osc: ax.set_ylim(-1.1, 1.1)
            fig.canvas.draw_idle()
            if ax == self.ax_wave: self.position_indicator_line_wave = None
        except Exception as e: print(f"Error drawing placeholder: {e}")

    def create_controls(self):
        """Create playback control buttons and volume slider."""
        # Colors set by apply_theme
        self.buttons_frame = ctk.CTkFrame(self.controls_frame, corner_radius=0)
        self.buttons_frame.pack(pady=(5,0), anchor="center")
        # Button colors will be set by apply_theme
        button_kwargs = {"font": self.button_font, "border_width": 0, "corner_radius": 0, "width": 35, "height": 28}
        self.prev_button = ctk.CTkButton(self.buttons_frame, text="◄◄", command=self.previous_song, **button_kwargs); self.prev_button.grid(row=0, column=0, padx=4)
        self.play_button = ctk.CTkButton(self.buttons_frame, text="▶", command=self.play, **button_kwargs); self.play_button.grid(row=0, column=1, padx=4)
        self.pause_button = ctk.CTkButton(self.buttons_frame, text="II", command=self.pause, **button_kwargs); self.pause_button.grid(row=0, column=2, padx=4)
        self.next_button = ctk.CTkButton(self.buttons_frame, text="►►", command=self.next_song, **button_kwargs); self.next_button.grid(row=0, column=3, padx=4)

        # Extra controls frame (Theme Toggle, MIX, LOOP, VOL, Slider)
        self.extra_frame = ctk.CTkFrame(self.controls_frame, corner_radius=0)
        self.extra_frame.pack(pady=(2,5), anchor="center")

        # Define base style for these buttons (Loop, Vol, Mix)
        extra_button_kwargs = {"font": self.normal_font, "border_width": 0, "corner_radius": 0, "width": 65, "height": 25}
        # Define style for the theme toggle button (needs to be wide enough for MN-1)
        theme_button_kwargs = {"font": self.normal_font, "border_width": 0, "corner_radius": 0, "width": 65, "height": 25}

        # Grid Layout: Theme(0), Mix(1), Loop(2), Vol(3), Slider(4)

        # Create Theme Toggle Button (First position)
        self.theme_toggle_button = ctk.CTkButton(
            self.extra_frame,
            text="MN-1", # <<< CHANGED Initial text
            command=self.toggle_theme,
            **theme_button_kwargs # Use the wider button style
        )
        self.theme_toggle_button.grid(row=0, column=0, padx=3) # Column 0

        # Create Mix Button (Second position)
        self.mix_button = ctk.CTkButton(self.extra_frame, text="MIX", command=self.toggle_mix, **extra_button_kwargs)
        self.mix_button.grid(row=0, column=1, padx=3) # Column 1

        # Create Loop Button (Third position)
        self.loop_button = ctk.CTkButton(self.extra_frame, text="LOOP", command=self.toggle_loop, **extra_button_kwargs)
        self.loop_button.grid(row=0, column=2, padx=3) # Column 2

        # Create Vol Button (Fourth position)
        self.volume_button = ctk.CTkButton(self.extra_frame, text="VOL", command=self.toggle_mute, **extra_button_kwargs)
        self.volume_button.grid(row=0, column=3, padx=3) # Column 3

        # Create Volume Slider (Fifth position)
        self.volume_slider = ctk.CTkSlider(self.extra_frame, from_=0, to=1, number_of_steps=100, command=self.volume_adjust, width=90, height=18);
        self.volume_slider.set(0.5)
        self.volume_slider.grid(row=0, column=4, padx=(3, 10), pady=(0,3)) # Column 4, added padding after

    def create_tracklist_area(self):
        """Create the tracklist display and management buttons."""
        # Colors set by apply_theme
        self.playlist_label_frame = ctk.CTkFrame(self.right_frame, corner_radius=0)
        self.playlist_label_frame.pack(fill="x", pady=5)

        self.tracklist_label = ctk.CTkLabel(self.playlist_label_frame, text="TRACKLIST", font=self.title_font)
        self.tracklist_label.pack(anchor="center")

        self.playlist_frame = ctk.CTkFrame(self.right_frame, corner_radius=0)
        self.playlist_frame.pack(fill="both", expand=True, padx=5, pady=0)

        # Scrollable frame colors set by apply_theme
        self.playlist_scrollable = ctk.CTkScrollableFrame(self.playlist_frame, label_fg_color=COLOR_BLACK, label_text_color=COLOR_BLACK) # Dummy colors initially
        self.playlist_scrollable.pack(fill="both", expand=True)
        self.playlist_entries = []

        self.playlist_buttons_frame = ctk.CTkFrame(self.right_frame, corner_radius=0)
        self.playlist_buttons_frame.pack(fill="x", pady=(5,10))
        playlist_button_kwargs = {"font": self.normal_font, "border_width": 0, "corner_radius": 0, "width": 70, "height": 25}
        self.load_button = ctk.CTkButton(self.playlist_buttons_frame, text="LOAD", command=self.add_songs, **playlist_button_kwargs); self.load_button.pack(side="left", padx=5, expand=True)
        self.remove_button = ctk.CTkButton(self.playlist_buttons_frame, text="REMOVE", command=self.remove_song, **playlist_button_kwargs); self.remove_button.pack(side="left", padx=5, expand=True)
        self.clear_button = ctk.CTkButton(self.playlist_buttons_frame, text="CLEAR", command=self.clear_playlist, **playlist_button_kwargs); self.clear_button.pack(side="left", padx=5, expand=True)


    # --- Theme Switching Logic ---
    def toggle_theme(self):
        """Cycles through defined themes."""
        try:
            current_index = self.theme_cycle.index(self.current_theme_name)
            next_index = (current_index + 1) % len(self.theme_cycle)
            self.current_theme_name = self.theme_cycle[next_index]
        except ValueError:
            # Fallback if current theme isn't in cycle (shouldn't happen)
            self.current_theme_name = self.theme_cycle[0]

        print(f"Switching theme to: {self.current_theme_name}")
        self.apply_theme()

    def apply_theme(self):
        """Applies the currently selected theme to all UI elements."""
        theme = self.themes[self.current_theme_name]

        # <<< CHANGED: Theme button text is now always "MN-1"
        theme_button_display_text = "MN-1"

        try:
            # Root
            self.root.configure(fg_color=theme["root_bg"])

            # Frames
            for frame in [self.player_frame, self.left_frame, self.right_frame,
                          self.controls_frame, self.visual_frame, self.info_frame,
                          self.waveform_frame, self.oscilloscope_frame, self.spacer_frame,
                          self.slider_frame, self.time_frame, self.playlist_label_frame,
                          self.playlist_frame, self.playlist_buttons_frame,
                          self.buttons_frame, self.extra_frame]:
                if frame and frame.winfo_exists():
                    frame.configure(fg_color=theme["frame_bg"])

            # Labels
            for label, text_color_key in [(self.song_title_label, "label_fg"),
                                          (self.current_time_label, "label_fg"),
                                          (self.total_time_label, "label_fg"),
                                          (self.tracklist_label, "label_fg"),
                                          ]:
                 if label and label.winfo_exists():
                     label.configure(fg_color=theme["label_bg"], text_color=theme[text_color_key])

            # Buttons (Main Playback)
            for btn in [self.prev_button, self.play_button, self.pause_button, self.next_button]:
                 if btn and btn.winfo_exists():
                     btn.configure(fg_color=theme["button_fg"], text_color=theme["button_text"], hover_color=theme["button_hover"])

            # Buttons (Extra Controls & Playlist)
            extra_buttons = [self.mix_button, self.loop_button, self.volume_button,
                             self.theme_toggle_button,
                             self.load_button, self.remove_button, self.clear_button]
            for btn in extra_buttons:
                 if btn and btn.winfo_exists():
                     btn.configure(fg_color=theme["button_fg"], # Apply bg color from theme
                                   hover_color=theme["button_hover"]) # Apply hover color
                     # Apply specific text color for theme button, default for others
                     if btn is self.theme_toggle_button:
                         btn.configure(text_color=theme["theme_toggle_fg"])
                     else:
                         btn.configure(text_color=theme["button_text"])


            # Theme Toggle Button Specific Styling (Text) - Text color set above
            if self.theme_toggle_button and self.theme_toggle_button.winfo_exists():
                self.theme_toggle_button.configure(
                    text=theme_button_display_text, # <<< Set text to "MN-1"
                )

            # Sliders
            if self.song_slider and self.song_slider.winfo_exists():
                self.song_slider.configure(fg_color=theme["slider_bg"], progress_color=theme["slider_progress"],
                                           button_color=theme["slider_button"], button_hover_color=theme["slider_button_hover"])
            if self.volume_slider and self.volume_slider.winfo_exists():
                 self.volume_slider.configure(fg_color=theme["slider_bg"], progress_color=theme["slider_progress"],
                                              button_color=theme["slider_button"], button_hover_color=theme["slider_button_hover"])

            # Scrollable Frame
            if self.playlist_scrollable and self.playlist_scrollable.winfo_exists():
                self.playlist_scrollable.configure(fg_color=theme["list_bg"],
                                                   scrollbar_button_color=theme["list_scrollbar"],
                                                   scrollbar_button_hover_color=theme["list_scrollbar_hover"])

            # --- Re-apply State-Dependent Colors (Text colors based on state) ---
            # Mute Button
            mute_color = theme["muted_fg"] if self.muted else theme["inactive_button_fg"]
            mute_text = "MUTED" if self.muted else "VOL"
            if self.volume_button and self.volume_button.winfo_exists():
                 self.volume_button.configure(text_color=mute_color, text=mute_text)

            # Mix Button
            mix_color = theme["active_button_fg"] if self.shuffle_state else theme["inactive_button_fg"]
            if self.mix_button and self.mix_button.winfo_exists():
                 self.mix_button.configure(text_color=mix_color)

            # Loop Button
            loop_color = theme["active_button_fg"] if self.loop_state > 0 else theme["inactive_button_fg"]
            if self.loop_button and self.loop_button.winfo_exists():
                 self.loop_button.configure(text_color=loop_color)

            # Tracklist Selection
            selected_idx = -1
            for i, entry in enumerate(self.playlist_entries):
                 # Check if entry still exists before accessing 'selected'
                 if entry and entry.get("frame") and entry["frame"].winfo_exists() and entry.get("selected"):
                    selected_idx = i
                    break
            if selected_idx != -1:
                 self.select_song(selected_idx) # Re-apply selection colors with new theme
            else: # Ensure all items have default theme color if none selected
                 for entry in self.playlist_entries:
                    try:
                        # Add checks before configuring potentially destroyed widgets
                        if entry and entry.get("label") and entry["label"].winfo_exists():
                            entry["label"].configure(fg_color=theme["list_bg"], text_color=theme["list_fg"])
                        if entry and entry.get("frame") and entry["frame"].winfo_exists():
                            entry["frame"].configure(fg_color=theme["list_bg"])
                    except Exception: pass # Ignore if widget destroyed


            # --- Update Matplotlib Plots ---
            # Waveform Plot
            if self.ax_wave and self.fig_wave and self.fig_wave.canvas:
                self._configure_axes(self.ax_wave, self.fig_wave, theme["plot_spine"], theme["plot_bg"])
                if self.waveform_peak_data is not None and len(self.waveform_peak_data) > 0:
                     self.draw_static_matplotlib_waveform() # Redraw with new colors
                     # No need to redraw indicator here, draw_static_matplotlib_waveform handles it
                else:
                     # Redraw placeholder with new theme colors
                     placeholder_msg = self.song_title_var.get() if "ERROR" in self.song_title_var.get() or "FAILED" in self.song_title_var.get() else ("LOAD A SONG" if not self.current_song else "NO WAVEFORM DATA")
                     self.draw_initial_placeholder(self.ax_wave, self.fig_wave, theme["plot_spine"], placeholder_msg, theme["plot_text"])
                self.fig_wave.canvas.draw_idle()

            # Oscilloscope Plot
            if self.ax_osc and self.fig_osc and self.fig_osc.canvas:
                 self._configure_axes(self.ax_osc, self.fig_osc, theme["plot_osc_main"], theme["plot_bg"]) # Use accent color for border too
                 if self.playing_state and self.raw_sample_data is not None:
                     self.update_oscilloscope() # Will redraw with new colors
                 else:
                      self.draw_initial_placeholder(self.ax_osc, self.fig_osc, theme["plot_osc_main"], "", theme["plot_text"]) # Redraw placeholder
                 self.fig_osc.canvas.draw_idle()

        except Exception as e:
            print(f"Error applying theme '{self.current_theme_name}': {e}")
            traceback.print_exc()

    # --- Helper to Update Title Display ---
    def _update_display_title(self, base_title=""):
        """Updates the song_title_var based on current state."""
        prefix = ""
        title = base_title if base_title else os.path.basename(self.current_song) if self.current_song else "NO SONG LOADED"

        if self.has_error:
            prefix = "[ERROR] "
        elif self.is_loading:
             prefix = "[LOADING...] "
        elif self.is_generating_waveform:
            prefix = "[GENERATING...] "
        elif self.playing_state:
            prefix = "[PLAYING] "
        elif self.paused:
            prefix = "[PAUSED] "
        elif self.current_song: # Song loaded but stopped
             pass
        else: # No song loaded / Idle
            title = "NO SONG LOADED"

        # Handle playlist empty state explicitly
        if not self.songs_list and not self.current_song:
            title = "TRACKLIST EMPTY"

        self.song_title_var.set(f"{prefix}{title}")

    # --- Playlist Management Methods ---
    def add_songs(self):
        """Opens file dialog to add songs to the tracklist."""
        songs = filedialog.askopenfilenames(title="Select Audio Files", filetypes=(("Audio Files", "*.mp3 *.flac"), ("MP3 Files", "*.mp3"), ("FLAC Files", "*.flac"), ("All Files", "*.*")))
        added_count = 0
        if not songs: return

        for song_path in songs:
            if os.path.exists(song_path):
                 try:
                    file_ext = os.path.splitext(song_path)[1].lower()
                    # Basic check using mutagen without storing the object
                    if file_ext == ".mp3": MP3(song_path)
                    elif file_ext == ".flac": FLAC_MUTAGEN(song_path)
                    else: continue # Skip unsupported

                    song_name = os.path.basename(song_path)
                    # Add only if not already present
                    if song_path not in self.songs_list:
                        self.add_song_to_playlist(song_name, song_path) # Adds UI element
                        self.songs_list.append(song_path)
                        added_count += 1
                    else: print(f"Song already in tracklist: {song_name}")
                 except Exception as e: print(f"Skipping invalid/unreadable file: {os.path.basename(song_path)} - Error: {e}")
            else: print(f"Skipping non-existent file: {song_path}")

        if added_count > 0: print(f"{added_count} TRACK(S) ADDED")
        elif added_count == 0 and songs: print("NO NEW TRACKS ADDED")

        if added_count > 0 and len(self.songs_list) == added_count:
            # If this is the first song added, update title from empty
            if self.song_title_var.get() == "TRACKLIST EMPTY":
                 self._update_display_title(base_title="NO SONG LOADED") # Change state
            # Auto-select the first song if none is loaded/playing
            if not self.current_song and not self.playing_state and not self.paused:
                self.select_song(0)


    def add_song_to_playlist(self, song_name, song_path):
        """Adds a single song entry to the tracklist UI (styled by theme)."""
        index = len(self.playlist_entries)
        theme = self.themes[self.current_theme_name]

        song_frame = ctk.CTkFrame(self.playlist_scrollable, fg_color=theme["list_bg"], corner_radius=0)
        song_frame.pack(fill="x", pady=1, ipady=1)

        song_label = ctk.CTkLabel(song_frame, text=song_name, font=self.normal_font, fg_color=theme["list_bg"], text_color=theme["list_fg"], anchor="w", justify="left", cursor="hand2")
        song_label.pack(fill="x", padx=5)

        # Bind selection and double-click play
        song_label.bind("<Button-1>", lambda e, idx=index: self.select_song(idx))
        song_label.bind("<Double-Button-1>", lambda e, idx=index: self.play_selected_song_by_index(idx))

        self.playlist_entries.append({"frame": song_frame, "label": song_label, "selected": False, "index": index})

    def select_song(self, index):
        """Highlights the selected song in the tracklist UI using theme colors."""
        if not (0 <= index < len(self.playlist_entries)): return

        theme = self.themes[self.current_theme_name]
        selected_color = theme["list_selected_fg"]
        default_fg_color = theme["list_fg"]
        bg_color = theme["list_bg"]

        for i, entry in enumerate(self.playlist_entries):
            is_selected = (i == index)
            text_color = selected_color if is_selected else default_fg_color
            try:
                # Check widgets exist before configuring
                if entry and entry.get("frame") and entry["frame"].winfo_exists():
                    entry["frame"].configure(fg_color=bg_color) # Background always theme list bg
                if entry and entry.get("label") and entry["label"].winfo_exists():
                    entry["label"].configure(fg_color=bg_color, text_color=text_color)
            except Exception as e:
                # Ignore errors if widget was destroyed (e.g., during clear playlist)
                if "invalid command name" not in str(e):
                    print(f"Error configuring tracklist entry {i}: {e}")
            # Update selected state even if widget doesn't exist (for internal logic)
            if entry: entry["selected"] = is_selected


    def play_selected_song_by_index(self, index):
        """Plays the song at the specified index."""
        if 0 <= index < len(self.songs_list):
             self.abort_waveform_generation()
             self.current_song_index = index
             self.select_song(index) # Select before playing
             self.play_music() # Play from start
        else: print(f"Warning: play_selected_song_by_index index {index} out of range.");

    def play_selected_song(self, event=None):
        """Plays the currently selected song, or the first if none selected."""
        selected_index = -1
        for index, entry in enumerate(self.playlist_entries):
             # Check entry exists before accessing 'selected'
            if entry and entry.get("frame") and entry["frame"].winfo_exists() and entry.get("selected"):
                selected_index = index
                break

        if selected_index != -1:
            self.play_selected_song_by_index(selected_index)
        elif self.playlist_entries: # If no selection, play first
             print("No song selected, playing first song.")
             self.play_selected_song_by_index(0)
        else: # No songs in list
             print("TRACKLIST EMPTY")
             self._update_display_title()

    def remove_song(self):
        """Removes the currently selected song from the tracklist."""
        removed_index = -1
        is_current_song_removed = False
        for i, entry in enumerate(self.playlist_entries):
             # Check entry exists before accessing 'selected'
             if entry and entry.get("frame") and entry["frame"].winfo_exists() and entry.get("selected"):
                removed_index = i
                break

        if removed_index == -1: print("NO TRACK SELECTED"); return

        # Check if the song being removed is the one currently loaded/playing
        current_song_path = self.songs_list[removed_index] if removed_index < len(self.songs_list) else None
        if current_song_path and removed_index == self.current_song_index and self.current_song == current_song_path:
             is_current_song_removed = True

        # Remove from UI and data lists
        if removed_index < len(self.playlist_entries):
             try:
                 if self.playlist_entries[removed_index]["frame"].winfo_exists():
                     self.playlist_entries[removed_index]["frame"].destroy()
             except Exception: pass # Ignore destroy error
             removed_entry = self.playlist_entries.pop(removed_index)

        if removed_index < len(self.songs_list):
            removed_song_path = self.songs_list.pop(removed_index)
            print(f"Removed: {os.path.basename(removed_song_path)}")
        else:
             print("Warning: Index mismatch during remove.") # Should ideally not happen
             return


        # Re-index remaining entries and re-bind events
        for i in range(removed_index, len(self.playlist_entries)):
            entry = self.playlist_entries[i]
            entry["index"] = i # Update internal index
            # Re-bind with the new index if label exists
            try:
                if entry and entry.get("label") and entry["label"].winfo_exists():
                    entry["label"].unbind("<Button-1>")
                    entry["label"].unbind("<Double-Button-1>")
                    entry["label"].bind("<Button-1>", lambda e, idx=i: self.select_song(idx))
                    entry["label"].bind("<Double-Button-1>", lambda e, idx=i: self.play_selected_song_by_index(idx))
            except Exception as e:
                 print(f"Error re-binding tracklist entry {i}: {e}")


        # Handle player state if the currently loaded song was removed
        if is_current_song_removed:
            self.stop() # Stop playback
            self.current_song = "" # Clear current song info
            self.has_error = False; self.is_loading = False; self.is_generating_waveform = False;
            self._update_display_title(base_title="NO SONG LOADED") # Reset title
            theme = self.themes[self.current_theme_name]
            # Clear visuals
            self.draw_initial_placeholder(self.ax_wave, self.fig_wave, theme['plot_spine'], "TRACK REMOVED")
            self.draw_initial_placeholder(self.ax_osc, self.fig_osc, theme['plot_osc_main'], "")
            self.raw_sample_data = None; self.waveform_peak_data = None; self.sample_rate = None
            # Reset time/slider
            self.song_length = 0; self.total_time_label.configure(text="00:00"); self.current_time_label.configure(text="00:00"); self.song_slider.set(0); self.song_slider.configure(to=100)

        # Adjust current_song_index if necessary
        if len(self.songs_list) == 0:
            # If list is now empty
            self.current_song_index = 0
            if not is_current_song_removed: # Clear state if it wasn't cleared above
                 self.current_song = ""
                 self.has_error = False; self.is_loading = False; self.is_generating_waveform = False;
                 self._update_display_title(base_title="TRACKLIST EMPTY")
                 theme = self.themes[self.current_theme_name]
                 self.draw_initial_placeholder(self.ax_wave, self.fig_wave, theme['plot_spine'], "TRACKLIST EMPTY")
                 self.draw_initial_placeholder(self.ax_osc, self.fig_osc, theme['plot_osc_main'], "")
                 self.raw_sample_data = None; self.waveform_peak_data = None; self.sample_rate = None; self.song_length = 0; self.total_time_label.configure(text="00:00"); self.current_time_label.configure(text="00:00"); self.song_slider.set(0); self.song_slider.configure(to=100)
        elif removed_index < self.current_song_index:
             # If removed item was before the current song, decrement index
             self.current_song_index -= 1
        elif removed_index == self.current_song_index and not is_current_song_removed:
             # If removed item was at the current index but WASN'T the loaded song,
             # the index might now be out of bounds or pointing wrong.
             # Clamp it to the new list size.
             self.current_song_index = min(removed_index, len(self.songs_list) - 1)
        # else: index remains valid or was handled by is_current_song_removed

        # Reselect the item at the (potentially adjusted) current_song_index
        if not is_current_song_removed and self.songs_list:
            new_index_to_select = min(self.current_song_index, len(self.playlist_entries) - 1)
            if new_index_to_select >= 0:
                self.select_song(new_index_to_select)


    def clear_playlist(self):
        """Removes all songs from the tracklist and stops playback."""
        self.stop(); # Stop playback first
        # Destroy UI elements
        for entry in self.playlist_entries:
            try:
                 if entry and entry.get("frame") and entry["frame"].winfo_exists():
                     entry["frame"].destroy()
            except Exception: pass # Ignore if already destroyed
        # Clear data structures
        self.playlist_entries.clear(); self.songs_list.clear(); self.current_song_index = 0; self.current_song = ""
        # Reset state flags
        self.has_error = False; self.is_loading = False; self.is_generating_waveform = False;
        self._update_display_title(base_title="TRACKLIST CLEARED")
        # Clear waveform/sample data
        self.waveform_peak_data = None; self.raw_sample_data = None; self.sample_rate = None
        # Reset visuals and time
        theme = self.themes[self.current_theme_name]
        self.draw_initial_placeholder(self.ax_wave, self.fig_wave, theme['plot_spine'], "TRACKLIST CLEARED")
        self.draw_initial_placeholder(self.ax_osc, self.fig_osc, theme['plot_osc_main'], "")
        self.total_time_label.configure(text="00:00"); self.current_time_label.configure(text="00:00"); self.song_slider.set(0); self.song_slider.configure(to=100)
        self.song_length = 0
        # Set final title state
        self._update_display_title(base_title="TRACKLIST EMPTY")


    # --- Playback Control Methods --- (play method updated above)
    # --- ... rest of the methods ... ---

# --- Main Execution Block ---
if __name__ == "__main__":
    print("Starting MN-1 Music Player...")
    try:
        # DPI awareness for sharper UI on Windows
        if os.name == 'nt':
             try: from ctypes import windll; windll.shcore.SetProcessDpiAwareness(1)
             except Exception as e: print(f"Could not set DPI awareness: {e}")

        # Removed ctk.set_appearance_mode - handled by internal theme logic now
        root = ctk.CTk()
        player = MN1MusicPlayer (root)
        root.mainloop()

    except Exception as main_error:
        # Catch and display fatal errors
        print("\n--- FATAL APPLICATION ERROR ---"); print(f"Error: {main_error}"); traceback.print_exc()
        try:
             # Try to show a simple Tkinter error box as a last resort
             import tkinter as tk; from tkinter import messagebox
             root_err = tk.Tk(); root_err.withdraw(); messagebox.showerror("Fatal Error", f"Critical error:\n\n{main_error}\n\nSee console."); root_err.destroy()
        except Exception as tk_error: print(f"(Tkinter error msg failed: {tk_error})")
        input("Press Enter to exit console.")