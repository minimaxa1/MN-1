import customtkinter as ctk
from tkinter import filedialog
import pygame
import os
from mutagen.mp3 import MP3
from mutagen.flac import FLAC as FLAC_MUTAGEN
# --- Added for OGG/WAV metadata ---
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE
# --- End Add ---
import time
import random
import threading
import numpy as np
import soundfile as sf # Using soundfile for waveform generation
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import traceback
import subprocess # Keep for potential future use or if needed by other libs
import sys # Keep for sys module usage

# --- Color Definitions ---
COLOR_BLACK = "#000000"; COLOR_WHITE = "#FFFFFF"; COLOR_NEAR_WHITE = "#F5F5F5"
COLOR_DEEP_RED = "#8B0000"; COLOR_LIGHT_RED_HOVER = "#A52A2A"; COLOR_BRIGHT_RED = "#FF0000"
COLOR_DARK_GRAY = "#333333"; COLOR_LIGHT_GRAY = "#D3D3D3"; COLOR_MID_GRAY = "#404040"
COLOR_DARKER_MID_GRAY = "#505050"; COLOR_LIGHTER_MID_GRAY = "#666666"
COLOR_GOLD = "#FFD700"; COLOR_LIGHT_GOLD = "#F0E68C"; COLOR_DARK_GOLD = "#B8860B"
COLOR_ORANGE = "#FFA500"; COLOR_LIGHT_ORANGE = "#FFDAB9"; COLOR_DARK_ORANGE = "#CD853F"
COLOR_PURPLE = "#8A2BE2"; COLOR_LIGHT_PURPLE = "#D8BFD8"; COLOR_DARK_PURPLE = "#4B0082"
COLOR_GREEN = "#32CD32"; COLOR_LIGHT_GREEN = "#90EE90"; COLOR_DARK_GREEN = "#006400"
COLOR_BLUE = "#00BFFF"; COLOR_LIGHT_BLUE = "#ADD8E6"; COLOR_DARK_BLUE = "#00008B"
COLOR_SUNSET_L1 = "#4D1F18"; COLOR_SUNSET_L2 = "#8C3B2E"; COLOR_SUNSET_L3 = "#C84C2F"
COLOR_SUNSET_L4 = "#D6704F"; COLOR_SUNSET_L5 = "#E09A5F"; COLOR_SUNSET_L6 = "#EEDAA8"
COLOR_OCEAN_L1 = "#172B40"; COLOR_OCEAN_L2 = "#1E3C58"; COLOR_OCEAN_L3 = "#3A6EA5"
COLOR_OCEAN_L4 = "#4C8BC9"; COLOR_OCEAN_L5 = "#4CAF8B"; COLOR_OCEAN_L6 = "#88C0B3"
COLOR_EMBER_L1 = "#4A6A5A"; COLOR_EMBER_L2 = "#9ABCA7"; COLOR_EMBER_L3 = "#FF7F50"
COLOR_EMBER_L4 = "#FFA07A"; COLOR_EMBER_L5 = "#FFDAB9"; COLOR_EMBER_L6 = "#FFE4E1"
COLOR_CYBERPUNK_L1 = "#10101A"; COLOR_CYBERPUNK_L2 = "#2A0944"; COLOR_CYBERPUNK_L3 = "#00F0FF"
COLOR_CYBERPUNK_L4 = "#E01E5A"; COLOR_CYBERPUNK_L5 = "#FFD300"; COLOR_CYBERPUNK_L6 = "#C0C0FF"
COLOR_SILVER_L1 = COLOR_NEAR_WHITE; COLOR_SILVER_L2 = "#D8D8D8"; COLOR_SILVER_L3 = "#C0C0C0"
COLOR_SILVER_L4 = "#A0A0A0"; COLOR_SILVER_L5 = "#404040"; COLOR_SILVER_L6 = COLOR_BLACK
COLOR_DARK_RED_DIM = "#600000"
COLOR_MID_DARK_GRAY = "#2A2A2A"
COLOR_VERY_LIGHT_GRAY = "#EEEEEE"
COLOR_VERY_DARK_GRAY = "#1E1E1E"
COLOR_DARK_GOLD_DIM = "#805306"
COLOR_DARK_ORANGE_DIM = "#8B4513" # SaddleBrown
COLOR_DARK_PURPLE_DIM = "#301934" # DarkPurple
COLOR_DARK_GREEN_DIM = "#004d00"
COLOR_DARK_BLUE_DIM = "#000050"

# --- Theme Palettes ---
THEMES = {
    "dark": {
        "L1_bg": COLOR_BLACK, "L2_element_dark": COLOR_MID_DARK_GRAY, "L3_accent_primary": COLOR_DEEP_RED,
        "L4_hover_bg": COLOR_DARK_GRAY, "L5_accent_secondary": COLOR_BRIGHT_RED, "L6_text_light": COLOR_WHITE,
        "slider_button": COLOR_SILVER_L3, "slider_button_hover": COLOR_BRIGHT_RED,
        "plot_bg": COLOR_BLACK, "plot_wave_main": COLOR_WHITE, "plot_osc_main": COLOR_DEEP_RED,
        "plot_wave_indicator": COLOR_BRIGHT_RED, "plot_spine": COLOR_WHITE, "plot_text": COLOR_WHITE,
        "list_scrollbar": COLOR_DARK_GRAY, "list_scrollbar_hover": COLOR_WHITE,
    },
    "light": {
        "L1_bg": COLOR_WHITE, "L2_element_dark": COLOR_LIGHT_GRAY, "L3_accent_primary": COLOR_DEEP_RED,
        "L4_hover_bg": COLOR_VERY_LIGHT_GRAY, "L5_accent_secondary": COLOR_BRIGHT_RED, "L6_text_light": COLOR_BLACK,
        "slider_button": COLOR_BLACK, "slider_button_hover": COLOR_DEEP_RED,
        "plot_bg": COLOR_WHITE, "plot_wave_main": COLOR_DARK_GRAY, "plot_osc_main": COLOR_DEEP_RED, # Changed plot_wave_main from LIGHT_GRAY
        "plot_wave_indicator": COLOR_BRIGHT_RED, "plot_spine": COLOR_BLACK, "plot_text": COLOR_BLACK,
        "list_scrollbar": COLOR_DEEP_RED, "list_scrollbar_hover": COLOR_BLACK,
    },
    "grey": {
        "L1_bg": COLOR_MID_GRAY, "L2_element_dark": COLOR_DARKER_MID_GRAY, "L3_accent_primary": COLOR_DEEP_RED,
        "L4_hover_bg": COLOR_LIGHTER_MID_GRAY, "L5_accent_secondary": COLOR_BRIGHT_RED, "L6_text_light": COLOR_WHITE,
        "slider_button": COLOR_SILVER_L3, "slider_button_hover": COLOR_BRIGHT_RED,
        "plot_bg": COLOR_MID_GRAY, "plot_wave_main": COLOR_SILVER_L3, "plot_osc_main": COLOR_DEEP_RED,
        "plot_wave_indicator": COLOR_BRIGHT_RED, "plot_spine": COLOR_SILVER_L3, "plot_text": COLOR_SILVER_L3,
        "list_scrollbar": COLOR_DEEP_RED, "list_scrollbar_hover": COLOR_WHITE,
    },
     "red": {
        "L1_bg": COLOR_DEEP_RED, "L2_element_dark": COLOR_DARK_RED_DIM, "L3_accent_primary": COLOR_WHITE,
        "L4_hover_bg": COLOR_LIGHT_RED_HOVER, "L5_accent_secondary": COLOR_LIGHT_GRAY, "L6_text_light": COLOR_WHITE,
        "slider_button": COLOR_WHITE, "slider_button_hover": COLOR_LIGHT_GRAY,
        "plot_bg": COLOR_DEEP_RED, "plot_wave_main": COLOR_WHITE, "plot_osc_main": COLOR_WHITE,
        "plot_wave_indicator": COLOR_BLACK, "plot_spine": COLOR_WHITE, "plot_text": COLOR_WHITE,
        "list_scrollbar": COLOR_WHITE, "list_scrollbar_hover": COLOR_BLACK,
    },
     "gold": {
        "L1_bg": COLOR_BLACK, "L2_element_dark": COLOR_DARK_GOLD_DIM, "L3_accent_primary": COLOR_GOLD,
        "L4_hover_bg": COLOR_DARK_GOLD, "L5_accent_secondary": COLOR_LIGHT_GOLD, "L6_text_light": COLOR_NEAR_WHITE,
        "slider_button": COLOR_NEAR_WHITE, "slider_button_hover": COLOR_LIGHT_GOLD,
        "plot_bg": COLOR_BLACK, "plot_wave_main": COLOR_GOLD, "plot_osc_main": COLOR_LIGHT_GOLD,
        "plot_wave_indicator": COLOR_LIGHT_GOLD, "plot_spine": COLOR_DARK_GOLD, "plot_text": COLOR_NEAR_WHITE,
        "list_scrollbar": COLOR_DARK_GOLD_DIM, "list_scrollbar_hover": COLOR_LIGHT_GOLD,
    },
    "orange": {
        "L1_bg": COLOR_BLACK, "L2_element_dark": COLOR_DARK_ORANGE_DIM, "L3_accent_primary": COLOR_ORANGE,
        "L4_hover_bg": COLOR_DARK_ORANGE, "L5_accent_secondary": COLOR_LIGHT_ORANGE, "L6_text_light": COLOR_NEAR_WHITE,
        "slider_button": COLOR_NEAR_WHITE, "slider_button_hover": COLOR_LIGHT_ORANGE,
        "plot_bg": COLOR_BLACK, "plot_wave_main": COLOR_ORANGE, "plot_osc_main": COLOR_LIGHT_ORANGE,
        "plot_wave_indicator": COLOR_LIGHT_ORANGE, "plot_spine": COLOR_DARK_ORANGE, "plot_text": COLOR_NEAR_WHITE,
        "list_scrollbar": COLOR_DARK_ORANGE_DIM, "list_scrollbar_hover": COLOR_LIGHT_ORANGE,
    },
    "purple": {
        "L1_bg": COLOR_BLACK, "L2_element_dark": COLOR_DARK_PURPLE_DIM, "L3_accent_primary": COLOR_PURPLE,
        "L4_hover_bg": COLOR_DARK_PURPLE, "L5_accent_secondary": COLOR_LIGHT_PURPLE, "L6_text_light": COLOR_NEAR_WHITE,
        "slider_button": COLOR_NEAR_WHITE, "slider_button_hover": COLOR_LIGHT_PURPLE,
        "plot_bg": COLOR_BLACK, "plot_wave_main": COLOR_PURPLE, "plot_osc_main": COLOR_LIGHT_PURPLE,
        "plot_wave_indicator": COLOR_LIGHT_PURPLE, "plot_spine": COLOR_DARK_PURPLE, "plot_text": COLOR_NEAR_WHITE,
        "list_scrollbar": COLOR_DARK_PURPLE_DIM, "list_scrollbar_hover": COLOR_LIGHT_PURPLE,
    },
    "green": {
        "L1_bg": COLOR_BLACK, "L2_element_dark": COLOR_DARK_GREEN_DIM, "L3_accent_primary": COLOR_GREEN,
        "L4_hover_bg": COLOR_DARK_GREEN, "L5_accent_secondary": COLOR_LIGHT_GREEN, "L6_text_light": COLOR_NEAR_WHITE,
        "slider_button": COLOR_NEAR_WHITE, "slider_button_hover": COLOR_LIGHT_GREEN,
        "plot_bg": COLOR_BLACK, "plot_wave_main": COLOR_GREEN, "plot_osc_main": COLOR_LIGHT_GREEN,
        "plot_wave_indicator": COLOR_LIGHT_GREEN, "plot_spine": COLOR_DARK_GREEN, "plot_text": COLOR_NEAR_WHITE,
        "list_scrollbar": COLOR_DARK_GREEN_DIM, "list_scrollbar_hover": COLOR_LIGHT_GREEN,
    },
    "blue": {
        "L1_bg": COLOR_BLACK, "L2_element_dark": COLOR_DARK_BLUE_DIM, "L3_accent_primary": COLOR_BLUE,
        "L4_hover_bg": COLOR_DARK_BLUE, "L5_accent_secondary": COLOR_LIGHT_BLUE, "L6_text_light": COLOR_NEAR_WHITE,
        "slider_button": COLOR_NEAR_WHITE, "slider_button_hover": COLOR_LIGHT_BLUE,
        "plot_bg": COLOR_BLACK, "plot_wave_main": COLOR_BLUE, "plot_osc_main": COLOR_LIGHT_BLUE,
        "plot_wave_indicator": COLOR_LIGHT_BLUE, "plot_spine": COLOR_DARK_BLUE, "plot_text": COLOR_NEAR_WHITE,
        "list_scrollbar": COLOR_DARK_BLUE_DIM, "list_scrollbar_hover": COLOR_LIGHT_BLUE,
    },
    "silver": {
        "L1_bg": COLOR_SILVER_L6, "L2_element_dark": COLOR_SILVER_L5, "L3_accent_primary": COLOR_SILVER_L3,
        "L4_hover_bg": COLOR_SILVER_L4, "L5_accent_secondary": COLOR_SILVER_L2, "L6_text_light": COLOR_SILVER_L1,
        "slider_button": COLOR_SILVER_L1, "slider_button_hover": COLOR_SILVER_L2,
        "plot_bg": COLOR_SILVER_L6, "plot_wave_main": COLOR_SILVER_L3, "plot_osc_main": COLOR_SILVER_L3,
        "plot_wave_indicator": COLOR_SILVER_L2, "plot_spine": COLOR_SILVER_L5,
        "plot_text": COLOR_SILVER_L1,
        "list_scrollbar": COLOR_SILVER_L5, "list_scrollbar_hover": COLOR_SILVER_L4,
    },
    "sunset": {
        "L1_bg": COLOR_BLACK, "L2_element_dark": COLOR_SUNSET_L2, "L3_accent_primary": COLOR_SUNSET_L3,
        "L4_hover_bg": COLOR_SUNSET_L4, "L5_accent_secondary": COLOR_SUNSET_L5, "L6_text_light": COLOR_NEAR_WHITE,
        "slider_button": COLOR_NEAR_WHITE, "slider_button_hover": COLOR_SUNSET_L6,
        "plot_bg": COLOR_BLACK, "plot_wave_main": COLOR_NEAR_WHITE, "plot_osc_main": COLOR_SUNSET_L3,
        "plot_wave_indicator": COLOR_SUNSET_L5, "plot_spine": COLOR_SUNSET_L2, "plot_text": COLOR_NEAR_WHITE,
        "list_scrollbar": COLOR_SUNSET_L2, "list_scrollbar_hover": COLOR_SUNSET_L5,
    },
    "ocean": {
        "L1_bg": COLOR_BLACK, "L2_element_dark": COLOR_OCEAN_L2, "L3_accent_primary": COLOR_OCEAN_L3,
        "L4_hover_bg": COLOR_OCEAN_L4, "L5_accent_secondary": COLOR_OCEAN_L5, "L6_text_light": COLOR_NEAR_WHITE,
        "slider_button": COLOR_NEAR_WHITE, "slider_button_hover": COLOR_OCEAN_L6,
        "plot_bg": COLOR_BLACK, "plot_wave_main": COLOR_NEAR_WHITE, "plot_osc_main": COLOR_OCEAN_L3,
        "plot_wave_indicator": COLOR_OCEAN_L5, "plot_spine": COLOR_OCEAN_L2, "plot_text": COLOR_NEAR_WHITE,
        "list_scrollbar": COLOR_OCEAN_L2, "list_scrollbar_hover": COLOR_OCEAN_L5,
    },
    "ember": {
        "L1_bg": COLOR_BLACK, "L2_element_dark": COLOR_EMBER_L2, "L3_accent_primary": COLOR_EMBER_L3,
        "L4_hover_bg": COLOR_EMBER_L4, "L5_accent_secondary": COLOR_EMBER_L5, "L6_text_light": COLOR_NEAR_WHITE,
        "slider_button": COLOR_NEAR_WHITE, "slider_button_hover": COLOR_EMBER_L6,
        "plot_bg": COLOR_BLACK, "plot_wave_main": COLOR_NEAR_WHITE, "plot_osc_main": COLOR_EMBER_L3,
        "plot_wave_indicator": COLOR_EMBER_L5, "plot_spine": COLOR_EMBER_L2, "plot_text": COLOR_NEAR_WHITE,
        "list_scrollbar": COLOR_EMBER_L2, "list_scrollbar_hover": COLOR_EMBER_L5,
    },
    "cyberpunk": {
        "L1_bg": COLOR_CYBERPUNK_L1, "L2_element_dark": COLOR_CYBERPUNK_L2, "L3_accent_primary": COLOR_CYBERPUNK_L3,
        "L4_hover_bg": COLOR_CYBERPUNK_L4, "L5_accent_secondary": COLOR_CYBERPUNK_L5, "L6_text_light": COLOR_NEAR_WHITE,
        "slider_button": COLOR_NEAR_WHITE, "slider_button_hover": COLOR_CYBERPUNK_L6,
        "plot_bg": COLOR_CYBERPUNK_L1, "plot_wave_main": COLOR_NEAR_WHITE, "plot_osc_main": COLOR_CYBERPUNK_L3,
        "plot_wave_indicator": COLOR_CYBERPUNK_L5, "plot_spine": COLOR_CYBERPUNK_L2, "plot_text": COLOR_NEAR_WHITE,
        "list_scrollbar": COLOR_CYBERPUNK_L2, "list_scrollbar_hover": COLOR_CYBERPUNK_L5,
    },
}

SPINE_LINEWIDTH = 0.8

class MN1MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("MN-1")
        self.root.geometry("800x650")
        self.root.resizable(True, True)

        # Make window always on top (optional, platform specific)
        try:
            if os.name == 'nt': # Windows
                self.root.wm_attributes("-topmost", True)
                print("Window set to always on top.")
            # Add similar checks for other OS if needed (e.g., using platform module)
        except Exception as e:
            print(f"Could not set always-on-top attribute: {e}")

        # Themes
        self.themes = THEMES
        self.theme_cycle = [
             "dark", "light", "grey", "red", "gold", "orange", "silver",
             "purple", "green", "blue", "sunset", "ocean",
             "ember", "cyberpunk"
        ]
        self.current_theme_name = "dark" # Default theme

        # Initialize Pygame Mixer
        try:
            pygame.mixer.init()
        except pygame.error as e:
            print(f"FATAL: Error initializing pygame mixer: {e}")
            try:
                import tkinter.messagebox
                tkinter.messagebox.showerror("Pygame Error", f"Could not initialize audio output.\nError: {e}\n\nThe application might not play sound.")
            except: pass # Ignore if messagebox fails

        # Player State Variables
        self.current_song = ""
        self.songs_list = []
        self.current_song_index = 0
        self.previous_volume = 0.5
        self.stopped_position = 0.0 # Store position in seconds when stopped/paused
        self.playing_state = False
        self.paused = False
        self.shuffle_state = False
        self.loop_state = 0  # 0: No loop, 1: Loop all, 2: Loop one
        self.muted = False
        self.slider_active = False  # True when user is dragging the song slider
        self.waveform_dragging = False # True when user is dragging on waveform plot
        self.is_seeking = False # Flag to prevent updates during seek operation
        self.is_generating_waveform = False
        self.is_loading = False
        self.has_error = False
        self.sidebar_visible = True

        try: pygame.mixer.music.set_volume(self.previous_volume)
        except Exception as e: print(f"Warning: Could not set initial volume: {e}")

        # Fonts
        self.title_font = ("SF Mono", 16, "bold")
        self.normal_font = ("SF Mono", 11)
        self.button_font = ("SF Mono", 13, "bold")
        self.play_pause_button_font = ("SF Mono", 26, "bold") # Larger for play/pause

        # Matplotlib Figures & Axes for Visualization
        self.fig_wave, self.ax_wave = plt.subplots(figsize=(5, 1.5))
        self.mpl_canvas_widget_wave = None
        self.position_indicator_line_wave = None # To hold the line object

        self.fig_osc, self.ax_osc = plt.subplots(figsize=(5, 0.8))
        self.mpl_canvas_widget_osc = None
        self.ax_osc.set_ylim(-1.1, 1.1) # Fixed y-axis for oscilloscope

        # Waveform/Oscilloscope Data
        self.waveform_peak_data = None # Holds processed peak data for static waveform
        self.raw_sample_data = None # Holds raw (or downsampled) sample data for oscilloscope
        self.sample_rate = None # Effective sample rate of raw_sample_data
        self.waveform_thread = None
        self.waveform_abort_flag = threading.Event()

        # Oscilloscope parameters
        self.osc_window_seconds = 0.05 # Time window to display
        self.osc_downsample_factor = 5 # Downsample raw audio for performance

        # Time & Title Variables
        self.song_length = 0.0 # In seconds
        self.song_time = 0.0 # Current playback time in seconds
        self.time_elapsed = "00:00"
        self.total_time = "00:00"
        self.update_thread = None
        self.thread_running = False
        self.song_title_var = ctk.StringVar(value="NO SONG LOADED")

        # --- Add placeholder for play/pause button reference ---
        self.play_pause_button = None
        self.sidebar_toggle_button = None
        # ---

        # Build UI
        self.create_frames()
        self.create_player_area()
        self.create_waveform_display()
        self.create_oscilloscope_display()
        self.create_controls()
        self.create_tracklist_area()
        self.apply_theme() # Apply default theme

        # Draw initial placeholder plots
        initial_theme = self.themes[self.current_theme_name]
        initial_spine_color = initial_theme['plot_spine']
        self.draw_initial_placeholder(self.ax_wave, self.fig_wave, initial_spine_color, "LOAD A SONG")
        self.draw_initial_placeholder(self.ax_osc, self.fig_osc, initial_spine_color, "")

        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _configure_axes(self, ax, fig, spine_color, bg_color):
        """Helper to configure Matplotlib axes appearance."""
        if not ax or not fig: return
        fig.patch.set_facecolor(bg_color)
        fig.patch.set_alpha(1.0) # Ensure figure bg is opaque
        ax.set_facecolor(bg_color)
        ax.patch.set_alpha(1.0) # Ensure axes bg is opaque
        # Hide ticks and labels
        ax.tick_params(axis='both', which='both', length=0, width=0, labelsize=0)
        # Configure spines (borders)
        for spine in ax.spines.values():
            spine.set_color(spine_color)
            spine.set_linewidth(SPINE_LINEWIDTH)
            spine.set_visible(True)
        ax.margins(0) # Remove padding inside axes
        ax.set_yticks([]) # Remove y-axis ticks
        ax.set_xticks([]) # Remove x-axis ticks
        # Adjust subplot parameters to minimize whitespace
        try:
            fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
        except Exception as e:
            # print(f"Minor issue adjusting subplot: {e}") # Ignore if fails
            pass

    def create_frames(self):
        """Creates the main frames for layout."""
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.player_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.player_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        # Configure columns to allow resizing: Left=Visuals/Controls, Right=Tracklist
        self.player_frame.grid_columnconfigure(0, weight=2) # Left frame takes more space initially
        self.player_frame.grid_columnconfigure(1, weight=1) # Right frame
        self.player_frame.grid_rowconfigure(0, weight=1)

        # Left Frame (Player Area)
        self.left_frame = ctk.CTkFrame(self.player_frame, corner_radius=0)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5)) # Pad between left/right
        self.left_frame.grid_rowconfigure(0, weight=1) # Visuals area expands
        self.left_frame.grid_rowconfigure(1, weight=0) # Controls area fixed height
        self.left_frame.grid_columnconfigure(0, weight=1)

        # Right Frame (Tracklist Area)
        self.right_frame = ctk.CTkFrame(self.player_frame, corner_radius=0)
        # Grid configuration for right_frame is done in create_tracklist_area

        # Controls Frame (within Left Frame)
        self.controls_frame = ctk.CTkFrame(self.left_frame, height=80, corner_radius=0) # Defined height
        self.controls_frame.grid(row=1, column=0, sticky="ew", pady=(5,5))

        # Visuals Frame (within Left Frame)
        self.visual_frame = ctk.CTkFrame(self.left_frame, corner_radius=0)
        self.visual_frame.grid(row=0, column=0, sticky="nsew", pady=(0,5))
        self.visual_frame.grid_columnconfigure(0, weight=1)
        # Configure rows for title, waveform, oscilloscope, spacer, slider/time
        self.visual_frame.grid_rowconfigure(0, weight=0) # Title
        self.visual_frame.grid_rowconfigure(1, weight=0) # Waveform
        self.visual_frame.grid_rowconfigure(2, weight=0) # Oscilloscope
        self.visual_frame.grid_rowconfigure(3, weight=1) # Spacer (expands vertically)
        self.visual_frame.grid_rowconfigure(4, weight=0) # Slider/Time


    def create_player_area(self):
        """Creates widgets for song info, visuals, slider, and time display."""
        # Info Frame (Title)
        self.info_frame = ctk.CTkFrame(self.visual_frame, corner_radius=0)
        self.info_frame.grid(row=0, column=0, sticky="ew", pady=(0,5))
        self.song_title_label = ctk.CTkLabel(self.info_frame, textvariable=self.song_title_var, font=self.title_font, anchor="w")
        self.song_title_label.pack(fill="x", padx=10, pady=(0, 2)) # Pad title slightly

        # Waveform Frame
        WAVEFORM_HEIGHT = 70 # Adjust height as needed
        self.waveform_frame = ctk.CTkFrame(self.visual_frame, corner_radius=0, height=WAVEFORM_HEIGHT)
        self.waveform_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 1)) # Pad waveform plot

        # Oscilloscope Frame
        OSCILLOSCOPE_HEIGHT = 35 # Adjust height as needed
        self.oscilloscope_frame = ctk.CTkFrame(self.visual_frame, corner_radius=0, height=OSCILLOSCOPE_HEIGHT)
        self.oscilloscope_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(1, 5)) # Pad oscilloscope plot

        # Spacer Frame (allows plots to be pushed up when space is limited)
        self.spacer_frame = ctk.CTkFrame(self.visual_frame, height=0, fg_color="transparent")
        self.spacer_frame.grid(row=3, column=0, sticky="nsew")

        # Slider Frame (Song Progress Slider and Time Labels)
        self.slider_frame = ctk.CTkFrame(self.visual_frame, corner_radius=0)
        self.slider_frame.grid(row=4, column=0, sticky="ew", pady=(0,5), padx=10)
        self.slider_frame.grid_columnconfigure(0, weight=1)
        self.slider_frame.grid_rowconfigure(0, weight=0) # Slider row
        self.slider_frame.grid_rowconfigure(1, weight=0) # Time labels row

        self.song_slider = ctk.CTkSlider(self.slider_frame, from_=0, to=100, command=self.slide_song, variable=ctk.DoubleVar()) # Variable needed for get()
        self.song_slider.grid(row=0, column=0, sticky="ew", pady=5)
        # Bind mouse events for precise seeking on release
        self.song_slider.bind("<ButtonPress-1>", self.slider_start_scroll)
        self.song_slider.bind("<ButtonRelease-1>", self.slider_stop_scroll)

        # Time Display Frame (below slider)
        self.time_frame = ctk.CTkFrame(self.slider_frame, corner_radius=0)
        self.time_frame.grid(row=1, column=0, sticky="ew")
        self.current_time_label = ctk.CTkLabel(self.time_frame, text="00:00", font=self.normal_font)
        self.current_time_label.pack(side="left", padx=(0, 5))
        self.total_time_label = ctk.CTkLabel(self.time_frame, text="00:00", font=self.normal_font)
        self.total_time_label.pack(side="right", padx=(5, 0))

    def create_waveform_display(self):
        """Creates the Matplotlib canvas for the waveform."""
        # Embed the Matplotlib figure in the Tkinter frame
        self.mpl_canvas_widget_wave = FigureCanvasTkAgg(self.fig_wave, master=self.waveform_frame)
        tk_widget = self.mpl_canvas_widget_wave.get_tk_widget()
        tk_widget.pack(fill="both", expand=True)

        # Connect mouse events directly to the Matplotlib canvas for seeking
        self.fig_wave.canvas.mpl_connect('button_press_event', self.on_waveform_press)
        self.fig_wave.canvas.mpl_connect('motion_notify_event', self.on_waveform_motion)
        # Use Tk widget binding for release as mpl_connect release can be tricky
        tk_widget.bind('<ButtonRelease-1>', self.on_waveform_release)
        tk_widget.bind('<Leave>', self.on_waveform_leave) # Handle mouse leaving canvas while dragging

    def create_oscilloscope_display(self):
        """Creates the Matplotlib canvas for the oscilloscope."""
        self.mpl_canvas_widget_osc = FigureCanvasTkAgg(self.fig_osc, master=self.oscilloscope_frame)
        tk_widget_osc = self.mpl_canvas_widget_osc.get_tk_widget()
        tk_widget_osc.pack(fill="both", expand=True)

    def draw_initial_placeholder(self, ax, fig, border_color, message="", text_color=None):
        """Draws a placeholder background and message on a plot."""
        if not ax or not fig or not fig.canvas: return
        try:
            theme = self.themes[self.current_theme_name]
            bg_color = theme['plot_bg']
            if text_color is None: text_color = theme['plot_text']

            ax.clear() # Clear previous content
            self._configure_axes(ax, fig, border_color, bg_color) # Apply theme colors/styles

            # Add message if provided
            font_size = 7 if fig == self.fig_osc else 9 # Smaller font for oscilloscope
            if message:
                ax.text(0.5, 0.5, message, ha='center', va='center', fontsize=font_size,
                        color=text_color, transform=ax.transAxes, fontfamily='SF Mono') # Use axis coordinates

            # Special case for oscilloscope y-limits
            if ax == self.ax_osc:
                ax.set_ylim(-1.1, 1.1)

            # Redraw the canvas
            try:
                fig.canvas.draw_idle() # Use draw_idle for efficiency
            except Exception: pass # Ignore if canvas is not ready yet

            # Reset position indicator if clearing waveform plot
            if ax == self.ax_wave:
                 self.position_indicator_line_wave = None

        except Exception as e:
            print(f"Error drawing placeholder: {e}")
            # traceback.print_exc() # Optional: for more detailed error


    def create_controls(self):
        """Creates the playback control buttons and volume slider."""
        # Frame for main transport buttons (Prev, Play/Pause, Next)
        self.buttons_frame = ctk.CTkFrame(self.controls_frame, corner_radius=0)
        self.buttons_frame.pack(pady=(5,0), anchor="center") # Center buttons horizontally

        button_kwargs = {"font": self.button_font, "border_width": 0, "corner_radius": 0, "width": 70, "height": 56}
        self.prev_button = ctk.CTkButton(self.buttons_frame, text="◄◄", command=self.previous_song, **button_kwargs)
        self.prev_button.grid(row=0, column=0, padx=4)

        self.play_pause_button = ctk.CTkButton(self.buttons_frame, text="▶", command=self.toggle_play_pause, **button_kwargs)
        self.play_pause_button.grid(row=0, column=1, padx=4)

        self.next_button = ctk.CTkButton(self.buttons_frame, text="►►", command=self.next_song, **button_kwargs)
        self.next_button.grid(row=0, column=2, padx=4)

        # Apply larger font specifically to Play/Pause button after creation
        if self.play_pause_button and self.play_pause_button.winfo_exists():
             self.play_pause_button.configure(font=self.play_pause_button_font)

        # Frame for extra controls (Mix, Loop, Vol, Theme, Sidebar)
        self.extra_frame = ctk.CTkFrame(self.controls_frame, corner_radius=0)
        self.extra_frame.pack(pady=(2,5), anchor="center") # Center buttons horizontally

        extra_button_kwargs = {"font": self.normal_font, "border_width": 0, "corner_radius": 0, "width": 65, "height": 25} # Smaller buttons
        theme_button_kwargs = {"font": self.normal_font, "border_width": 0, "corner_radius": 0, "width": 65, "height": 25} # Separate for potential styling

        self.sidebar_toggle_button = ctk.CTkButton(self.extra_frame, text="SIDE", command=self.toggle_sidebar, **extra_button_kwargs)
        self.sidebar_toggle_button.grid(row=0, column=0, padx=3)

        self.theme_toggle_button = ctk.CTkButton(self.extra_frame, text="MN-1", command=self.toggle_theme,**theme_button_kwargs)
        self.theme_toggle_button.grid(row=0, column=1, padx=3)

        self.mix_button = ctk.CTkButton(self.extra_frame, text="MIX", command=self.toggle_mix, **extra_button_kwargs)
        self.mix_button.grid(row=0, column=2, padx=3)

        self.loop_button = ctk.CTkButton(self.extra_frame, text="LOOP", command=self.toggle_loop, **extra_button_kwargs)
        self.loop_button.grid(row=0, column=3, padx=3)

        self.volume_button = ctk.CTkButton(self.extra_frame, text="VOL", command=self.toggle_mute, **extra_button_kwargs)
        self.volume_button.grid(row=0, column=4, padx=3)

        # Volume Slider
        self.volume_slider = ctk.CTkSlider(self.extra_frame, from_=0, to=1, number_of_steps=100, command=self.volume_adjust, width=90, height=18); # Width/height adjusted
        self.volume_slider.set(self.previous_volume) # Set initial volume
        self.volume_slider.grid(row=0, column=5, padx=(3, 10), pady=(0,3)) # Pad volume slider


    def create_tracklist_area(self):
        """Creates the tracklist display and associated buttons."""
        # Configure the right frame (created in create_frames)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0)) # Add padding
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=0) # Label row
        self.right_frame.grid_rowconfigure(1, weight=1) # Scrollable list row (expands)
        self.right_frame.grid_rowconfigure(2, weight=0) # Buttons row

        # Playlist Label Frame
        self.playlist_label_frame = ctk.CTkFrame(self.right_frame, corner_radius=0)
        self.playlist_label_frame.grid(row=0, column=0, sticky="ew", pady=5)
        self.tracklist_label = ctk.CTkLabel(self.playlist_label_frame, text="TRACKLIST", font=self.title_font)
        self.tracklist_label.pack(anchor="center") # Center the label

        # Playlist Scrollable Frame
        self.playlist_frame = ctk.CTkFrame(self.right_frame, corner_radius=0)
        self.playlist_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=0)
        self.playlist_frame.grid_rowconfigure(0, weight=1)
        self.playlist_frame.grid_columnconfigure(0, weight=1)
        self.playlist_scrollable = ctk.CTkScrollableFrame(self.playlist_frame)
        self.playlist_scrollable.grid(row=0, column=0, sticky="nsew")
        self.playlist_entries = [] # List to hold dictionaries for each song entry widget

        # Playlist Buttons Frame (Load, Remove, Clear)
        self.playlist_buttons_frame = ctk.CTkFrame(self.right_frame, corner_radius=0)
        self.playlist_buttons_frame.grid(row=2, column=0, sticky="ew", pady=(5,10)) # Add padding
        # Make buttons expand equally
        self.playlist_buttons_frame.grid_columnconfigure(0, weight=1)
        self.playlist_buttons_frame.grid_columnconfigure(1, weight=1)
        self.playlist_buttons_frame.grid_columnconfigure(2, weight=1)

        playlist_button_kwargs = {"font": self.normal_font, "border_width": 0, "corner_radius": 0}
        # --- Modified Button Text ---
        self.load_button = ctk.CTkButton(self.playlist_buttons_frame, text="MEDIA", command=self.add_songs, **playlist_button_kwargs)
        # --- End Modification ---
        self.load_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.remove_button = ctk.CTkButton(self.playlist_buttons_frame, text="REMOVE", command=self.remove_song, **playlist_button_kwargs)
        self.remove_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.clear_button = ctk.CTkButton(self.playlist_buttons_frame, text="CLEAR", command=self.clear_playlist, **playlist_button_kwargs)
        self.clear_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    def toggle_sidebar(self):
        """Shows or hides the right sidebar (tracklist)."""
        if self.sidebar_visible:
            # Hide sidebar
            self.right_frame.grid_forget()
            # Make left frame take full width
            self.player_frame.grid_columnconfigure(0, weight=1)
            self.player_frame.grid_columnconfigure(1, weight=0)
            self.sidebar_visible = False
            print("Sidebar hidden")
        else:
            # Show sidebar
            self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
            # Restore column weights
            self.player_frame.grid_columnconfigure(0, weight=2)
            self.player_frame.grid_columnconfigure(1, weight=1)
            self.sidebar_visible = True
            print("Sidebar shown")

        # Update button appearance
        self.apply_sidebar_button_state()

        # Schedule plot redraw slightly later to allow layout to settle
        self.root.after(10, self._redraw_plots_after_toggle)

    def _redraw_plots_after_toggle(self):
        """Forces redraw of matplotlib plots after layout changes."""
        try:
            # Waveform Plot
            if self.fig_wave and self.fig_wave.canvas:
                self.fig_wave.canvas.draw_idle()
            # Oscilloscope Plot
            if self.fig_osc and self.fig_osc.canvas:
                self.fig_osc.canvas.draw_idle()
            # Ensure Tkinter widgets update
            if self.mpl_canvas_widget_wave and self.mpl_canvas_widget_wave.get_tk_widget().winfo_exists():
                self.mpl_canvas_widget_wave.get_tk_widget().update_idletasks()
            if self.mpl_canvas_widget_osc and self.mpl_canvas_widget_osc.get_tk_widget().winfo_exists():
                self.mpl_canvas_widget_osc.get_tk_widget().update_idletasks()
        except Exception as e:
            print(f"Error redrawing plots after toggle: {e}")


    def apply_sidebar_button_state(self):
        """Updates the appearance of the sidebar toggle button based on state."""
        if not (self.sidebar_toggle_button and self.sidebar_toggle_button.winfo_exists()):
            return
        theme = self.themes[self.current_theme_name]
        # Determine text color (use black for light theme base, otherwise theme's text color)
        base_text_col = COLOR_BLACK if self.current_theme_name == "light" else theme["L6_text_light"]
        accent_col = theme["L3_accent_primary"]

        # Use accent color when sidebar is hidden (button is 'active' to show it)
        color = accent_col if not self.sidebar_visible else base_text_col
        self.sidebar_toggle_button.configure(text_color=color)


    def toggle_theme(self):
        """Cycles through the available themes."""
        try:
            current_index = self.theme_cycle.index(self.current_theme_name)
            next_index = (current_index + 1) % len(self.theme_cycle)
            self.current_theme_name = self.theme_cycle[next_index]
        except ValueError:
            # Fallback if current theme isn't in the cycle list
            self.current_theme_name = self.theme_cycle[0]
        print(f"Switching theme to: {self.current_theme_name}")
        self.apply_theme()

    def apply_theme(self):
        """Applies the selected theme's colors to all relevant widgets."""
        try:
            theme = self.themes[self.current_theme_name]
            theme_button_display_text = "MN-1" # Consistent text for theme button

            # Extract theme colors
            bg_col = theme["L1_bg"]
            element_dark_col = theme["L2_element_dark"]
            accent_col = theme["L3_accent_primary"]
            hover_col = theme["L4_hover_bg"]
            accent_light_col = theme["L5_accent_secondary"]
            text_col = theme["L6_text_light"]
            slider_button_col = theme.get("slider_button", text_col) # Default to text color if not defined
            slider_button_hover_col = theme.get("slider_button_hover", accent_light_col)
            list_scrollbar_col = theme["list_scrollbar"]
            list_scrollbar_hover_col = theme["list_scrollbar_hover"]
            plot_bg_col = theme["plot_bg"]
            plot_spine_col = theme["plot_spine"]
            plot_text_col = theme["plot_text"]

            # Apply theme to root and main frames
            self.root.configure(fg_color=bg_col)
            for frame in [self.player_frame, self.left_frame, self.right_frame,
                          self.controls_frame, self.visual_frame, self.info_frame,
                          self.waveform_frame, self.oscilloscope_frame, self.spacer_frame,
                          self.slider_frame, self.time_frame, self.playlist_label_frame,
                          self.playlist_frame, self.playlist_buttons_frame,
                          self.buttons_frame, self.extra_frame]:
                if frame and frame.winfo_exists():
                     # Special case for spacer frame
                     if frame is self.spacer_frame:
                         frame.configure(fg_color="transparent")
                     else:
                         frame.configure(fg_color=bg_col)

            # Apply theme to labels
            for label in [self.song_title_label, self.current_time_label,
                          self.total_time_label, self.tracklist_label]:
                 if label and label.winfo_exists():
                     label.configure(fg_color="transparent", text_color=text_col) # Transparent bg

            # Apply theme to main buttons (Prev, Play/Pause, Next)
            # Special handling for light theme buttons to have white background
            main_button_fg = bg_col
            main_button_text = text_col
            if self.current_theme_name == "light":
                main_button_fg = COLOR_WHITE # Use white bg for light theme main buttons
                main_button_text = COLOR_BLACK # Use black text for light theme main buttons

            for btn in [self.prev_button, self.play_pause_button, self.next_button]:
                 if btn and btn.winfo_exists():
                     btn.configure(fg_color=main_button_fg, text_color=main_button_text, hover_color=hover_col)
                     # Ensure correct font is reapplied
                     if btn is self.play_pause_button:
                         btn.configure(font=self.play_pause_button_font)
                     else:
                         btn.configure(font=self.button_font)

            # Apply theme to extra buttons (Mix, Loop, Vol, etc.) and tracklist buttons
            extra_button_fg = main_button_fg # Use same fg logic as main buttons for consistency
            extra_button_text = main_button_text # Use same text logic

            extra_buttons = [self.sidebar_toggle_button, self.mix_button, self.loop_button,
                             self.volume_button, self.theme_toggle_button, self.load_button,
                             self.remove_button, self.clear_button]
            for btn in extra_buttons:
                 if btn and btn.winfo_exists():
                     btn.configure(fg_color=extra_button_fg, hover_color=hover_col)
                     # Special text colors for specific buttons
                     if btn is self.theme_toggle_button:
                         btn.configure(text_color=accent_col) # Theme button uses accent
                     elif btn is self.sidebar_toggle_button:
                          self.apply_sidebar_button_state() # Handle its state-dependent color
                     else:
                          # Apply base text color, stateful buttons will override below
                          btn.configure(text_color=extra_button_text)

            # Update theme button text
            if self.theme_toggle_button and self.theme_toggle_button.winfo_exists():
                self.theme_toggle_button.configure(text=theme_button_display_text)

            # Apply theme to sliders
            if self.song_slider and self.song_slider.winfo_exists():
                self.song_slider.configure(fg_color=element_dark_col, progress_color=accent_col,
                                           button_color=slider_button_col, button_hover_color=slider_button_hover_col)
            if self.volume_slider and self.volume_slider.winfo_exists():
                self.volume_slider.configure(fg_color=element_dark_col, progress_color=accent_col,
                                             button_color=slider_button_col, button_hover_color=slider_button_hover_col)

            # Apply theme to scrollable frame scrollbar
            if self.playlist_scrollable and self.playlist_scrollable.winfo_exists():
                 self.playlist_scrollable.configure(fg_color=bg_col, scrollbar_button_color=list_scrollbar_col,
                                                    scrollbar_button_hover_color=list_scrollbar_hover_col)

            # Update stateful button appearances
            # Mute button
            mute_color = accent_col if self.muted else extra_button_text
            mute_text = "MUTED" if self.muted else "VOL"
            if self.volume_button and self.volume_button.winfo_exists():
                self.volume_button.configure(text_color=mute_color, text=mute_text)
            # Mix button
            mix_color = accent_col if self.shuffle_state else extra_button_text
            if self.mix_button and self.mix_button.winfo_exists():
                self.mix_button.configure(text_color=mix_color)
            # Loop button
            self.apply_loop_button_state() # Handles its own text/color based on loop_state
            # Sidebar button (handled earlier and in its own function)
            self.apply_sidebar_button_state()

            # Update tracklist item colors (selected/deselected)
            selected_idx = -1
            for i, entry in enumerate(self.playlist_entries):
                 if entry and entry.get("frame") and entry["frame"].winfo_exists() and entry.get("selected"):
                     selected_idx = i
                     break
            if selected_idx != -1:
                self.select_song(selected_idx) # Re-apply selection styling with new theme
            else:
                 # Ensure non-selected items have default theme colors
                 bg_color_default = theme["L1_bg"]
                 text_color_default = theme["L6_text_light"]
                 for entry in self.playlist_entries:
                    try:
                        if entry and not entry.get("selected"):
                            if entry.get("frame") and entry["frame"].winfo_exists():
                                entry["frame"].configure(fg_color=bg_color_default)
                            if entry.get("label") and entry["label"].winfo_exists():
                                entry["label"].configure(fg_color="transparent", text_color=text_color_default)
                    except Exception: pass # Ignore errors on potentially destroyed widgets

            # Re-draw plots with new theme colors
            # Waveform
            if self.ax_wave and self.fig_wave and self.fig_wave.canvas:
                self._configure_axes(self.ax_wave, self.fig_wave, plot_spine_col, plot_bg_col)
                if self.waveform_peak_data is not None:
                    self.draw_static_matplotlib_waveform() # Redraw existing data
                else:
                     # Determine appropriate placeholder message
                     placeholder_msg = self.song_title_var.get() if "ERROR" in self.song_title_var.get() or "FAILED" in self.song_title_var.get() else \
                                      ("LOAD A SONG" if not self.current_song else "NO WAVEFORM DATA")
                     self.draw_initial_placeholder(self.ax_wave, self.fig_wave, plot_spine_col, placeholder_msg, plot_text_col)

            # Oscilloscope
            if self.ax_osc and self.fig_osc and self.fig_osc.canvas:
                 self._configure_axes(self.ax_osc, self.fig_osc, plot_spine_col, plot_bg_col)
                 if self.playing_state and self.raw_sample_data is not None:
                     self.update_oscilloscope() # Redraw current oscilloscope segment
                 else:
                     self.draw_initial_placeholder(self.ax_osc, self.fig_osc, plot_spine_col, "", plot_text_col)

        except Exception as e:
            print(f"Error applying theme '{self.current_theme_name}': {e}")
            traceback.print_exc()

    def _update_display_title(self, base_title=""):
        """Updates the song title label with state prefixes."""
        prefix = ""
        # Determine the base title
        title = base_title if base_title else \
                (os.path.basename(self.current_song) if self.current_song else "NO SONG LOADED")

        # Add prefix based on state
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
        elif not self.songs_list and not self.current_song:
            # Handle empty playlist state explicitly
            title = "TRACKLIST EMPTY"
        elif not self.current_song:
            title = "NO SONG LOADED"
            # If playlist isn't empty but no song selected/loaded yet
            if self.songs_list:
                 title = "SELECT A TRACK"


        # Update the label if it exists
        if self.song_title_label and self.song_title_label.winfo_exists():
            self.song_title_var.set(f"{prefix}{title}")


    def add_songs(self):
        """Opens file dialog to add songs to the tracklist."""
        # --- Modified filetypes to include OGG and WAV ---
        songs = filedialog.askopenfilenames(
            initialdir=os.path.expanduser("~"), # Start in user's home directory
            title="Select Audio Files",
            filetypes=(("Audio Files", "*.mp3 *.flac *.ogg *.wav"),
                       ("MP3 Files", "*.mp3"),
                       ("FLAC Files", "*.flac"),
                       ("Ogg Files", "*.ogg"),
                       ("WAV Files", "*.wav"),
                       ("All Files", "*.*"))
        )
        # --- End Modification ---
        added_count = 0
        if not songs: # User cancelled dialog
             return

        for song_path in songs:
            if os.path.exists(song_path):
                 try:
                    # Basic validation using Mutagen to check if readable
                    file_ext = os.path.splitext(song_path)[1].lower()
                    # --- Modified validation to include OGG and WAV ---
                    if file_ext == ".mp3": MP3(song_path)
                    elif file_ext == ".flac": FLAC_MUTAGEN(song_path)
                    elif file_ext == ".ogg": OggVorbis(song_path)
                    elif file_ext == ".wav": WAVE(song_path)
                    # --- End Modification ---
                    else:
                        print(f"Skipping unsupported file type: {os.path.basename(song_path)}")
                        continue # Skip unsupported types

                    song_name = os.path.basename(song_path)
                    # Add if not already in the list
                    if song_path not in self.songs_list:
                        self.add_song_to_playlist(song_name, song_path)
                        self.songs_list.append(song_path)
                        added_count += 1
                    else:
                        print(f"Song already in tracklist: {song_name}")
                 except Exception as e:
                     # Catch errors during file validation (corrupt, permission denied etc.)
                     print(f"Skipping invalid/unreadable file: {os.path.basename(song_path)} - Error: {e}")
            else:
                 print(f"Skipping non-existent file: {song_path}")

        if added_count > 0:
            print(f"{added_count} TRACK(S) ADDED")
        elif added_count == 0 and songs: # Files were selected, but none were new/valid
            print("NO NEW TRACKS ADDED")

        # If this is the first song added, select it automatically
        if added_count > 0 and len(self.songs_list) == added_count:
            if self.song_title_var.get() == "TRACKLIST EMPTY":
                self._update_display_title(base_title="SELECT A TRACK")
            if not self.current_song and not self.playing_state and not self.paused:
                self.select_song(0) # Select the first added song


    def add_song_to_playlist(self, song_name, song_path):
        """Adds a single song entry to the visual tracklist."""
        index = len(self.playlist_entries)
        theme = self.themes[self.current_theme_name]
        list_item_bg = theme["L1_bg"] # Use main background for items initially
        list_item_fg = theme["L6_text_light"]

        # Create frame for the list item
        song_frame = ctk.CTkFrame(self.playlist_scrollable, fg_color=list_item_bg, corner_radius=0)
        song_frame.pack(fill="x", pady=1, ipady=1) # Fill horizontally, small vertical padding

        # Create label for the song name
        song_label = ctk.CTkLabel(song_frame, text=song_name, font=self.normal_font,
                                  fg_color="transparent", text_color=list_item_fg, # Label bg transparent
                                  anchor="w", justify="left", cursor="hand2") # Left aligned text
        song_label.pack(fill="x", padx=5) # Pad text inside frame

        # Bind mouse clicks to the label
        song_label.bind("<Button-1>", lambda e, idx=index: self.select_song(idx))
        song_label.bind("<Double-Button-1>", lambda e, idx=index: self.play_selected_song_by_index(idx))
        # Also bind to frame in case user clicks padding
        song_frame.bind("<Button-1>", lambda e, idx=index: self.select_song(idx))
        song_frame.bind("<Double-Button-1>", lambda e, idx=index: self.play_selected_song_by_index(idx))

        # Store references to the widgets and state
        self.playlist_entries.append({
            "frame": song_frame,
            "label": song_label,
            "selected": False,
            "index": index # Store original index for rebinding if needed
        })

    def select_song(self, index):
        """Highlights the selected song in the tracklist."""
        if not (0 <= index < len(self.playlist_entries)):
             # print(f"Warning: select_song index {index} out of range.")
             return # Invalid index

        theme = self.themes[self.current_theme_name]
        # Use accent color for selected text, main bg for frame
        selected_text_color = theme["L3_accent_primary"]
        # Use theme text/bg colors for deselected items
        default_text_color = theme["L6_text_light"]
        default_bg_color = theme["L1_bg"]

        for i, entry in enumerate(self.playlist_entries):
            if not (entry and entry.get("frame") and entry.get("label")):
                continue # Skip if entry is somehow invalid

            is_selected = (i == index)

            # Determine colors based on selection state
            # Frame background ALWAYS default in this version
            frame_bg = default_bg_color
            # Text color changes based on selection
            text_color = selected_text_color if is_selected else default_text_color

            try:
                # Configure Frame background (always default)
                if entry["frame"].winfo_exists():
                    entry["frame"].configure(fg_color=frame_bg)

                # Configure Label text color (changes) and ensure label background is transparent
                if entry["label"].winfo_exists():
                    entry["label"].configure(fg_color="transparent", text_color=text_color)

            except Exception as e:
                # Avoid spamming console with errors if widgets are destroyed during rapid changes
                if "invalid command name" not in str(e).lower():
                    print(f"Warning: Error configuring tracklist entry {i} during select: {e}")

            entry["selected"] = is_selected # Update selection state in our tracking list


    def play_selected_song_by_index(self, index):
        """Plays the song at the specified index."""
        if 0 <= index < len(self.songs_list):
             # Abort any ongoing waveform generation for the *previous* song first
             self.abort_waveform_generation()
             # Set the index and select visually
             self.current_song_index = index
             self.select_song(index)
             # Play the music (this will handle loading, info update, waveform trigger)
             self.play_music()
        else:
             print(f"Warning: play_selected_song_by_index index {index} out of range.")


    def play_selected_song(self, event=None):
        """Plays the currently selected song in the tracklist."""
        selected_index = -1
        # Find the currently selected index
        for index, entry in enumerate(self.playlist_entries):
            if entry and entry.get("frame") and entry["frame"].winfo_exists() and entry.get("selected"):
                selected_index = index
                break

        if selected_index != -1:
            self.play_selected_song_by_index(selected_index)
        elif self.playlist_entries:
            # If nothing is selected, play the first song
            print("Nothing selected, playing first track.")
            self.play_selected_song_by_index(0)
        else:
            # No songs in the list
             self._update_display_title() # Show "TRACKLIST EMPTY"


    def remove_song(self):
        """Removes the currently selected song from the tracklist."""
        removed_index = -1
        is_current_song_removed = False
        current_selected_index = -1

        # Find the selected index
        for i, entry in enumerate(self.playlist_entries):
             if entry and entry.get("frame") and entry["frame"].winfo_exists() and entry.get("selected"):
                 current_selected_index = i
                 break

        if current_selected_index == -1:
            print("NO TRACK SELECTED")
            return # Nothing to remove

        removed_index = current_selected_index

        # Check if the song being removed is the currently loaded/playing one
        current_song_path = self.songs_list[removed_index] if removed_index < len(self.songs_list) else None
        if current_song_path and removed_index == self.current_song_index and self.current_song == current_song_path:
            is_current_song_removed = True

        # Remove from visual playlist (destroy widgets)
        if removed_index < len(self.playlist_entries):
             try:
                 if self.playlist_entries[removed_index]["frame"].winfo_exists():
                     self.playlist_entries[removed_index]["frame"].destroy()
             except Exception: pass # Ignore errors destroying widgets
             removed_entry_data = self.playlist_entries.pop(removed_index) # Remove dict from list
        else:
             print("Warning: Playlist entry index mismatch during remove.")
             return # Should not happen

        # Remove from internal song list
        if removed_index < len(self.songs_list):
             removed_song_path = self.songs_list.pop(removed_index)
             print(f"Removed: {os.path.basename(removed_song_path)}")
        else:
            print("Warning: Song list index mismatch during remove.")
            # Consistency issue, might need to rebuild lists? For now, just return.
            return

        # --- Adjust internal state and selection ---
        new_selected_index = -1

        if is_current_song_removed:
             # If the playing song was removed, select the next one (or previous if it was last)
             new_selected_index = removed_index if removed_index < len(self.playlist_entries) else removed_index - 1
        else:
            # If a different song was removed, adjust the current_song_index if needed
            if self.current_song_index > removed_index:
                self.current_song_index -= 1
            # Keep the selection on the (now potentially shifted) currently playing song
            new_selected_index = self.current_song_index

        # Re-index and re-bind remaining playlist entries
        for i in range(len(self.playlist_entries)):
            entry = self.playlist_entries[i]
            if entry:
                entry["index"] = i # Update index stored in dict
                try:
                    # Re-bind click events with the new index 'i'
                    if entry.get("label") and entry["label"].winfo_exists():
                        entry["label"].unbind("<Button-1>")
                        entry["label"].unbind("<Double-Button-1>")
                        entry["label"].bind("<Button-1>", lambda e, idx=i: self.select_song(idx))
                        entry["label"].bind("<Double-Button-1>", lambda e, idx=i: self.play_selected_song_by_index(idx))
                    if entry.get("frame") and entry["frame"].winfo_exists():
                        entry["frame"].unbind("<Button-1>")
                        entry["frame"].unbind("<Double-Button-1>")
                        entry["frame"].bind("<Button-1>", lambda e, idx=i: self.select_song(idx))
                        entry["frame"].bind("<Double-Button-1>", lambda e, idx=i: self.play_selected_song_by_index(idx))
                except Exception as e:
                    print(f"Error re-binding tracklist entry {i}: {e}")


        # --- Handle player state if the current song was removed ---
        if is_current_song_removed:
            self.stop() # Stop playback
            self.current_song = "" # Clear current song path
            self.has_error = False; self.is_loading = False; self.is_generating_waveform = False;
            self._update_display_title(base_title="NO SONG LOADED") # Update title
            if self.play_pause_button and self.play_pause_button.winfo_exists():
                self.play_pause_button.configure(text="▶") # Reset button text

            # Clear visuals
            theme = self.themes[self.current_theme_name]
            spine_color = theme['plot_spine']
            self.draw_initial_placeholder(self.ax_wave, self.fig_wave, spine_color, "TRACK REMOVED")
            self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color, "")
            self.raw_sample_data = None; self.waveform_peak_data = None; self.sample_rate = None; self.song_length = 0;

            # Reset time/slider
            if self.total_time_label and self.total_time_label.winfo_exists(): self.total_time_label.configure(text="00:00")
            if self.current_time_label and self.current_time_label.winfo_exists(): self.current_time_label.configure(text="00:00")
            if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.set(0); self.song_slider.configure(to=100) # Reset slider

            # Select the new index if playlist is not empty
            if len(self.playlist_entries) > 0:
                 select_idx = max(0, min(new_selected_index, len(self.playlist_entries) - 1)) # Ensure valid index
                 self.select_song(select_idx)
                 self.current_song_index = select_idx # Update index tracking the logical current song
            elif len(self.songs_list) == 0: # Check songs_list as playlist_entries might be briefly out of sync
                 self._update_display_title(base_title="TRACKLIST EMPTY")

        # --- Handle state if playlist becomes empty ---
        elif len(self.songs_list) == 0:
             # This case handles removing the *last* song when it wasn't playing
             self.current_song_index = 0 # Reset index
             self.current_song = ""
             self.has_error = False; self.is_loading = False; self.is_generating_waveform = False;
             self._update_display_title(base_title="TRACKLIST EMPTY")
             if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="▶")
             theme = self.themes[self.current_theme_name]; spine_color = theme['plot_spine']
             self.draw_initial_placeholder(self.ax_wave, self.fig_wave, spine_color, "TRACKLIST EMPTY")
             self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color, "")
             self.raw_sample_data = None; self.waveform_peak_data = None; self.sample_rate = None; self.song_length = 0;
             if self.total_time_label and self.total_time_label.winfo_exists(): self.total_time_label.configure(text="00:00")
             if self.current_time_label and self.current_time_label.winfo_exists(): self.current_time_label.configure(text="00:00")
             if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.set(0); self.song_slider.configure(to=100)
        else:
             # If a different song was removed, just ensure the correct song remains selected
             if 0 <= new_selected_index < len(self.playlist_entries):
                 self.select_song(new_selected_index)

    def clear_playlist(self):
        """Removes all songs from the tracklist and stops playback."""
        self.stop() # Stop any playback

        # Destroy all visual playlist entries
        for entry in self.playlist_entries:
            try:
                 if entry and entry.get("frame") and entry["frame"].winfo_exists():
                     entry["frame"].destroy()
            except Exception: pass # Ignore errors

        # Clear internal lists and reset state
        self.playlist_entries.clear()
        self.songs_list.clear()
        self.current_song_index = 0
        self.current_song = ""
        self.has_error = False; self.is_loading = False; self.is_generating_waveform = False;
        self._update_display_title(base_title="TRACKLIST CLEARED") # Initial clear message
        if self.play_pause_button and self.play_pause_button.winfo_exists():
            self.play_pause_button.configure(text="▶") # Reset button

        # Clear waveform/oscilloscope data
        self.waveform_peak_data = None
        self.raw_sample_data = None
        self.sample_rate = None

        # Reset visuals
        theme = self.themes[self.current_theme_name]; spine_color = theme['plot_spine']
        self.draw_initial_placeholder(self.ax_wave, self.fig_wave, spine_color, "TRACKLIST CLEARED")
        self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color, "")

        # Reset time and slider
        if self.total_time_label and self.total_time_label.winfo_exists(): self.total_time_label.configure(text="00:00")
        if self.current_time_label and self.current_time_label.winfo_exists(): self.current_time_label.configure(text="00:00")
        if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.set(0); self.song_slider.configure(to=100)
        self.song_length = 0
        self._update_display_title(base_title="TRACKLIST EMPTY") # Final state title


    def toggle_play_pause(self):
        """Toggles playback state between play, pause, and resuming."""
        # Handle case where playlist is empty
        if not self.songs_list:
            self._update_display_title(base_title="TRACKLIST EMPTY")
            if self.play_pause_button and self.play_pause_button.winfo_exists():
                self.play_pause_button.configure(text="▶") # Ensure button shows play symbol
            return

        self.has_error = False # Clear any previous error state on interaction
        theme = self.themes[self.current_theme_name]
        active_button_color = theme["L4_hover_bg"] # Use hover color for feedback
        default_button_color = COLOR_WHITE if self.current_theme_name == "light" else theme["L1_bg"]
        spine_color = theme['plot_spine'] # For placeholder drawing

        # --- Button press visual feedback ---
        if self.play_pause_button and self.play_pause_button.winfo_exists():
            original_color = self.play_pause_button.cget("fg_color")
            self.play_pause_button.configure(fg_color=active_button_color)
            # Schedule resetting the color slightly later
            self.root.after(100, lambda: self.play_pause_button.configure(fg_color=original_color) if self.play_pause_button and self.play_pause_button.winfo_exists() else None)
        # ---

        # --- Logic based on current state ---
        if self.playing_state:
            # --- PAUSE ---
            if not self.paused: # Should always be true if playing_state is true, but check anyway
                try:
                    current_pos_ms = 0
                    # Get current position before pausing
                    if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                         current_pos_ms = pygame.mixer.music.get_pos() # Returns time since last play/start in ms
                         if current_pos_ms != -1:
                             # Update the stopped position based on elapsed time
                             time_since_last_play_sec = current_pos_ms / 1000.0
                             self.stopped_position = self.stopped_position + time_since_last_play_sec
                             self.song_time = self.stopped_position # Sync internal time tracker
                         # else: Error getting position, might happen briefly at end

                    pygame.mixer.music.pause()
                    self.paused = True
                    self.playing_state = False # Not actively playing anymore
                    self.thread_running = False # Stop background updates
                    if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="▶") # Show play symbol
                    self._update_display_title()
                    print(f"Playback Paused at {self.stopped_position:.2f}s (Raw mixer pos: {current_pos_ms}ms)")
                except pygame.error as e:
                    print(f"Pygame error during pause: {e}")
                    self.has_error = True; self._update_display_title()

        elif self.paused:
            # --- UNPAUSE / RESUME ---
             try:
                 pygame.mixer.music.unpause()
                 self.paused = False
                 self.playing_state = True
                 if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="II") # Show pause symbol
                 self._update_display_title()
                 self.start_update_thread() # Restart background updates
                 # Note: stopped_position already holds the correct resume time
                 print(f"Resumed playback from {self.stopped_position:.2f}s")
             except pygame.error as e:
                 print(f"Pygame error during unpause: {e}")
                 self.has_error = True; self._update_display_title()

        else: # Neither playing nor paused: Start playback
            # --- PLAY (from beginning or stopped position) ---
            song_to_play_index = -1
            selected_idx = -1
            is_resuming = False

            # Determine which song to play:
            # 1. Check if a song is selected in the list
            for i, entry in enumerate(self.playlist_entries):
                 if entry and entry.get("frame") and entry["frame"].winfo_exists() and entry.get("selected"):
                     selected_idx = i
                     break

            if selected_idx != -1 and 0 <= selected_idx < len(self.songs_list):
                 # Play the selected song
                 song_to_play_index = selected_idx
                 # Check if we are resuming the *same* selected song from a non-zero position
                 is_resuming = (song_to_play_index == self.current_song_index and
                                self.stopped_position > 0 and
                                self.current_song == self.songs_list[song_to_play_index])
            elif self.current_song and self.stopped_position > 0 and \
                 0 <= self.current_song_index < len(self.songs_list) and \
                 self.songs_list[self.current_song_index] == self.current_song:
                 # If nothing is selected, but a song was previously loaded and stopped mid-way, resume it
                 song_to_play_index = self.current_song_index
                 is_resuming = True
            elif self.songs_list:
                 # Fallback: Play the logically current song (or first if index is invalid)
                 # Check if there's a selected song first (covers case where selection exists but isn't current_song_index)
                 current_selected_index = -1
                 for i, entry in enumerate(self.playlist_entries):
                     if entry and entry.get("frame") and entry["frame"].winfo_exists() and entry.get("selected"):
                         current_selected_index = i
                         break
                 if 0 <= current_selected_index < len(self.songs_list):
                     song_to_play_index = current_selected_index
                 elif 0 <= self.current_song_index < len(self.songs_list):
                     song_to_play_index = self.current_song_index
                 else:
                     song_to_play_index = 0 # Default to first song

                 # Check if resuming *this* fallback song
                 is_resuming = (song_to_play_index == self.current_song_index and
                                self.stopped_position > 0 and
                                self.current_song == self.songs_list[song_to_play_index])
            # else: songs_list is empty, handled at the start of the function

            # --- Load and play the determined song ---
            if song_to_play_index != -1:
                new_song_path = self.songs_list[song_to_play_index]
                song_changed = (new_song_path != self.current_song)

                # Update internal state
                self.current_song_index = song_to_play_index
                self.current_song = new_song_path
                self.select_song(self.current_song_index) # Visually select the song

                try:
                    self.is_loading = True; self._update_display_title() # Show loading state

                    if song_changed or not is_resuming:
                         # Load song from beginning if it's new or we weren't resuming
                         self.abort_waveform_generation() # Abort previous waveform gen if any
                         self.update_song_info() # Get length, update slider range etc.
                         # Show loading placeholders immediately
                         self.draw_initial_placeholder(self.ax_wave, self.fig_wave, spine_color, "LOADING...")
                         self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color, "")

                         pygame.mixer.music.load(self.current_song)
                         start_pos = 0.0
                         self.stopped_position = 0.0 # Reset position for new song
                         self.song_time = 0.0
                         print(f"Starting new playback: {os.path.basename(self.current_song)}")
                    else:
                         # Resuming the same song, start from stopped_position
                         # Need to re-load the song before playing from a specific point with Pygame
                         pygame.mixer.music.load(self.current_song)
                         start_pos = self.stopped_position
                         # Ensure song info (length etc.) is current if resuming
                         self.update_song_info()
                         print(f"Resuming stopped playback: {os.path.basename(self.current_song)} at {start_pos:.2f}s")

                    # Play the loaded song
                    pygame.mixer.music.play(start=start_pos)
                    self.playing_state = True
                    self.paused = False
                    self.is_loading = False # Done loading

                    if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="II") # Show pause symbol
                    self._update_display_title() # Update title to playing state
                    self.start_update_thread() # Start updates

                    # Trigger waveform generation if it's a new song or wasn't resuming
                    if song_changed or not is_resuming:
                        self.trigger_waveform_generation()
                    # If resuming, ensure visuals are up-to-date for the current position
                    elif self.waveform_peak_data is not None:
                        pos_ratio = np.clip(self.stopped_position / self.song_length, 0.0, 1.0) if self.song_length > 0 else 0.0
                        self.draw_waveform_position_indicator(pos_ratio)
                        if self.fig_wave and self.fig_wave.canvas: self.fig_wave.canvas.draw_idle()
                        self.update_oscilloscope() # Draw initial oscilloscope frame


                except pygame.error as e:
                    print(f"Pygame Error loading/playing: {e}")
                    self.has_error = True; self.is_loading = False;
                    self._update_display_title(base_title=f"{os.path.basename(self.current_song)}")
                    self.playing_state = False; self.paused = False; self.current_song = "" # Reset state
                    if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="▶")
                except Exception as e:
                    print(f"Error loading/playing song: {e}")
                    traceback.print_exc()
                    self.has_error = True; self.is_loading = False;
                    self._update_display_title(base_title=f"{os.path.basename(self.current_song)}")
                    self.playing_state = False; self.paused = False; self.current_song = "" # Reset state
                    if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="▶")
            else:
                 # This case should ideally not be reached if the initial check for songs_list works
                 self._update_display_title(base_title="TRACKLIST EMPTY?") # Should show empty earlier
                 if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="▶")


    def play_music(self):
        """Loads and plays the song at self.current_song_index from the beginning."""
        # Validate index
        if not self.songs_list or not (0 <= self.current_song_index < len(self.songs_list)):
            self._update_display_title(base_title="INVALID SELECTION")
            if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="▶")
            return

        self.has_error = False # Clear previous errors
        self.current_song = self.songs_list[self.current_song_index]
        self.stopped_position = 0.0 # Start from beginning
        self.song_time = 0.0
        theme = self.themes[self.current_theme_name]
        spine_color = theme['plot_spine']

        try:
            self.abort_waveform_generation() # Stop any previous waveform generation
            print(f"play_music: Loading {os.path.basename(self.current_song)}")
            self.is_loading = True; self._update_display_title()

            # Stop previous, load new, get info, play
            pygame.mixer.music.stop() # Stop potential previous playback cleanly
            pygame.mixer.music.load(self.current_song)
            self.update_song_info() # Get length, update slider/labels
            pygame.mixer.music.play() # Start from beginning (default)

            self.playing_state = True
            self.paused = False
            self.is_loading = False # Done loading

            # Update UI state
            if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="II") # Show pause symbol
            self.select_song(self.current_song_index) # Ensure correct song is highlighted
            self._update_display_title() # Show playing state

            # Reset slider and time display for new song
            if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.set(0)
            if self.current_time_label and self.current_time_label.winfo_exists(): self.current_time_label.configure(text="00:00")

            # Show placeholders while waveform generates
            self.draw_initial_placeholder(self.ax_wave, self.fig_wave, spine_color,"GENERATING...")
            self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color,"") # Clear oscilloscope

            # Start waveform generation and position updates in background
            self.trigger_waveform_generation()
            self.start_update_thread()

        except pygame.error as e:
             print(f"Pygame Error in play_music: {e}")
             self.has_error = True; self.is_loading = False;
             self._update_display_title(base_title=f"{os.path.basename(self.current_song)}")
             self.playing_state = False; self.paused = False; self.current_song = ""; # Reset state
             if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="▶")
             # Show error on plots
             self.draw_initial_placeholder(self.ax_wave, self.fig_wave, spine_color,"LOAD ERROR")
             self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color,"")

        except Exception as e:
             print(f"Error in play_music: {e}")
             traceback.print_exc()
             self.has_error = True; self.is_loading = False;
             self._update_display_title(base_title=f"{os.path.basename(self.current_song)}")
             self.playing_state = False; self.paused = False; self.current_song = ""; # Reset state
             if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="▶")
             # Show error on plots
             self.draw_initial_placeholder(self.ax_wave, self.fig_wave, spine_color,"ERROR")
             self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color,"")

    def stop(self):
        """Stops playback and records the current position."""
        if self.playing_state or self.paused:
            final_pos = 0.0
            try:
                # Determine the final position accurately
                if self.paused:
                    # If paused, the stopped_position is already accurate
                    final_pos = self.stopped_position
                elif self.playing_state and pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                    # If playing, calculate position based on last start time and elapsed time
                    current_pos_ms = pygame.mixer.music.get_pos()
                    if current_pos_ms != -1:
                        final_pos = self.stopped_position + (current_pos_ms / 1000.0)
                    else:
                        # Fallback if get_pos fails (e.g., right at the end)
                        final_pos = self.song_time # Use the last known time from update loop
                else:
                     # Fallback if not playing/paused but stop was called (e.g., from clear playlist)
                     final_pos = self.song_time

                # print(f"Stop called, final calculated pos: {final_pos:.2f}s") # Debugging log
                pygame.mixer.music.stop()

            except pygame.error as e:
                print(f"Pygame error during stop: {e}")
            finally:
                was_playing_or_paused = self.playing_state or self.paused # Record if state changed
                # Update state variables
                self.playing_state = False
                self.paused = False
                # Store the final position accurately, clipping to song length if known
                self.stopped_position = np.clip(final_pos, 0.0, self.song_length if self.song_length > 0 else final_pos + 1.0) # Clip to length or allow slight over if length unknown
                self.song_time = self.stopped_position # Sync internal timer

                # Stop the update thread
                self.thread_running = False

                # Update UI
                self._update_display_title()
                if self.play_pause_button and self.play_pause_button.winfo_exists():
                    self.play_pause_button.configure(text="▶")

                # Update visuals to reflect the stopped position only if playback was active
                if was_playing_or_paused:
                    slider_val = self.stopped_position
                    if self.song_slider and self.song_slider.winfo_exists():
                         # Ensure slider value doesn't exceed its 'to' value
                         max_slider_val = self.song_slider.cget("to")
                         self.song_slider.set(min(slider_val, max_slider_val))

                    if self.current_time_label and self.current_time_label.winfo_exists():
                         display_time = np.clip(self.stopped_position, 0.0, self.song_length if self.song_length > 0 else self.stopped_position)
                         mins, secs = divmod(int(display_time), 60)
                         self.current_time_label.configure(text=f"{mins:02d}:{secs:02d}")

                    # Update waveform indicator to final position
                    theme = self.themes[self.current_theme_name]
                    spine_color = theme['plot_spine']
                    pos_ratio = np.clip(self.stopped_position / self.song_length, 0.0, 1.0) if self.song_length > 0 else 0.0
                    self.draw_waveform_position_indicator(pos_ratio)
                    if self.fig_wave and self.fig_wave.canvas:
                         try: self.fig_wave.canvas.draw_idle()
                         except Exception: pass

                    # Clear oscilloscope as playback stopped
                    self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color,"")

                    print(f"Stopped. Recorded pos: {self.stopped_position:.2f}s")
        else:
             # If already stopped, just ensure thread is stopped and UI is correct
             self.thread_running = False
             self._update_display_title()
             if self.play_pause_button and self.play_pause_button.winfo_exists():
                 self.play_pause_button.configure(text="▶")


    def previous_song(self):
        """Stops current song and plays the previous one in the list."""
        if not self.songs_list:
            self._update_display_title(base_title="TRACKLIST EMPTY")
            return

        original_index = self.current_song_index
        self.stop() # Stop current song first

        if len(self.songs_list) > 0:
            # Decrement index, wrapping around
            self.current_song_index = (original_index - 1 + len(self.songs_list)) % len(self.songs_list)
            self.play_music() # Play the new song


    def next_song(self, auto_advance=False):
        """Stops current song (unless auto-advancing) and plays the next one."""
        if not self.songs_list:
            self._update_display_title(base_title="TRACKLIST EMPTY")
            return

        original_index = self.current_song_index

        # Stop current song only if manually triggered
        if not auto_advance:
            self.stop()
        else:
            # If auto-advancing (song ended), reset state without explicit stop() call
            self.playing_state = False
            self.paused = False
            self.thread_running = False
            self.abort_waveform_generation() # Abort potential gen from previous song
            self.stopped_position = 0.0 # Next song starts at 0
            self.song_time = 0.0
            print("Auto-advancing to next song.")

        if len(self.songs_list) > 0:
             # Increment index, wrapping around
             self.current_song_index = (original_index + 1) % len(self.songs_list)
             self.play_music() # Play the new song

    def volume_adjust(self, value):
        """Adjusts the playback volume based on the volume slider."""
        volume = float(value)
        try:
            pygame.mixer.music.set_volume(volume)
        except Exception as e:
            print(f"Warning: Could not set volume: {e}")
            return # Don't update UI if setting volume failed

        # Update Mute button state/text if volume changes
        theme = self.themes[self.current_theme_name]
        base_text_col = COLOR_BLACK if self.current_theme_name == "light" else theme["L6_text_light"]
        accent_col = theme["L3_accent_primary"]

        if volume > 0 and self.muted:
            # Unmuted by slider
            self.muted = False
            if self.volume_button and self.volume_button.winfo_exists():
                self.volume_button.configure(text="VOL", text_color=base_text_col)
        elif volume == 0 and not self.muted:
             # Muted by dragging slider to 0
             self.muted = True
             if self.volume_button and self.volume_button.winfo_exists():
                 self.volume_button.configure(text="MUTED", text_color=accent_col)

        # Store the last non-zero volume
        if volume > 0:
            self.previous_volume = volume


    def toggle_mute(self):
        """Toggles the mute state."""
        theme = self.themes[self.current_theme_name]
        base_text_col = COLOR_BLACK if self.current_theme_name == "light" else theme["L6_text_light"]
        accent_col = theme["L3_accent_primary"]

        if self.muted:
             # --- UNMUTE ---
             try:
                 # Restore previous volume
                 pygame.mixer.music.set_volume(self.previous_volume)
                 # Update slider to match
                 if self.volume_slider and self.volume_slider.winfo_exists():
                     self.volume_slider.set(self.previous_volume)
                 self.muted = False
                 # Update button appearance
                 if self.volume_button and self.volume_button.winfo_exists():
                     self.volume_button.configure(text="VOL", text_color=base_text_col)
             except Exception as e:
                 print(f"Warning: Could not set volume on unmute: {e}")
        else:
             # --- MUTE ---
             try:
                 # Store current volume before muting (if > 0)
                 current_vol = pygame.mixer.music.get_volume()
                 if current_vol > 0:
                     self.previous_volume = current_vol
                 # Set volume to 0
                 pygame.mixer.music.set_volume(0)
                 # Update slider to 0
                 if self.volume_slider and self.volume_slider.winfo_exists():
                     self.volume_slider.set(0)
                 self.muted = True
                 # Update button appearance
                 if self.volume_button and self.volume_button.winfo_exists():
                     self.volume_button.configure(text="MUTED", text_color=accent_col)
             except Exception as e:
                 print(f"Warning: Could not set volume on mute: {e}")

    def toggle_mix(self):
        """Toggles shuffle/mix mode."""
        self.shuffle_state = not self.shuffle_state
        print(f"Mix toggled: {'ON' if self.shuffle_state else 'OFF'}")
        # Update button appearance
        theme = self.themes[self.current_theme_name]
        base_text_col = COLOR_BLACK if self.current_theme_name == "light" else theme["L6_text_light"]
        accent_col = theme["L3_accent_primary"]
        color = accent_col if self.shuffle_state else base_text_col
        if self.mix_button and self.mix_button.winfo_exists():
            self.mix_button.configure(text_color=color)

    def toggle_loop(self):
        """Cycles through loop modes: OFF -> ALL -> ONE -> OFF."""
        self.loop_state = (self.loop_state + 1) % 3 # Cycle 0, 1, 2
        print(f"Loop toggled: State {self.loop_state}") # 0=Off, 1=All, 2=One
        self.apply_loop_button_state() # Update button appearance

    def apply_loop_button_state(self):
        """Updates the loop button text and color based on loop_state."""
        if not (self.loop_button and self.loop_button.winfo_exists()):
            return
        theme = self.themes[self.current_theme_name]
        base_text_col = COLOR_BLACK if self.current_theme_name == "light" else theme["L6_text_light"]
        accent_col = theme["L3_accent_primary"]

        # Set color based on whether looping is active (state 1 or 2)
        color = accent_col if self.loop_state > 0 else base_text_col

        # Set text based on the specific loop mode
        if self.loop_state == 1:
            loop_text = "LOOP ALL"
        elif self.loop_state == 2:
            loop_text = "LOOP ONE"
        else: # loop_state == 0
            loop_text = "LOOP"

        self.loop_button.configure(text_color=color, text=loop_text)

    # --- Slider Interaction ---

    def slider_start_scroll(self, event):
        """Called when the user presses the mouse button on the song slider."""
        # Only activate if there's a song loaded with a valid length
        if self.current_song and self.song_length > 0:
            self.slider_active = True
            # print("Slider press - Active") # Debug log
        else:
            self.slider_active = False # Prevent dragging if no song/length


    def slider_stop_scroll(self, event):
        """Called when the user releases the mouse button from the song slider."""
        if not self.slider_active:
            # print("Slider release - Ignored (was not active)") # Debug log
            return # Do nothing if slider wasn't active

        position = 0.0
        # Get the final position from the slider widget
        if self.song_slider and self.song_slider.winfo_exists():
            position = float(self.song_slider.get())
        else:
             # Should not happen if slider was active, but handle defensively
             self.slider_active = False
             return

        self.slider_active = False # Deactivate slider dragging
        # print(f"Slider release - Seeking to: {position:.2f}s") # Debug log
        self.seek_song(position) # Perform the actual seek


    def slide_song(self, value):
        """Called continuously while the user drags the song slider (due to command)."""
        # Only update visuals if the slider drag is active (Button is pressed)
        if not self.slider_active:
             # print(f"Slide command ignored - slider not active (value: {value})") # Debug log
             return

        position = float(value)
        # Update the current time label display during drag
        mins, secs = divmod(int(position), 60)
        time_str = f"{mins:02d}:{secs:02d}"
        if self.current_time_label and self.current_time_label.winfo_exists():
            self.current_time_label.configure(text=time_str)

        # Update the waveform position indicator during drag
        pos_ratio = np.clip(position / self.song_length, 0.0, 1.0) if self.song_length > 0 else 0.0
        self.draw_waveform_position_indicator(pos_ratio)
        if self.fig_wave and self.fig_wave.canvas:
             try: self.fig_wave.canvas.draw_idle() # Redraw canvas to show indicator move
             except Exception: pass

    # --- Waveform Interaction ---

    def on_waveform_press(self, event):
        """Called when the user clicks on the waveform plot."""
        # Check if click is inside the correct axes and data exists
        if (event.inaxes != self.ax_wave or
            self.waveform_peak_data is None or self.song_length <= 0):
            self.waveform_dragging = False
            return

        self.waveform_dragging = True
        self.slider_active = True # Also set slider active for consistent state handling
        # print("Waveform press - Active") # Debug log
        # Update position immediately based on click location
        self._update_position_from_waveform_event(event)


    def on_waveform_motion(self, event):
        """Called when the mouse moves over the waveform plot while pressed."""
        # Only process if dragging is active and inside the correct axes
        if not self.waveform_dragging or event.inaxes != self.ax_wave:
            return
        # print(f"Waveform motion - xdata: {event.xdata}") # Debug log
        # Update position based on current mouse location
        self._update_position_from_waveform_event(event)

    def on_waveform_release(self, event):
        """Called when the mouse button is released after clicking/dragging on waveform."""
        if not self.waveform_dragging:
            # print("Waveform release - Ignored (was not dragging)") # Debug log
            return

        # Get the target time from the slider (which was updated during drag)
        target_time = 0.0
        if self.song_slider and self.song_slider.winfo_exists():
            target_time = float(self.song_slider.get())
        else:
            # Should not happen if dragging was active, but handle defensively
            self.waveform_dragging = False
            self.slider_active = False
            return

        self.waveform_dragging = False
        self.slider_active = False # Deactivate both flags
        # print(f"Waveform release - Seeking to: {target_time:.2f}s") # Debug log
        self.seek_song(target_time) # Perform the seek


    def on_waveform_leave(self, event):
        """Called when the mouse leaves the waveform plot area."""
        # If the user was dragging and leaves the canvas, treat it as a release
        if self.waveform_dragging:
            print("Waveform leave while dragging - treating as release") # Debug log
            self.on_waveform_release(event) # Trigger the seek


    def _update_position_from_waveform_event(self, event):
        """Helper to calculate time and update UI based on waveform click/drag event."""
        # Validate data needed for calculation
        if (self.waveform_peak_data is None or self.song_length <= 0 or
            event.xdata is None): # event.xdata is the clicked x-coordinate in plot units
            return

        try:
            num_points = len(self.waveform_peak_data)
            # Get plot limits to map xdata correctly
            x_min, x_max_limit = self.ax_wave.get_xlim() # Use actual axis limits
            # Ensure x_max is at least 1 to avoid division by zero if data is very short
            x_max = max(1, x_max_limit)

            # Calculate position ratio based on clicked x-coordinate relative to plot limits
            x_coord = event.xdata
            position_ratio = np.clip((x_coord - x_min) / (x_max - x_min), 0.0, 1.0) if (x_max - x_min) > 0 else 0.0

            # Calculate target time in seconds
            target_time = position_ratio * self.song_length

            # Update the slider position
            if self.song_slider and self.song_slider.winfo_exists():
                self.song_slider.set(target_time)

            # Update the time label
            if self.current_time_label and self.current_time_label.winfo_exists():
                mins, secs = divmod(int(target_time), 60)
                self.current_time_label.configure(text=f"{mins:02d}:{secs:02d}")

            # Update the waveform position indicator line
            self.draw_waveform_position_indicator(position_ratio)
            if self.fig_wave and self.fig_wave.canvas:
                self.fig_wave.canvas.draw_idle() # Redraw waveform plot

        except Exception as e:
            print(f"Error updating position from waveform event: {e}")
            # traceback.print_exc()


    def seek_song(self, position_seconds):
        """Seeks to the specified position in the current song."""
        # Check prerequisites
        if not (self.current_song and self.song_length > 0 and pygame.mixer.get_init()):
            print("Seek ignored: No song, zero length, or mixer not initialized.")
            # Ensure flags are reset if seek fails early
            self.is_seeking = False; self.slider_active = False; self.waveform_dragging = False
            return

        self.is_seeking = True # Set flag to block updates during seek operation
        try:
            self.has_error = False # Clear previous error
            # Clamp requested position to valid range (slightly before end)
            # Subtracting a small amount helps prevent issues seeking exactly to the end
            seek_pos = np.clip(position_seconds, 0.0, self.song_length - 0.1 if self.song_length > 0.1 else 0.0)

            print(f"Seeking to: {seek_pos:.2f}s (requested: {position_seconds:.2f}s)")

            # --- Update internal time immediately ---
            # This is crucial: update the base position before starting playback
            self.stopped_position = seek_pos
            self.song_time = seek_pos # Sync internal timer

            # --- Update UI to reflect seek position ---
            # Slider
            if self.song_slider and self.song_slider.winfo_exists():
                 max_slider_val = self.song_slider.cget("to")
                 self.song_slider.set(min(seek_pos, max_slider_val))
            # Time label
            if self.current_time_label and self.current_time_label.winfo_exists():
                mins, secs = divmod(int(seek_pos), 60)
                self.current_time_label.configure(text=f"{mins:02d}:{secs:02d}")
            # Waveform indicator
            pos_ratio = np.clip(seek_pos / self.song_length, 0.0, 1.0) if self.song_length > 0 else 0.0
            self.draw_waveform_position_indicator(pos_ratio)
            if self.fig_wave and self.fig_wave.canvas:
                try: self.fig_wave.canvas.draw_idle()
                except Exception: pass
            # Update oscilloscope (optional, can show discontinuity)
            if self.raw_sample_data is not None:
                self.update_oscilloscope()

            # --- Perform the actual seek using Pygame ---
            # Note: Pygame requires loading the song again to seek reliably with play(start=...)
            # This might cause a slight delay/hiccup but is safer.
            try:
                # Only call play if music was playing or paused. If stopped, just set the position.
                if self.playing_state or self.paused:
                    was_paused = self.paused # Store state before playing
                    # Reload and play from the seek position
                    # It seems pygame.mixer.music.set_pos() is unreliable/deprecated.
                    # Using stop/load/play(start=...) is the recommended way.
                    pygame.mixer.music.stop() # Stop first
                    pygame.mixer.music.load(self.current_song) # Reload
                    pygame.mixer.music.play(start=seek_pos) # Play from new position

                    # Restore paused state if necessary
                    if was_paused:
                        pygame.mixer.music.pause()
                        self.playing_state = False # Ensure state is consistent
                        self.paused = True
                        if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="▶") # Show play symbol
                    else:
                        self.playing_state = True # Playback is now active
                        self.paused = False
                        if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="II") # Show pause symbol
                        # Restart the update thread only if playback is active
                        self.start_update_thread()

                    self._update_display_title() # Update title based on new state
                else:
                    # If player was stopped, we've already updated stopped_position.
                    # No need to call play(). The next time play is pressed, it will use it.
                     self._update_display_title() # Ensure title is correct (not playing/paused)
                     if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="▶") # Ensure play symbol
                     print(f"Player stopped, updated next start pos to {seek_pos:.2f}s")

            except pygame.error as e:
                print(f"Pygame error on seek's play/pause: {e}")
                self.has_error = True; self._update_display_title()
                # Attempt to reset state cleanly
                self.playing_state = False; self.paused = False;
                if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="▶")
            except Exception as e:
                print(f"General error during seek's play/pause: {e}")
                traceback.print_exc()
                self.has_error = True; self._update_display_title()
                self.playing_state = False; self.paused = False;
                if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="▶")

        finally:
            # Schedule clearing the seeking flag slightly later to allow Pygame to process
            self.root.after(50, self._clear_seeking_flag)


    def _clear_seeking_flag(self):
        """Callback to reset the seeking flag after a short delay."""
        self.is_seeking = False
        # print("Seek flag cleared") # Debug log

    def update_song_info(self):
        """Updates song length, total time display, and slider range using Mutagen."""
        if not self.current_song:
            # Reset if no song is loaded
            self._update_display_title(base_title="NO SONG LOADED")
            if self.total_time_label and self.total_time_label.winfo_exists(): self.total_time_label.configure(text="00:00")
            if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.configure(to=100, number_of_steps=100); self.song_slider.set(0)
            self.song_length = 0.0
            return

        song_name = os.path.basename(self.current_song)
        try:
            file_extension = os.path.splitext(self.current_song)[1].lower()
            audio = None
            # --- Modified file type check for metadata ---
            if file_extension == '.mp3':
                audio = MP3(self.current_song)
            elif file_extension == '.flac':
                audio = FLAC_MUTAGEN(self.current_song)
            elif file_extension == '.ogg':
                 audio = OggVorbis(self.current_song)
            elif file_extension == '.wav':
                 audio = WAVE(self.current_song)
            # --- End Modification ---
            else:
                 # Should ideally not happen if add_songs filters, but handle defensively
                 raise ValueError(f"Unsupported file type for info: {file_extension}")

            # Get length from mutagen info
            if audio and hasattr(audio, 'info') and hasattr(audio.info, 'length'):
                self.song_length = audio.info.length
                # Validate length
                if not isinstance(self.song_length, (int, float)) or self.song_length <= 0:
                     print(f"Warning: Mutagen reported invalid length ({self.song_length}) for {song_name}. Falling back to 0.")
                     self.song_length = 0.0

                # Format total time string
                mins, secs = divmod(int(self.song_length), 60)
                self.total_time = f"{mins:02d}:{secs:02d}"
                if self.total_time_label and self.total_time_label.winfo_exists():
                    self.total_time_label.configure(text=self.total_time)

                # Configure slider range based on song length
                # Use max(1.0, ...) to prevent slider having zero range
                slider_max = max(1.0, self.song_length)
                # More steps for longer songs can feel smoother (optional)
                num_steps = max(100, int(slider_max * 10))
                if self.song_slider and self.song_slider.winfo_exists():
                    self.song_slider.configure(to=slider_max, number_of_steps=num_steps)

                # Reset slider position only if starting fresh (not resuming)
                if self.stopped_position == 0 and not self.playing_state and not self.paused:
                    if self.song_slider and self.song_slider.winfo_exists():
                        self.song_slider.set(0)
                    if self.current_time_label and self.current_time_label.winfo_exists():
                        self.current_time_label.configure(text="00:00")

            else:
                raise ValueError(f"Mutagen could not read info/length for {song_name}")

        except Exception as e:
            # Handle errors reading metadata
            print(f"Error getting song info for {song_name}: {e}")
            self.has_error = True # Indicate error state
            self._update_display_title(base_title=song_name) # Show filename with error prefix
            self.song_length = 0.0
            self.total_time = "00:00"
            # Reset UI elements
            if self.total_time_label and self.total_time_label.winfo_exists(): self.total_time_label.configure(text=self.total_time)
            if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.configure(to=100, number_of_steps=100); self.song_slider.set(0)
            if self.current_time_label and self.current_time_label.winfo_exists(): self.current_time_label.configure(text="00:00")

    # --- Waveform Generation ---

    def trigger_waveform_generation(self):
        """Initiates background waveform data generation for the current song."""
        # Abort previous generation if still running
        if self.waveform_thread and self.waveform_thread.is_alive():
            print("Aborting previous waveform generation thread...")
            self.abort_waveform_generation()
            # Give the old thread a moment to exit
            # self.waveform_thread.join(timeout=0.1) # Optional wait
            time.sleep(0.05) # Short sleep instead of join to avoid blocking UI


        if not self.current_song:
            print("Waveform generation skipped: No current song.")
            return

        # Reset data and set state
        self.waveform_peak_data = None
        self.raw_sample_data = None
        self.sample_rate = None
        self.is_generating_waveform = True
        self.has_error = False # Clear previous error status
        self._update_display_title() # Show "GENERATING..."

        # Show placeholder on plots
        theme = self.themes[self.current_theme_name]
        spine_color = theme['plot_spine']
        self.draw_initial_placeholder(self.ax_wave, self.fig_wave, spine_color,"GENERATING...")
        self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color,"")

        # Start the background thread
        self.waveform_abort_flag.clear() # Ensure flag is clear before starting
        self.waveform_thread = threading.Thread(
            target=self.generate_waveform_data_background,
            args=(self.current_song, self.waveform_abort_flag), # Pass path and abort flag
            daemon=True # Allows application to exit even if thread is running
        )
        self.waveform_thread.start()
        print(f"Started waveform generation thread for: {os.path.basename(self.current_song)}")


    def generate_waveform_data_background(self, song_path, abort_flag):
        """
        Background thread function to load audio data using soundfile
        and generate peak data for waveform and raw data for oscilloscope.
        """
        local_peak_data = None
        local_raw_data = None
        effective_sample_rate = None
        error_message = None
        print(f"BG_THREAD: Starting waveform generation for {os.path.basename(song_path)}")

        try:
            start_time = time.monotonic()

            # --- Check for abort signal frequently ---
            if abort_flag.is_set():
                print("BG_THREAD: Aborted before loading.")
                return

            # --- Load Audio using soundfile ---
            # soundfile supports many formats (MP3, FLAC, OGG, WAV etc.) via libsndfile
            # always_2d=True ensures consistent shape even for mono files
            if not os.path.exists(song_path):
                raise FileNotFoundError(f"Audio file not found: {song_path}")

            try:
                audio_data, original_sample_rate = sf.read(song_path, dtype='float64', always_2d=True)
            except sf.SoundFileError as sf_err:
                 # More specific error catching for soundfile issues
                 error_message = f"WAVEFORM ERROR\nSoundfile Error\n({sf_err})"
                 print(f"BG_THREAD: SoundFileError: {sf_err}")
                 raise # Re-raise to be caught by the general exception handler below
            except Exception as load_err:
                 # Catch other potential loading errors (permissions, etc.)
                 print(f"BG_THREAD: Error loading audio with soundfile: {load_err}")
                 # Check specifically for missing libsndfile library
                 if "sndfile library not found" in str(load_err).lower():
                     raise ImportError(f"libsndfile not found. Soundfile cannot operate. Error: {load_err}")
                 else:
                     raise RuntimeError(f"Soundfile load failed: {load_err}")


            if abort_flag.is_set():
                 print("BG_THREAD: Aborted after loading.")
                 return

            # --- Process Audio Data ---
            if audio_data.size == 0:
                raise ValueError("Audio file contains no samples.")

            # Convert to mono if stereo by averaging channels
            if audio_data.shape[1] > 1:
                mono_samples_normalized = audio_data.mean(axis=1)
            else:
                mono_samples_normalized = audio_data[:, 0]

            # Check for silence (optional, but can be informative)
            if not np.any(mono_samples_normalized):
                 print(f"Warning: Audio file {os.path.basename(song_path)} appears to be silent.")

            # --- Check for abort signal ---
            if abort_flag.is_set():
                 print("BG_THREAD: Aborted before processing raw/peak data.")
                 return

            # --- Prepare Data for Oscilloscope (Downsample if needed) ---
            if self.osc_downsample_factor > 1:
                 # Take every Nth sample
                 local_raw_data = mono_samples_normalized[::self.osc_downsample_factor]
                 effective_sample_rate = original_sample_rate / self.osc_downsample_factor
            else:
                 local_raw_data = mono_samples_normalized
                 effective_sample_rate = original_sample_rate

            # --- Check for abort signal ---
            if abort_flag.is_set():
                 print("BG_THREAD: Aborted before generating peak data.")
                 return

            # --- Generate Peak Data for Static Waveform ---
            # Aim for a fixed number of points for the visual waveform
            target_points = 500 # Adjust for desired detail vs performance
            num_samples = len(mono_samples_normalized)

            if num_samples > 0:
                # Calculate chunk size to get roughly target_points
                chunk_size = max(1, num_samples // target_points)
                processed_peaks = []
                num_chunks = (num_samples + chunk_size - 1) // chunk_size # Ceiling division

                # Iterate through chunks and find the peak (max absolute value) in each
                for i in range(num_chunks):
                     # --- Check for abort signal periodically inside loop ---
                     if i % 50 == 0 and abort_flag.is_set(): # Check every 50 chunks
                          print(f"BG_THREAD: Aborted during peak generation (chunk {i}).")
                          return

                     start = i * chunk_size
                     end = min((i + 1) * chunk_size, num_samples)
                     chunk = mono_samples_normalized[start:end]

                     # Find peak (max absolute value) in the chunk
                     peak = np.max(np.abs(chunk)) if len(chunk) > 0 else 0.0
                     processed_peaks.append(peak)

                local_peak_data = np.array(processed_peaks)
            else:
                # Handle empty audio case
                local_peak_data = np.array([])


            # --- Generation Complete ---
            end_time = time.monotonic()
            print(f"BG_THREAD: Waveform gen (soundfile) finished: {os.path.basename(song_path)} in {end_time - start_time:.2f}s")

        # --- Error Handling ---
        except ImportError as e:
             # Specific error for missing dependencies like libsndfile
             error_message = f"WAVEFORM ERROR\nDependency Missing?\n(e.g., libsndfile)\n{e}"
             print(f"BG_THREAD: ImportError: {e}")
        except FileNotFoundError as e:
            error_message = f"WAVEFORM ERROR\nFile Not Found\n({e})"
            print(f"BG_THREAD: FileNotFoundError: {e}")
        except PermissionError as e:
             error_message = f"WAVEFORM ERROR\nPermission Denied\n({e})"
             print(f"BG_THREAD: PermissionError: {e}")
        except MemoryError:
             # Handle cases where the file is too large to load into memory
             error_message = "WAVEFORM ERROR\nMemory Error"
             print(f"BG_THREAD: MemoryError loading {os.path.basename(song_path)}")
        except ValueError as e:
             # Handle invalid audio data (e.g., empty file, format issues not caught by sf.read)
             error_message = f"WAVEFORM ERROR\nInvalid Audio Data\n({e})"
             print(f"BG_THREAD: ValueError: {e}")
        except RuntimeError as e:
             # Catch runtime errors, potentially from soundfile internal issues
             error_message = f"WAVEFORM ERROR\nLoad/Process Error\n({e})"
             print(f"BG_THREAD: RuntimeError: {e}")
        except Exception as e:
             # Generic catch-all for unexpected errors
             print(f"BG_THREAD: UNEXPECTED error generating waveform (soundfile):")
             traceback.print_exc() # Print full traceback for debugging
             error_message = f"WAVEFORM ERROR\nUnexpected Error\n({type(e).__name__})"

        # --- Final Step: Send results back to main thread ---
        finally:
            if not abort_flag.is_set():
                 # Check if root window still exists before scheduling callback
                 if hasattr(self, 'root') and self.root.winfo_exists():
                     # Use root.after to safely pass data back to the main thread
                     self.root.after(1, self.process_waveform_result, song_path, local_peak_data, local_raw_data, effective_sample_rate, error_message)
                 else:
                      print("BG_THREAD: Root window closed, skipping result processing.")
            else:
                 # If aborted, don't send potentially incomplete results
                 print(f"BG_THREAD: Waveform generation was aborted for {os.path.basename(song_path)}, result not processed.")


    def process_waveform_result(self, song_path, peak_data, raw_data, sample_rate, error_message):
        """Processes the waveform data received from the background thread."""
        # Check if the result is still relevant (user might have switched songs)
        if song_path != self.current_song:
            print(f"Waveform result for '{os.path.basename(song_path)}' ignored (song changed).")
            # Ensure generating flag is cleared if this was the active generation task
            if self.is_generating_waveform and self.waveform_thread and not self.waveform_thread.is_alive():
                 self.is_generating_waveform = False
                 # Don't update title here, let the new song's process handle it
            return

        # Mark generation as complete
        self.is_generating_waveform = False
        theme = self.themes[self.current_theme_name]
        spine_color = theme['plot_spine']

        if error_message:
            # Handle error case
            self.waveform_peak_data = None
            self.raw_sample_data = None
            self.sample_rate = None
            self.has_error = True
            self._update_display_title(base_title=os.path.basename(song_path)) # Show error in title
            # Display error message on the waveform plot
            self.draw_initial_placeholder(self.ax_wave, self.fig_wave, spine_color, error_message)
            self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color, "") # Clear oscilloscope
            print(f"Waveform generation failed for {os.path.basename(song_path)}: {error_message.replace('/n', ' - ')}") # Log flattened error
        elif peak_data is not None and raw_data is not None and sample_rate is not None:
            # Handle success case
            self.waveform_peak_data = peak_data
            self.raw_sample_data = raw_data
            self.sample_rate = sample_rate
            self.has_error = False
            self._update_display_title() # Update title (remove generating prefix)
            # Draw the newly generated waveform
            self.draw_static_matplotlib_waveform()
            # Update position immediately in case song started playing during generation
            self.update_song_position() # This will also trigger oscilloscope update if playing
            print(f"Waveform generated successfully for: {os.path.basename(song_path)}")
        else:
             # Handle unexpected case where thread finished without error but data is missing
             self.waveform_peak_data = None; self.raw_sample_data = None; self.sample_rate = None; self.has_error = True
             self._update_display_title(base_title=os.path.basename(song_path))
             self.draw_initial_placeholder(self.ax_wave, self.fig_wave, spine_color,"GEN FAILED (Internal)")
             self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color,"")
             print(f"Waveform generation failed internally (missing data) for: {os.path.basename(song_path)}")

    # --- Matplotlib Drawing Functions ---

    def draw_static_matplotlib_waveform(self):
        """Draws the full waveform using the processed peak data."""
        ax = self.ax_wave
        fig = self.fig_wave
        data = self.waveform_peak_data
        theme = self.themes[self.current_theme_name]
        spine_color = theme['plot_spine']

        # Check if data and plot objects are valid
        if data is None or not ax or not fig or not fig.canvas:
            if ax and fig and fig.canvas: # Only draw placeholder if canvas exists
                 placeholder_msg = "NO WAVEFORM DATA" if self.current_song else "LOAD A SONG"
                 self.draw_initial_placeholder(ax, fig, spine_color, placeholder_msg)
            return

        try:
            ax.clear() # Clear previous plot content
            self._configure_axes(ax, fig, spine_color, theme["plot_bg"]) # Apply theme

            if len(data) > 0:
                 # Create x-axis values (indices of peak data)
                 x = np.arange(len(data))
                 # Scale data slightly below 1 for visual padding
                 y = data * 0.9
                 # Clip just in case data exceeds 1 (shouldn't if normalized correctly)
                 y = np.clip(y, 0.0, 0.95)

                 # Use fill_between for a filled waveform shape
                 ax.fill_between(x, 0 - y, 0 + y, color=theme['plot_wave_main'], linewidth=0) # No outline

                 # Set plot limits
                 ax.set_ylim(-1, 1)
                 ax.set_xlim(0, len(data) - 1 if len(data) > 1 else 1) # Handle single point case

            else:
                 # Draw a flat line if data is empty
                 ax.set_ylim(-1, 1)
                 ax.set_xlim(0, 1)
                 ax.plot([0, 1], [0, 0], color=theme['plot_wave_main'], linewidth=0.5)

            # Reset and redraw the position indicator
            self.position_indicator_line_wave = None # Clear old reference
            # Calculate current position ratio
            current_display_time = np.clip(self.song_time, 0.0, self.song_length if self.song_length > 0 else self.song_time)
            pos_ratio = np.clip(current_display_time / self.song_length, 0.0, 1.0) if self.song_length > 0 else 0.0
            self.draw_waveform_position_indicator(pos_ratio) # Draw the line at the correct spot

            # Redraw the canvas
            try:
                 fig.canvas.draw_idle()
            except Exception: pass # Ignore if canvas not ready


        except Exception as e:
            print(f"Error drawing static waveform: {e}")
            traceback.print_exc()
            # Attempt to draw error placeholder
            self.draw_initial_placeholder(ax, fig, spine_color, "DRAW ERROR")


    def draw_waveform_position_indicator(self, position_ratio):
        """Draws or updates the vertical line indicating playback position on the waveform."""
        ax = self.ax_wave
        fig = self.fig_wave
        data = self.waveform_peak_data
        line_attr = 'position_indicator_line_wave' # Attribute name to store the line object
        theme = self.themes[self.current_theme_name]
        indicator_col = theme['plot_wave_indicator']

        # Check prerequisites
        if not ax or not fig or not fig.canvas:
            # print("Indicator draw skipped: No canvas") # Debug
            return

        try:
            # --- Remove previous line ---
            old_line = getattr(self, line_attr, None)
            if old_line and old_line in ax.lines:
                try:
                    old_line.remove()
                    # print("Removed old indicator line") # Debug
                except (ValueError, AttributeError, RuntimeError): # Catch potential errors if line is invalid
                    # print("Could not remove old indicator line") # Debug
                    pass
            setattr(self, line_attr, None) # Clear attribute even if removal failed


            # --- Calculate position ---
            # Use waveform data length to determine x-axis scale
            num_points = len(data) if data is not None else 0
            # Get actual plot limits to be precise
            x_min, x_max_limit = ax.get_xlim()
            x_max = max(1, x_max_limit) # Ensure range is at least 1

            # Calculate the x-coordinate for the line based on the ratio and plot limits
            position_ratio = np.clip(position_ratio, 0.0, 1.0)
            x_pos = x_min + (position_ratio * (x_max - x_min))

            # Ensure x_pos is within the actual limits after calculation
            x_pos = max(x_min, min(x_pos, x_max))

            # print(f"Drawing indicator at ratio {position_ratio:.3f}, x_pos {x_pos:.2f}") # Debug

            # --- Draw new line ---
            if ax: # Double-check axes still exists
                 # Use axvline for a vertical line across the axes
                 # ymin/ymax restrict line vertically (0=bottom, 1=top)
                 new_line = ax.axvline(x=x_pos, color=indicator_col, linewidth=1.2, ymin=0.05, ymax=0.95)
                 setattr(self, line_attr, new_line) # Store reference to the new line

        except Exception as e:
            print(f"Error drawing position indicator: {e}")
            traceback.print_exc()
            # Ensure attribute is cleared on error
            setattr(self, line_attr, None)

    def update_oscilloscope(self):
        """Updates the oscilloscope display based on current playback time."""
        ax = self.ax_osc
        fig = self.fig_osc
        theme = self.themes[self.current_theme_name]
        spine_color = theme['plot_spine']
        osc_col = theme['plot_osc_main']
        bg_col = theme['plot_bg']

        # --- Conditions to skip update or clear display ---
        if (self.raw_sample_data is None or len(self.raw_sample_data) == 0 or
            self.sample_rate is None or self.sample_rate <= 0 or
            not self.playing_state or self.paused or self.is_seeking or # Don't update if paused, seeking, or stopped
            not ax or not fig or not fig.canvas):

            # If stopped/paused/seeking, clear the oscilloscope plot
            if (not self.playing_state or self.paused or self.is_seeking) and \
               ax and fig and fig.canvas and len(ax.lines) > 0: # Only clear if something is drawn
                self.draw_initial_placeholder(ax, fig, spine_color, "")
            return

        try:
            # --- Calculate sample range to display ---
            # Current position in samples
            current_sample_index = int(self.song_time * self.sample_rate)
            # Number of samples in the desired time window
            window_samples = int(self.osc_window_seconds * self.sample_rate)
            if window_samples <= 0: # Fallback if calculation fails
                window_samples = max(100, int(0.02 * self.sample_rate)) # e.g., 20ms fallback

            # Calculate start and end indices, clamping to data bounds
            start_index = max(0, current_sample_index)
            end_index = min(len(self.raw_sample_data), start_index + window_samples)
            # Adjust start index if end_index hit the boundary, to ensure full window width
            start_index = max(0, end_index - window_samples)

            sample_slice = self.raw_sample_data[start_index:end_index]

            # --- Draw the slice ---
            if len(sample_slice) > 0:
                ax.clear() # Clear previous oscilloscope frame
                self._configure_axes(ax, fig, spine_color, bg_col) # Apply theme
                ax.set_ylim(-1.1, 1.1) # Ensure y-limits are set

                # Create x-axis (simple range for the slice)
                x_osc = np.arange(len(sample_slice))
                # Plot the sample slice, clipping values just in case
                ax.plot(x_osc, np.clip(sample_slice, -1.0, 1.0), color=osc_col, linewidth=0.8)
                # Set x-limits to fit the slice exactly
                ax.set_xlim(0, len(sample_slice) - 1 if len(sample_slice) > 1 else 1)

                # Redraw the oscilloscope canvas
                try:
                    fig.canvas.draw_idle()
                except Exception: pass # Ignore if canvas not ready

            elif len(ax.lines) > 0: # If slice is empty, clear the plot
                self.draw_initial_placeholder(ax, fig, spine_color, "")

        except Exception as e:
            # Prevent errors here from crashing the update loop
            print(f"Error updating oscilloscope: {e}")
            # Optionally clear plot on error:
            # self.draw_initial_placeholder(ax, fig, spine_color, "")


    # --- Time Update Logic ---

    def update_song_position(self):
        """Updates the current time label, slider, and visual indicators during playback."""
        # Skip update if user is interacting with slider/waveform or seeking
        if self.slider_active or self.waveform_dragging or self.is_seeking:
            return

        if self.playing_state and not self.paused:
             try:
                 # Check if mixer is still initialized and music is playing
                 if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                     # Get time elapsed since the last play() or unpause() call (in ms)
                     current_pos_ms = pygame.mixer.music.get_pos()

                     if current_pos_ms != -1: # -1 indicates an error or not playing
                         # Calculate absolute time: base position + elapsed time
                         time_since_last_play_sec = current_pos_ms / 1000.0
                         current_abs_time = self.stopped_position + time_since_last_play_sec

                         # --- Sanity Check / Prevent runaway time ---
                         # Add a small buffer to song length check
                         buffer = 0.1
                         current_abs_time = np.clip(current_abs_time, 0.0, (self.song_length + buffer) if self.song_length > 0 else current_abs_time + 1.0) # Clip to length + buffer
                         self.song_time = current_abs_time # Update internal time tracker

                         # --- Update UI elements ---
                         # Use time clipped to actual song length for display
                         display_time_for_ui = np.clip(self.song_time, 0.0, self.song_length if self.song_length > 0 else self.song_time)

                         # Update Slider (if not being dragged)
                         if self.song_slider and self.song_slider.winfo_exists():
                             max_slider_val = self.song_slider.cget("to")
                             self.song_slider.set(min(display_time_for_ui, max_slider_val))

                         # Update Time Label
                         if self.current_time_label and self.current_time_label.winfo_exists():
                             mins, secs = divmod(int(display_time_for_ui), 60)
                             time_elapsed_str = f"{mins:02d}:{secs:02d}"
                             # Only update label if text changed to reduce flicker/overhead
                             if self.current_time_label.cget("text") != time_elapsed_str:
                                 self.current_time_label.configure(text=time_elapsed_str)

                         # Update Waveform Indicator
                         pos_ratio = np.clip(display_time_for_ui / self.song_length, 0.0, 1.0) if self.song_length > 0 else 0
                         self.draw_waveform_position_indicator(pos_ratio)
                         # Redraw waveform canvas (needed for indicator update)
                         if self.fig_wave and self.fig_wave.canvas:
                             try: self.fig_wave.canvas.draw_idle()
                             except Exception: pass # Ignore if canvas not ready

                         # Update Oscilloscope
                         self.update_oscilloscope()

                     # else: get_pos() returned -1, might be end of song or error

                 else: # Mixer not init or music not busy (i.e., stopped)
                     # Check if this happened unexpectedly while self.playing_state is true
                     if hasattr(self, 'root') and self.root.winfo_exists() and self.playing_state:
                        # Potential end-of-song condition or unexpected stop
                        # Use song_time and song_length for check
                        is_past_end = (self.song_length > 0 and self.song_time >= self.song_length - 0.05) # Check slightly before end
                        mixer_really_stopped = pygame.mixer.get_init() and not pygame.mixer.music.get_busy()

                        # If mixer stopped OR we are past the calculated end time, trigger end check
                        if is_past_end or mixer_really_stopped:
                            if hasattr(self, 'root') and self.root.winfo_exists():
                                # Schedule the check on the main thread to handle UI/state changes safely
                                self.root.after(50, self.check_music_end_on_main_thread)
                        # else: Normal playback, just hasn't reached end yet

             except pygame.error as e:
                 # Handle Pygame errors during update (e.g., mixer died)
                 print(f"Pygame error in update_song_position: {e}")
                 self.has_error = True
                 if hasattr(self, 'root') and self.root.winfo_exists(): self._update_display_title()
                 self.stop() # Attempt to stop cleanly
             except Exception as e:
                 # Catch other unexpected errors in the update logic
                 if hasattr(self, 'root') and self.root.winfo_exists(): # Check if window exists
                     print(f"Error during UI update: {e}")
                     # traceback.print_exc() # Optional detailed traceback
                 # Stop the update thread if unexpected errors occur
                 self.thread_running = False


    def start_update_thread(self):
        """Starts the background thread for updating time if not already running."""
        # Only start if playing, not paused, and thread isn't already marked as running
        if not self.thread_running and self.playing_state and not self.paused:
            self.thread_running = True
            # Prevent starting multiple threads if one is already assigned and alive
            if self.update_thread and self.update_thread.is_alive():
                # print("Update thread already running.") # Debug
                return
            # Create and start the thread
            self.update_thread = threading.Thread(target=self.update_time, daemon=True)
            self.update_thread.start()
            # print("Update thread started.") # Debug
        elif not self.playing_state or self.paused:
            # If state changed to non-playing/paused, ensure thread flag is off
            self.thread_running = False


    def update_time(self):
        """Background thread function to periodically trigger UI updates."""
        # Update frequency (e.g., 20 times per second)
        # Lower value = smoother updates but more CPU usage
        # Higher value = less smooth but less CPU usage
        update_interval = 0.05 # seconds (20 Hz)

        while self.thread_running:
            start_loop_time = time.monotonic()
            try:
                # --- Schedule UI update on main thread ---
                # Check if root window still exists before calling 'after'
                if hasattr(self, 'root') and self.root.winfo_exists():
                    # root.after(0, ...) schedules the function to run ASAP in the main event loop
                    self.root.after(0, self.update_song_position)
                else:
                    # Root window closed, stop the thread
                    print("Update thread stopping: Root window destroyed.")
                    self.thread_running = False
                    break # Exit the loop

            except Exception as e:
                 # Catch errors related to scheduling the update (e.g., Tkinter errors)
                 if "application has been destroyed" in str(e).lower() or \
                    "invalid command name" in str(e).lower():
                     print("Update thread stopping: Tkinter object destroyed.")
                 else:
                     print(f"Update thread error: {e}")
                     # traceback.print_exc() # Optional detailed traceback
                 self.thread_running = False # Stop thread on error
                 break # Exit the loop

            # --- Calculate sleep time ---
            # Sleep for the remainder of the interval to maintain update frequency
            time_taken = time.monotonic() - start_loop_time
            sleep_time = max(0, update_interval - time_taken)
            time.sleep(sleep_time)

            # Check running condition again at end of loop (might have changed during sleep)
            if not self.playing_state or self.paused:
                self.thread_running = False
                # print("Update thread stopping: Playback stopped/paused.") # Debug

        # print("Update thread finished.") # Debug


    def check_music_end_on_main_thread(self):
        """Checks if the music has finished playing and handles end-of-song actions."""
        # Ensure runs on main thread and window exists
        if not (hasattr(self, 'root') and self.root.winfo_exists()):
            return
        # Don't check if paused, seeking, or already stopped
        if not self.playing_state or self.paused or self.is_seeking:
            return

        try:
            # --- Conditions for song end ---
            # 1. Time reached or passed song length (with tolerance)
            is_at_end = (self.song_length > 0 and self.song_time >= self.song_length - 0.05)
            # 2. Pygame mixer reports music is no longer busy
            mixer_stopped = pygame.mixer.get_init() and not pygame.mixer.music.get_busy()
            # 3. Pygame mixer get_pos() returns -1 (can happen at end or on error)
            mixer_pos_error = False
            if pygame.mixer.get_init():
                 try:
                      mixer_pos_error = (pygame.mixer.music.get_pos() == -1)
                 except pygame.error:
                      mixer_pos_error = True # Treat pygame error as potential stop

            # --- If any end condition is met ---
            if mixer_stopped or mixer_pos_error or is_at_end:
                 # Prevent multiple triggers by ensuring we are still in 'playing' state logically
                 if not self.playing_state: return

                 print(f"Detected song end: {os.path.basename(self.current_song)} (MixerStopped: {mixer_stopped}, MixerPosError: {mixer_pos_error}, IsAtEnd: {is_at_end})")

                 # --- Update State ---
                 self.playing_state = False # No longer playing
                 self.paused = False
                 self.thread_running = False # Stop update thread
                 # Set final position accurately to song length if known
                 final_pos = self.song_length if self.song_length > 0 else 0
                 self.stopped_position = final_pos
                 self.song_time = final_pos

                 # --- Update UI ---
                 # Set slider/time to the very end
                 if self.song_length > 0:
                     if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.set(self.song_length)
                     if self.current_time_label and self.current_time_label.winfo_exists(): mins, secs = divmod(int(self.song_length), 60); self.current_time_label.configure(text=f"{mins:02d}:{secs:02d}")
                     self.draw_waveform_position_indicator(1.0) # Move indicator to end
                 else: # Reset if length is unknown
                     if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.set(0);
                     if self.current_time_label and self.current_time_label.winfo_exists(): self.current_time_label.configure(text="00:00");
                     self.draw_waveform_position_indicator(0.0)

                 # Redraw wave plot
                 if self.fig_wave and self.fig_wave.canvas:
                      try: self.fig_wave.canvas.draw_idle()
                      except Exception: pass
                 # Reset play button
                 if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="▶")
                 # Clear oscilloscope
                 theme = self.themes[self.current_theme_name]; spine_color = theme['plot_spine']
                 self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color, "")
                 # Update title (remove playing prefix)
                 self._update_display_title()

                 # --- Schedule Next Action ---
                 # Use root.after to handle next song/loop action in the main loop
                 # This prevents modifying state directly within the check function
                 if hasattr(self, 'root') and self.root.winfo_exists():
                      self.root.after(50, self.handle_song_end_action) # Short delay

            # Handle unexpected mixer stop
            elif not pygame.mixer.get_init():
                 print("Mixer stopped unexpectedly.")
                 self.stop() # Try to stop cleanly

        except pygame.error as e:
             print(f"Pygame error during end check: {e}")
             self.has_error=True; self._update_display_title(); self.stop()
        except Exception as e:
             print(f"Error during end check: {e}")
             traceback.print_exc()
             self.has_error=True; self._update_display_title(); self.stop()

    def handle_song_end_action(self):
        """Determines what action to take after a song finishes based on loop/mix state."""
        # Ensure runs on main thread and window exists
        if not (hasattr(self, 'root') and self.root.winfo_exists()):
            return

        theme = self.themes[self.current_theme_name]
        spine_color = theme['plot_spine']

        # --- Loop One ---
        if self.loop_state == 2: # Loop One
             print("Looping current song.")
             # Reset UI for replay
             if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.set(0);
             if self.current_time_label and self.current_time_label.winfo_exists(): self.current_time_label.configure(text="00:00");
             # Just call play_music again for the current index
             self.play_music()

        # --- Loop All ---
        elif self.loop_state == 1: # Loop All
             print("Looping all - playing next.")
             # Call next_song with auto_advance flag
             self.next_song(auto_advance=True)

        # --- Mix / Shuffle ---
        elif self.shuffle_state:
             print("Mix on - playing random.")
             self.play_random_song(auto_advance=True)

        # --- No Loop / End of Playlist ---
        else: # loop_state == 0 and not shuffle_state
             # Check if it was the last song in the list
             if self.current_song_index >= len(self.songs_list) - 1:
                 print("End of tracklist reached.")
                 # Keep the last song's info displayed but reset playback state
                 last_song_name = os.path.basename(self.current_song) if self.current_song else "TRACKLIST END"
                 self.stop() # Ensure stopped state
                 # Reset position variables for potential future play
                 self.stopped_position = 0.0
                 self.song_time = 0.0
                 # Optionally reset index to 0 or keep it at the end
                 self.current_song_index = 0 # Reset to start for next play action
                 if self.songs_list: self.select_song(self.current_song_index) # Select first song

                 # Reset UI elements to initial state
                 if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.set(0);
                 if self.current_time_label and self.current_time_label.winfo_exists(): self.current_time_label.configure(text="00:00");
                 self.draw_waveform_position_indicator(0) # Indicator to start
                 if self.fig_wave and self.fig_wave.canvas:
                     try: self.fig_wave.canvas.draw_idle()
                     except Exception: pass
                 self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color,"") # Clear osc
                 self._update_display_title(base_title=last_song_name) # Show last song title (not playing)
                 if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="▶") # Show play symbol

             else: # Not the last song, play next in sequence
                 print("Playing next song in sequence.")
                 self.next_song(auto_advance=True)


    def play_random_song(self, auto_advance=False):
        """Plays a random song from the list, avoiding immediate repeat if possible."""
        if not self.songs_list:
            self.stop() # Stop if playlist became empty
            return

        # Handle state reset if auto-advancing
        if not auto_advance:
            self.stop()
        else:
             # Reset state without explicit stop() call
             self.playing_state = False; self.paused = False; self.thread_running = False;
             self.abort_waveform_generation(); # Abort previous gen
             self.stopped_position = 0.0; self.song_time = 0.0;
             print("Auto-advancing to random song.")

        if len(self.songs_list) > 1:
             # Create list of possible indices (all except current)
             possible_indices = [i for i in range(len(self.songs_list)) if i != self.current_song_index]
             # If list had only one song, possible_indices will be empty. Fallback to full list.
             if not possible_indices:
                 possible_indices = list(range(len(self.songs_list)))
             # Choose a random index from the possibilities
             self.current_song_index = random.choice(possible_indices)
        elif len(self.songs_list) == 1:
            # Only one song, just play it
            self.current_song_index = 0
        else:
            # Should not happen if initial check passed, but handle defensively
            self.clear_playlist() # Clear everything if list is somehow invalid
            return

        # Play the chosen song
        self.play_music()


    def abort_waveform_generation(self):
        """Signals the waveform generation thread to stop."""
        if self.waveform_thread and self.waveform_thread.is_alive():
            if not self.waveform_abort_flag.is_set():
                 print(f"Signalling waveform thread to abort...")
                 self.waveform_abort_flag.set() # Set the event flag
                 # Update UI immediately if it was in generating state
                 if self.is_generating_waveform:
                      self.is_generating_waveform = False
                      # If the title still shows generating, update it
                      if self.current_song and "[GENERATING...]" in self.song_title_var.get():
                          try:
                              # Schedule update on main thread
                              if hasattr(self, 'root') and self.root.winfo_exists():
                                   self.root.after(0, self._update_display_title)
                          except Exception: pass # Ignore if root is gone


    # --- Closing ---
    def on_closing(self):
        """Handles cleanup when the application window is closed."""
        print("Closing application...")
        # Stop background threads safely
        self.thread_running = False # Signal update thread to stop
        self.abort_waveform_generation() # Signal waveform thread to stop

        # Stop Pygame
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
                print("Pygame stopped.")
        except Exception as e:
            print(f"Error quitting pygame: {e}")

        # Close Matplotlib figures to release resources
        try:
            if self.fig_wave: plt.close(self.fig_wave)
        except Exception: pass
        try:
            if self.fig_osc: plt.close(self.fig_osc)
        except Exception: pass

        # Wait briefly for threads to exit (optional, daemon threads shouldn't block exit)
        if self.waveform_thread and self.waveform_thread.is_alive():
            print("Waiting for waveform thread to join...")
            self.waveform_thread.join(timeout=0.3) # Short timeout
            if self.waveform_thread.is_alive(): print("Waveform thread did not join cleanly.")

        if self.update_thread and self.update_thread.is_alive():
             print("Waiting for update thread to join...")
             self.update_thread.join(timeout=0.3) # Short timeout
             if self.update_thread.is_alive(): print("Update thread did not join cleanly.")


        # Destroy the Tkinter window
        if hasattr(self, 'root') and self.root:
            try:
                if self.root.winfo_exists():
                     self.root.destroy()
                     print("Application closed.")
                else:
                     print("Root window already destroyed.")
            except Exception as e:
                print(f"Error destroying root window: {e}")

# --- Main Execution Block ---
if __name__ == "__main__":
    try:
        # --- Set DPI awareness on Windows (optional but recommended) ---
        if os.name == 'nt':
             try:
                from ctypes import windll
                # Try modern API first
                try: windll.shcore.SetProcessDpiAwareness(1) # Argument 1 means System Aware
                except AttributeError:
                    # Fallback for older Windows versions
                    try: windll.user32.SetProcessDPIAware()
                    except AttributeError: pass # No DPI awareness setting possible
             except Exception as dpi_error:
                 print(f"Could not set DPI awareness: {dpi_error}")

        # --- Initialize Tkinter ---
        root = ctk.CTk()
        # Removed minsize constraint to allow full resizing flexibility
        # root.minsize(600, 450)

        # --- Create and Run Player ---
        player = MN1MusicPlayer (root)
        root.mainloop()

    except Exception as main_error:
        # --- Fatal Error Handling ---
        print("\n--- FATAL APPLICATION ERROR ---")
        print(f"Error: {main_error}")
        traceback.print_exc() # Print full traceback to console

        # Try to show a simple Tkinter error message box as a fallback
        try:
            import tkinter as tk
            from tkinter import messagebox
            root_err = tk.Tk()
            root_err.withdraw() # Hide the empty root window
            messagebox.showerror("Fatal Error", f"A critical error occurred:\n\n{main_error}\n\nPlease check the console output for details.")
            root_err.destroy()
        except Exception:
            pass # Ignore if even the fallback messagebox fails

        # Keep console open until user presses Enter
        input("Press Enter to exit console.")