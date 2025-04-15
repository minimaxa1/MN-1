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
from pydub import AudioSegment # Requires ffmpeg/ffprobe
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import traceback

# --- Color Definitions ---
COLOR_BLACK = "#000000"; COLOR_WHITE = "#FFFFFF"; COLOR_NEAR_WHITE = "#F5F5F5"
# COLOR_CREAM = "#FFFDD0" # Removed Cream Color
COLOR_DEEP_RED = "#8B0000"; COLOR_LIGHT_RED_HOVER = "#A52A2A"; COLOR_BRIGHT_RED = "#FF0000"
COLOR_DARK_GRAY = "#333333"; COLOR_LIGHT_GRAY = "#D3D3D3"; COLOR_MID_GRAY = "#404040"
COLOR_DARKER_MID_GRAY = "#505050"; COLOR_LIGHTER_MID_GRAY = "#666666"
COLOR_GOLD = "#FFD700"; COLOR_LIGHT_GOLD = "#F0E68C"; COLOR_DARK_GOLD = "#B8860B"
COLOR_ORANGE = "#FFA500"; COLOR_LIGHT_ORANGE = "#FFDAB9"; COLOR_DARK_ORANGE = "#CD853F"
COLOR_PURPLE = "#8A2BE2"; COLOR_LIGHT_PURPLE = "#D8BFD8"; COLOR_DARK_PURPLE = "#4B0082"
COLOR_GREEN = "#32CD32"; COLOR_LIGHT_GREEN = "#90EE90"; COLOR_DARK_GREEN = "#006400"
COLOR_BLUE = "#00BFFF"; COLOR_LIGHT_BLUE = "#ADD8E6"; COLOR_DARK_BLUE = "#00008B"

# Inspired Palettes
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

# Additional shades for 6-level conversion
COLOR_DARK_RED_DIM = "#600000"
COLOR_MID_DARK_GRAY = "#2A2A2A"
COLOR_VERY_LIGHT_GRAY = "#EEEEEE"
COLOR_VERY_DARK_GRAY = "#1E1E1E"
COLOR_DARK_GOLD_DIM = "#805306"
COLOR_DARK_ORANGE_DIM = "#8B4513" # SaddleBrown
COLOR_DARK_PURPLE_DIM = "#301934" # DarkPurple
COLOR_DARK_GREEN_DIM = "#004d00"
COLOR_DARK_BLUE_DIM = "#000050"


# --- Theme Palettes (Using 6 Levels Conceptually) ---
# Keys map roles:
# L1_bg: Root/Frame BG
# L2_element_dark: Slider BG, Scrollbar BG, Dark Plot Spine (if needed)
# L3_accent_primary: Progress, Active Button, List Selected, Osc Main, Muted/Theme Toggle Text
# L4_hover_bg: Button Hover BG
# L5_accent_secondary: Wave Indicator, Scrollbar Hover, Slider Button Hover
# L6_text_light: Primary Text, Slider Button, Inactive Button Text
# plot_bg, plot_wave_main, plot_spine, plot_text map directly to the plot elements

THEMES = {
    "dark": {
        "L1_bg": COLOR_BLACK, "L2_element_dark": COLOR_MID_DARK_GRAY, "L3_accent_primary": COLOR_DEEP_RED,
        "L4_hover_bg": COLOR_DARK_GRAY, "L5_accent_secondary": COLOR_BRIGHT_RED, "L6_text_light": COLOR_WHITE,
        "slider_button": COLOR_SILVER_L3, # Keep explicit slider button for now
        "plot_bg": COLOR_BLACK, "plot_wave_main": COLOR_WHITE, "plot_osc_main": COLOR_DEEP_RED,
        "plot_wave_indicator": COLOR_BRIGHT_RED, "plot_spine": COLOR_WHITE, "plot_text": COLOR_WHITE,
        "list_scrollbar": COLOR_DARK_GRAY, "list_scrollbar_hover": COLOR_WHITE,
    },
    "light": {
        "L1_bg": COLOR_WHITE, "L2_element_dark": COLOR_LIGHT_GRAY, "L3_accent_primary": COLOR_DEEP_RED,
        "L4_hover_bg": COLOR_VERY_LIGHT_GRAY, # Back to very light gray for white buttons
        "L5_accent_secondary": COLOR_BRIGHT_RED, "L6_text_light": COLOR_BLACK,
        "slider_button": COLOR_BLACK,
        "plot_bg": COLOR_WHITE, "plot_wave_main": COLOR_LIGHT_GRAY, "plot_osc_main": COLOR_DEEP_RED,
        "plot_wave_indicator": COLOR_BRIGHT_RED, "plot_spine": COLOR_BLACK, "plot_text": COLOR_BLACK,
        "list_scrollbar": COLOR_DEEP_RED, "list_scrollbar_hover": COLOR_BLACK,
    },
    "grey": {
        "L1_bg": COLOR_MID_GRAY, "L2_element_dark": COLOR_DARKER_MID_GRAY, "L3_accent_primary": COLOR_DEEP_RED,
        "L4_hover_bg": COLOR_LIGHTER_MID_GRAY, "L5_accent_secondary": COLOR_BRIGHT_RED, "L6_text_light": COLOR_WHITE,
        "slider_button": COLOR_SILVER_L3,
        "plot_bg": COLOR_MID_GRAY, "plot_wave_main": COLOR_SILVER_L3, "plot_osc_main": COLOR_DEEP_RED,
        "plot_wave_indicator": COLOR_BRIGHT_RED, "plot_spine": COLOR_SILVER_L3, "plot_text": COLOR_SILVER_L3,
        "list_scrollbar": COLOR_DEEP_RED, "list_scrollbar_hover": COLOR_WHITE,
    },
     "red": {
        "L1_bg": COLOR_DEEP_RED, "L2_element_dark": COLOR_DARK_RED_DIM, "L3_accent_primary": COLOR_WHITE,
        "L4_hover_bg": COLOR_LIGHT_RED_HOVER, "L5_accent_secondary": COLOR_LIGHT_GRAY, "L6_text_light": COLOR_WHITE,
        "slider_button": COLOR_WHITE,
        "plot_bg": COLOR_DEEP_RED, "plot_wave_main": COLOR_WHITE, "plot_osc_main": COLOR_WHITE,
        "plot_wave_indicator": COLOR_BLACK, "plot_spine": COLOR_WHITE, "plot_text": COLOR_WHITE,
        "list_scrollbar": COLOR_WHITE, "list_scrollbar_hover": COLOR_BLACK,
    },
     "gold": {
        "L1_bg": COLOR_BLACK, "L2_element_dark": COLOR_DARK_GOLD_DIM, "L3_accent_primary": COLOR_GOLD,
        "L4_hover_bg": COLOR_DARK_GOLD, "L5_accent_secondary": COLOR_LIGHT_GOLD, "L6_text_light": COLOR_NEAR_WHITE,
        "slider_button": COLOR_NEAR_WHITE,
        "plot_bg": COLOR_BLACK, "plot_wave_main": COLOR_GOLD, "plot_osc_main": COLOR_LIGHT_GOLD,
        "plot_wave_indicator": COLOR_LIGHT_GOLD, "plot_spine": COLOR_DARK_GOLD, "plot_text": COLOR_NEAR_WHITE,
        "list_scrollbar": COLOR_DARK_GOLD_DIM, "list_scrollbar_hover": COLOR_LIGHT_GOLD,
    },
    "orange": {
        "L1_bg": COLOR_BLACK, "L2_element_dark": COLOR_DARK_ORANGE_DIM, "L3_accent_primary": COLOR_ORANGE,
        "L4_hover_bg": COLOR_DARK_ORANGE, "L5_accent_secondary": COLOR_LIGHT_ORANGE, "L6_text_light": COLOR_NEAR_WHITE,
        "slider_button": COLOR_NEAR_WHITE,
        "plot_bg": COLOR_BLACK, "plot_wave_main": COLOR_ORANGE, "plot_osc_main": COLOR_LIGHT_ORANGE,
        "plot_wave_indicator": COLOR_LIGHT_ORANGE, "plot_spine": COLOR_DARK_ORANGE, "plot_text": COLOR_NEAR_WHITE,
        "list_scrollbar": COLOR_DARK_ORANGE_DIM, "list_scrollbar_hover": COLOR_LIGHT_ORANGE,
    },
    "purple": {
        "L1_bg": COLOR_BLACK, "L2_element_dark": COLOR_DARK_PURPLE_DIM, "L3_accent_primary": COLOR_PURPLE,
        "L4_hover_bg": COLOR_DARK_PURPLE, "L5_accent_secondary": COLOR_LIGHT_PURPLE, "L6_text_light": COLOR_NEAR_WHITE,
        "slider_button": COLOR_NEAR_WHITE,
        "plot_bg": COLOR_BLACK, "plot_wave_main": COLOR_PURPLE, "plot_osc_main": COLOR_LIGHT_PURPLE,
        "plot_wave_indicator": COLOR_LIGHT_PURPLE, "plot_spine": COLOR_DARK_PURPLE, "plot_text": COLOR_NEAR_WHITE,
        "list_scrollbar": COLOR_DARK_PURPLE_DIM, "list_scrollbar_hover": COLOR_LIGHT_PURPLE,
    },
    "green": {
        "L1_bg": COLOR_BLACK, "L2_element_dark": COLOR_DARK_GREEN_DIM, "L3_accent_primary": COLOR_GREEN,
        "L4_hover_bg": COLOR_DARK_GREEN, "L5_accent_secondary": COLOR_LIGHT_GREEN, "L6_text_light": COLOR_NEAR_WHITE,
        "slider_button": COLOR_NEAR_WHITE,
        "plot_bg": COLOR_BLACK, "plot_wave_main": COLOR_GREEN, "plot_osc_main": COLOR_LIGHT_GREEN,
        "plot_wave_indicator": COLOR_LIGHT_GREEN, "plot_spine": COLOR_DARK_GREEN, "plot_text": COLOR_NEAR_WHITE,
        "list_scrollbar": COLOR_DARK_GREEN_DIM, "list_scrollbar_hover": COLOR_LIGHT_GREEN,
    },
    "blue": {
        "L1_bg": COLOR_BLACK, "L2_element_dark": COLOR_DARK_BLUE_DIM, "L3_accent_primary": COLOR_BLUE,
        "L4_hover_bg": COLOR_DARK_BLUE, "L5_accent_secondary": COLOR_LIGHT_BLUE, "L6_text_light": COLOR_NEAR_WHITE,
        "slider_button": COLOR_NEAR_WHITE,
        "plot_bg": COLOR_BLACK, "plot_wave_main": COLOR_BLUE, "plot_osc_main": COLOR_LIGHT_BLUE,
        "plot_wave_indicator": COLOR_LIGHT_BLUE, "plot_spine": COLOR_DARK_BLUE, "plot_text": COLOR_NEAR_WHITE,
        "list_scrollbar": COLOR_DARK_BLUE_DIM, "list_scrollbar_hover": COLOR_LIGHT_BLUE,
    },
    "silver": {
        "L1_bg": COLOR_SILVER_L6, "L2_element_dark": COLOR_SILVER_L5, "L3_accent_primary": COLOR_SILVER_L3,
        "L4_hover_bg": COLOR_SILVER_L4, "L5_accent_secondary": COLOR_SILVER_L2, "L6_text_light": COLOR_SILVER_L1,
        "slider_button": COLOR_SILVER_L1, # Explicit
        "plot_bg": COLOR_SILVER_L6, "plot_wave_main": COLOR_SILVER_L3, "plot_osc_main": COLOR_SILVER_L3,
        "plot_wave_indicator": COLOR_SILVER_L2, "plot_spine": COLOR_SILVER_L5, # Darker spine for contrast
        "plot_text": COLOR_SILVER_L1,
        "list_scrollbar": COLOR_SILVER_L5, "list_scrollbar_hover": COLOR_SILVER_L4,
    },
    "sunset": {
        "L1_bg": COLOR_BLACK, "L2_element_dark": COLOR_SUNSET_L2, "L3_accent_primary": COLOR_SUNSET_L3,
        "L4_hover_bg": COLOR_SUNSET_L4, "L5_accent_secondary": COLOR_SUNSET_L5, "L6_text_light": COLOR_NEAR_WHITE,
        "slider_button": COLOR_NEAR_WHITE, "slider_button_hover": COLOR_SUNSET_L6, # Using L6 for slider hover
        "plot_bg": COLOR_BLACK, "plot_wave_main": COLOR_NEAR_WHITE, "plot_osc_main": COLOR_SUNSET_L3,
        "plot_wave_indicator": COLOR_SUNSET_L5, "plot_spine": COLOR_SUNSET_L2, "plot_text": COLOR_NEAR_WHITE,
        "list_scrollbar": COLOR_SUNSET_L2, "list_scrollbar_hover": COLOR_SUNSET_L5,
    },
    "ocean": {
        "L1_bg": COLOR_BLACK, "L2_element_dark": COLOR_OCEAN_L2, "L3_accent_primary": COLOR_OCEAN_L3,
        "L4_hover_bg": COLOR_OCEAN_L4, "L5_accent_secondary": COLOR_OCEAN_L5, "L6_text_light": COLOR_NEAR_WHITE,
        "slider_button": COLOR_NEAR_WHITE, "slider_button_hover": COLOR_OCEAN_L6, # Using L6 for slider hover
        "plot_bg": COLOR_BLACK, "plot_wave_main": COLOR_NEAR_WHITE, "plot_osc_main": COLOR_OCEAN_L3,
        "plot_wave_indicator": COLOR_OCEAN_L5, "plot_spine": COLOR_OCEAN_L2, "plot_text": COLOR_NEAR_WHITE,
        "list_scrollbar": COLOR_OCEAN_L2, "list_scrollbar_hover": COLOR_OCEAN_L5,
    },
    "ember": {
        "L1_bg": COLOR_BLACK, "L2_element_dark": COLOR_EMBER_L2, "L3_accent_primary": COLOR_EMBER_L3,
        "L4_hover_bg": COLOR_EMBER_L4, "L5_accent_secondary": COLOR_EMBER_L5, "L6_text_light": COLOR_NEAR_WHITE,
        "slider_button": COLOR_NEAR_WHITE, "slider_button_hover": COLOR_EMBER_L6, # Using L6 for slider hover
        "plot_bg": COLOR_BLACK, "plot_wave_main": COLOR_NEAR_WHITE, "plot_osc_main": COLOR_EMBER_L3,
        "plot_wave_indicator": COLOR_EMBER_L5, "plot_spine": COLOR_EMBER_L2, "plot_text": COLOR_NEAR_WHITE,
        "list_scrollbar": COLOR_EMBER_L2, "list_scrollbar_hover": COLOR_EMBER_L5,
    },
    "cyberpunk": {
        "L1_bg": COLOR_CYBERPUNK_L1, "L2_element_dark": COLOR_CYBERPUNK_L2, "L3_accent_primary": COLOR_CYBERPUNK_L3,
        "L4_hover_bg": COLOR_CYBERPUNK_L4, "L5_accent_secondary": COLOR_CYBERPUNK_L5, "L6_text_light": COLOR_NEAR_WHITE,
        "slider_button": COLOR_NEAR_WHITE, "slider_button_hover": COLOR_CYBERPUNK_L6, # Using L6 for slider hover
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

        self.themes = THEMES
        self.theme_cycle = [
             "dark", "light", "grey", "red", "gold", "orange", "silver",
             "purple", "green", "blue", "sunset", "ocean",
             "ember", "cyberpunk"
        ]
        self.current_theme_name = "dark"

        try:
            pygame.mixer.init()
        except pygame.error as e:
            print(f"FATAL: Error initializing pygame mixer: {e}")
            try:
                import tkinter.messagebox
                tkinter.messagebox.showerror("Pygame Error", f"Could not initialize audio output.\nError: {e}\n\nThe application might not play sound.")
            except: pass

        self.current_song = ""
        self.songs_list = []
        self.current_song_index = 0
        self.previous_volume = 0.5
        self.stopped_position = 0.0 # Base time for current playback segment

        self.playing_state = False; self.paused = False; self.shuffle_state = False
        self.loop_state = 0; self.muted = False; self.slider_active = False
        self.waveform_dragging = False; self.is_seeking = False
        self.is_generating_waveform = False; self.is_loading = False; self.has_error = False

        try: pygame.mixer.music.set_volume(self.previous_volume)
        except Exception as e: print(f"Warning: Could not set initial volume: {e}")

        # --- Fonts ---
        self.title_font = ("SF Mono", 16, "bold")
        self.normal_font = ("SF Mono", 11)
        self.button_font = ("SF Mono", 13, "bold")
        self.play_pause_button_font = ("SF Mono", 26, "bold") # Larger font for Play/Pause icon
        # --- End Fonts ---

        self.fig_wave, self.ax_wave = plt.subplots(figsize=(5, 1.5))
        self.mpl_canvas_widget_wave = None
        self.position_indicator_line_wave = None

        self.fig_osc, self.ax_osc = plt.subplots(figsize=(5, 0.8))
        self.mpl_canvas_widget_osc = None
        self.ax_osc.set_ylim(-1.1, 1.1)

        self.waveform_peak_data = None; self.raw_sample_data = None; self.sample_rate = None
        self.waveform_thread = None; self.waveform_abort_flag = threading.Event()

        self.osc_window_seconds = 0.05; self.osc_downsample_factor = 5
        self.song_length = 0.0; self.song_time = 0.0
        self.time_elapsed = "00:00"; self.total_time = "00:00"
        self.update_thread = None; self.thread_running = False
        self.song_title_var = ctk.StringVar(value="NO SONG LOADED")

        # --- UI Elements (declare button here) ---
        self.play_pause_button = None

        # --- Create UI ---
        self.create_frames()
        self.create_player_area()
        self.create_waveform_display()
        self.create_oscilloscope_display()
        self.create_controls()
        self.create_tracklist_area()

        self.apply_theme()

        initial_theme = self.themes[self.current_theme_name]
        initial_spine_color = initial_theme['plot_spine']
        self.draw_initial_placeholder(self.ax_wave, self.fig_wave, initial_spine_color, "LOAD A SONG")
        self.draw_initial_placeholder(self.ax_osc, self.fig_osc, initial_spine_color, "")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _configure_axes(self, ax, fig, spine_color, bg_color):
        fig.patch.set_facecolor(bg_color)
        fig.patch.set_alpha(1.0)
        ax.set_facecolor(bg_color)
        ax.patch.set_alpha(1.0)
        ax.tick_params(axis='both', which='both', length=0, width=0, labelsize=0)
        for spine in ax.spines.values():
            spine.set_color(spine_color)
            spine.set_linewidth(SPINE_LINEWIDTH)
            spine.set_visible(True)
        ax.margins(0); ax.set_yticks([]); ax.set_xticks([])
        try:
            fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
        except Exception as e:
             # print(f"Warning: subplots_adjust failed: {e}") # Be less verbose
             pass

    def create_frames(self):
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
        self.spacer_frame = ctk.CTkFrame(self.visual_frame, height=0)
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
        self.mpl_canvas_widget_wave = FigureCanvasTkAgg(self.fig_wave, master=self.waveform_frame)
        tk_widget = self.mpl_canvas_widget_wave.get_tk_widget()
        tk_widget.pack(fill="both", expand=True)
        self.fig_wave.canvas.mpl_connect('button_press_event', self.on_waveform_press)
        self.fig_wave.canvas.mpl_connect('motion_notify_event', self.on_waveform_motion)
        tk_widget.bind('<ButtonRelease-1>', self.on_waveform_release)
        tk_widget.bind('<Leave>', self.on_waveform_leave)

    def create_oscilloscope_display(self):
        self.mpl_canvas_widget_osc = FigureCanvasTkAgg(self.fig_osc, master=self.oscilloscope_frame)
        tk_widget_osc = self.mpl_canvas_widget_osc.get_tk_widget()
        tk_widget_osc.pack(fill="both", expand=True)

    def draw_initial_placeholder(self, ax, fig, border_color, message="", text_color=None):
        if not ax or not fig or not fig.canvas: return
        try:
            theme = self.themes[self.current_theme_name]
            bg_color = theme['plot_bg']
            if text_color is None: text_color = theme['plot_text']
            ax.clear()
            self._configure_axes(ax, fig, border_color, bg_color)
            font_size = 7 if fig == self.fig_osc else 9
            if message: ax.text(0.5, 0.5, message, ha='center', va='center', fontsize=font_size, color=text_color, transform=ax.transAxes, fontfamily='SF Mono')
            if ax == self.ax_osc: ax.set_ylim(-1.1, 1.1)
            fig.canvas.draw_idle()
            if ax == self.ax_wave: self.position_indicator_line_wave = None
        except Exception as e: print(f"Error drawing placeholder: {e}")

    def create_controls(self):
        self.buttons_frame = ctk.CTkFrame(self.controls_frame, corner_radius=0)
        self.buttons_frame.pack(pady=(5,0), anchor="center")

        # Button size (100% larger than original 35x28)
        # Font here is the *default* for all buttons initially
        button_kwargs = {"font": self.button_font, # Use standard button font for initial creation
                         "border_width": 0,
                         "corner_radius": 0,
                         "width": 70,  # Doubled width
                         "height": 56} # Doubled height

        # --- Buttons (Using updated kwargs) ---
        self.prev_button = ctk.CTkButton(self.buttons_frame, text="◄◄", command=self.previous_song, **button_kwargs)
        self.prev_button.grid(row=0, column=0, padx=4) # Column 0

        self.play_pause_button = ctk.CTkButton(self.buttons_frame, text="▶", command=self.toggle_play_pause, **button_kwargs)
        self.play_pause_button.grid(row=0, column=1, padx=4) # Column 1

        self.next_button = ctk.CTkButton(self.buttons_frame, text="►►", command=self.next_song, **button_kwargs)
        self.next_button.grid(row=0, column=2, padx=4) # Column 2
        # --- End Buttons ---

        # --- Apply larger font specifically to Play/Pause button ---
        if self.play_pause_button and self.play_pause_button.winfo_exists():
            self.play_pause_button.configure(font=self.play_pause_button_font) # Override font
        # --- End Font Override ---

        # --- Rest of the controls ---
        self.extra_frame = ctk.CTkFrame(self.controls_frame, corner_radius=0)
        self.extra_frame.pack(pady=(2,5), anchor="center")
        extra_button_kwargs = {"font": self.normal_font, "border_width": 0, "corner_radius": 0, "width": 65, "height": 25}
        theme_button_kwargs = {"font": self.normal_font, "border_width": 0, "corner_radius": 0, "width": 65, "height": 25}

        self.theme_toggle_button = ctk.CTkButton(self.extra_frame, text="MN-1", command=self.toggle_theme,**theme_button_kwargs)
        self.theme_toggle_button.grid(row=0, column=0, padx=3)
        self.mix_button = ctk.CTkButton(self.extra_frame, text="MIX", command=self.toggle_mix, **extra_button_kwargs)
        self.mix_button.grid(row=0, column=1, padx=3)
        self.loop_button = ctk.CTkButton(self.extra_frame, text="LOOP", command=self.toggle_loop, **extra_button_kwargs)
        self.loop_button.grid(row=0, column=2, padx=3)
        self.volume_button = ctk.CTkButton(self.extra_frame, text="VOL", command=self.toggle_mute, **extra_button_kwargs)
        self.volume_button.grid(row=0, column=3, padx=3)
        self.volume_slider = ctk.CTkSlider(self.extra_frame, from_=0, to=1, number_of_steps=100, command=self.volume_adjust, width=90, height=18);
        self.volume_slider.set(self.previous_volume)
        self.volume_slider.grid(row=0, column=4, padx=(3, 10), pady=(0,3))

    def create_tracklist_area(self):
        self.playlist_label_frame = ctk.CTkFrame(self.right_frame, corner_radius=0)
        self.playlist_label_frame.pack(fill="x", pady=5)
        self.tracklist_label = ctk.CTkLabel(self.playlist_label_frame, text="TRACKLIST", font=self.title_font)
        self.tracklist_label.pack(anchor="center")
        self.playlist_frame = ctk.CTkFrame(self.right_frame, corner_radius=0)
        self.playlist_frame.pack(fill="both", expand=True, padx=5, pady=0)
        self.playlist_scrollable = ctk.CTkScrollableFrame(self.playlist_frame)
        self.playlist_scrollable.pack(fill="both", expand=True)
        self.playlist_entries = []
        self.playlist_buttons_frame = ctk.CTkFrame(self.right_frame, corner_radius=0)
        self.playlist_buttons_frame.pack(fill="x", pady=(5,10))
        playlist_button_kwargs = {"font": self.normal_font, "border_width": 0, "corner_radius": 0, "width": 70, "height": 25}
        self.load_button = ctk.CTkButton(self.playlist_buttons_frame, text="LOAD", command=self.add_songs, **playlist_button_kwargs); self.load_button.pack(side="left", padx=5, expand=True)
        self.remove_button = ctk.CTkButton(self.playlist_buttons_frame, text="REMOVE", command=self.remove_song, **playlist_button_kwargs); self.remove_button.pack(side="left", padx=5, expand=True)
        self.clear_button = ctk.CTkButton(self.playlist_buttons_frame, text="CLEAR", command=self.clear_playlist, **playlist_button_kwargs); self.clear_button.pack(side="left", padx=5, expand=True)

    def toggle_theme(self):
        try:
            current_index = self.theme_cycle.index(self.current_theme_name)
            next_index = (current_index + 1) % len(self.theme_cycle)
            self.current_theme_name = self.theme_cycle[next_index]
        except ValueError:
            self.current_theme_name = self.theme_cycle[0]
        print(f"Switching theme to: {self.current_theme_name}")
        self.apply_theme()

    def apply_theme(self):
        theme = self.themes[self.current_theme_name]
        theme_button_display_text = "MN-1"
        # Define colors based on the 6-level concept for clarity
        bg_col = theme["L1_bg"]
        element_dark_col = theme["L2_element_dark"]
        accent_col = theme["L3_accent_primary"]
        hover_col = theme["L4_hover_bg"] # Use the theme's defined hover color
        accent_light_col = theme["L5_accent_secondary"]
        text_col = theme["L6_text_light"]
        slider_button_col = theme.get("slider_button", text_col)
        slider_button_hover_col = theme.get("slider_button_hover", accent_light_col)
        list_scrollbar_col = theme["list_scrollbar"]
        list_scrollbar_hover_col = theme["list_scrollbar_hover"]
        plot_bg_col = theme["plot_bg"]
        plot_spine_col = theme["plot_spine"]
        plot_text_col = theme["plot_text"]

        try:
            self.root.configure(fg_color=bg_col)

            # Frames
            for frame in [self.player_frame, self.left_frame, self.right_frame,
                          self.controls_frame, self.visual_frame, self.info_frame,
                          self.waveform_frame, self.oscilloscope_frame, self.spacer_frame,
                          self.slider_frame, self.time_frame, self.playlist_label_frame,
                          self.playlist_frame, self.playlist_buttons_frame,
                          self.buttons_frame, self.extra_frame]:
                if frame and frame.winfo_exists(): frame.configure(fg_color=bg_col)

            # Labels
            for label in [self.song_title_label, self.current_time_label,
                           self.total_time_label, self.tracklist_label]:
                 if label and label.winfo_exists():
                     label.configure(fg_color=bg_col, text_color=text_col)

            # --- Button Color Logic ---
            # Default: Button FG matches Frame BG, Text contrasts
            main_button_fg = bg_col
            main_button_text = text_col

            # Override needed only if Button FG should NOT match Frame BG
            # Example: Keeping light theme buttons white
            if self.current_theme_name == "light":
                 main_button_fg = COLOR_WHITE # Explicitly white for light theme buttons
                 main_button_text = COLOR_BLACK # Text must be black
            # --- End Button Color Logic ---


            # Buttons (Main Playback)
            for btn in [self.prev_button, self.play_pause_button, self.next_button]:
                 if btn and btn.winfo_exists():
                     btn.configure(fg_color=main_button_fg, text_color=main_button_text, hover_color=hover_col)
                     # Re-apply correct font (larger one for play/pause)
                     if btn is self.play_pause_button:
                         btn.configure(font=self.play_pause_button_font)
                     else:
                         btn.configure(font=self.button_font)


            # Buttons (Extra Controls & Playlist)
            extra_button_fg = main_button_fg # Use the same FG logic as main buttons
            extra_button_text = main_button_text # Use the same text logic
            extra_buttons = [self.mix_button, self.loop_button, self.volume_button,
                             self.theme_toggle_button,
                             self.load_button, self.remove_button, self.clear_button]
            for btn in extra_buttons:
                 if btn and btn.winfo_exists():
                     # Set background and hover based on calculated colors
                     btn.configure(fg_color=extra_button_fg, hover_color=hover_col)
                     # Set text color - special case for theme toggle
                     if btn is self.theme_toggle_button:
                         # Theme toggle text uses primary accent color regardless of theme
                         btn.configure(text_color=accent_col)
                     else:
                         # Other extra buttons use the calculated text color
                         btn.configure(text_color=extra_button_text)

            if self.theme_toggle_button and self.theme_toggle_button.winfo_exists():
                self.theme_toggle_button.configure(text=theme_button_display_text)

            # Sliders
            if self.song_slider and self.song_slider.winfo_exists():
                self.song_slider.configure(fg_color=element_dark_col, progress_color=accent_col,
                                           button_color=slider_button_col, button_hover_color=slider_button_hover_col)
            if self.volume_slider and self.volume_slider.winfo_exists():
                 self.volume_slider.configure(fg_color=element_dark_col, progress_color=accent_col,
                                              button_color=slider_button_col, button_hover_color=slider_button_hover_col)

            # Scrollable Frame
            if self.playlist_scrollable and self.playlist_scrollable.winfo_exists():
                 self.playlist_scrollable.configure(fg_color=bg_col,
                                                    scrollbar_button_color=list_scrollbar_col,
                                                    scrollbar_button_hover_color=list_scrollbar_hover_col)

            # State-Dependent Colors (Text Colors)
            mute_color = accent_col if self.muted else extra_button_text # Use calculated text color
            mute_text = "MUTED" if self.muted else "VOL"
            if self.volume_button and self.volume_button.winfo_exists():
                 self.volume_button.configure(text_color=mute_color, text=mute_text)

            mix_color = accent_col if self.shuffle_state else extra_button_text # Use calculated text color
            if self.mix_button and self.mix_button.winfo_exists():
                 self.mix_button.configure(text_color=mix_color)

            loop_color = accent_col if self.loop_state > 0 else extra_button_text # Use calculated text color
            loop_text = "LOOP";
            if self.loop_state == 1: loop_text = "LOOP ALL"
            elif self.loop_state == 2: loop_text = "LOOP ONE"
            if self.loop_button and self.loop_button.winfo_exists():
                 self.loop_button.configure(text_color=loop_color, text=loop_text)

            # Tracklist Selection
            selected_idx = -1
            for i, entry in enumerate(self.playlist_entries):
                 if entry and entry.get("frame") and entry["frame"].winfo_exists() and entry.get("selected"):
                    selected_idx = i; break
            if selected_idx != -1:
                 self.select_song(selected_idx) # Re-apply selection colors
            else:
                 for entry in self.playlist_entries:
                    try:
                        if entry and entry.get("label") and entry["label"].winfo_exists():
                             entry["label"].configure(fg_color=bg_col, text_color=text_col)
                        if entry and entry.get("frame") and entry["frame"].winfo_exists():
                            entry["frame"].configure(fg_color=bg_col)
                    except Exception: pass

            # Matplotlib Plots
            if self.ax_wave and self.fig_wave and self.fig_wave.canvas:
                self._configure_axes(self.ax_wave, self.fig_wave, plot_spine_col, plot_bg_col)
                if self.waveform_peak_data is not None:
                     self.draw_static_matplotlib_waveform()
                else:
                     placeholder_msg = self.song_title_var.get() if "ERROR" in self.song_title_var.get() or "FAILED" in self.song_title_var.get() else ("LOAD A SONG" if not self.current_song else "NO WAVEFORM DATA")
                     self.draw_initial_placeholder(self.ax_wave, self.fig_wave, plot_spine_col, placeholder_msg, plot_text_col)

            if self.ax_osc and self.fig_osc and self.fig_osc.canvas:
                 self._configure_axes(self.ax_osc, self.fig_osc, plot_spine_col, plot_bg_col)
                 if self.playing_state and self.raw_sample_data is not None:
                     self.update_oscilloscope()
                 else:
                      self.draw_initial_placeholder(self.ax_osc, self.fig_osc, plot_spine_col, "", plot_text_col)

        except Exception as e:
            print(f"Error applying theme '{self.current_theme_name}': {e}")
            traceback.print_exc()

    def _update_display_title(self, base_title=""):
        prefix = ""
        title = base_title if base_title else os.path.basename(self.current_song) if self.current_song else "NO SONG LOADED"
        if self.has_error: prefix = "[ERROR] "
        elif self.is_loading: prefix = "[LOADING...] "
        elif self.is_generating_waveform: prefix = "[GENERATING...] "
        elif self.playing_state: prefix = "[PLAYING] "
        elif self.paused: prefix = "[PAUSED] "
        elif not self.songs_list and not self.current_song: title = "TRACKLIST EMPTY"
        elif not self.current_song: title = "NO SONG LOADED"

        if self.song_title_label and self.song_title_label.winfo_exists():
             self.song_title_var.set(f"{prefix}{title}")

    def add_songs(self):
        songs = filedialog.askopenfilenames(title="Select Audio Files", filetypes=(("Audio Files", "*.mp3 *.flac"), ("MP3 Files", "*.mp3"), ("FLAC Files", "*.flac"), ("All Files", "*.*")))
        added_count = 0
        if not songs: return
        for song_path in songs:
            if os.path.exists(song_path):
                 try:
                    file_ext = os.path.splitext(song_path)[1].lower()
                    if file_ext == ".mp3": MP3(song_path)
                    elif file_ext == ".flac": FLAC_MUTAGEN(song_path)
                    else: continue
                    song_name = os.path.basename(song_path)
                    if song_path not in self.songs_list:
                        self.add_song_to_playlist(song_name, song_path)
                        self.songs_list.append(song_path); added_count += 1
                    else: print(f"Song already in tracklist: {song_name}")
                 except Exception as e: print(f"Skipping invalid/unreadable file: {os.path.basename(song_path)} - Error: {e}")
            else: print(f"Skipping non-existent file: {song_path}")
        if added_count > 0: print(f"{added_count} TRACK(S) ADDED")
        elif added_count == 0 and songs: print("NO NEW TRACKS ADDED")
        if added_count > 0 and len(self.songs_list) == added_count:
            if self.song_title_var.get() == "TRACKLIST EMPTY": self._update_display_title(base_title="NO SONG LOADED")
            if not self.current_song and not self.playing_state and not self.paused: self.select_song(0)

    def add_song_to_playlist(self, song_name, song_path):
        index = len(self.playlist_entries)
        theme = self.themes[self.current_theme_name]
        list_item_bg = theme["L1_bg"]
        list_item_fg = theme["L6_text_light"]

        song_frame = ctk.CTkFrame(self.playlist_scrollable, fg_color=list_item_bg, corner_radius=0)
        song_frame.pack(fill="x", pady=1, ipady=1)
        song_label = ctk.CTkLabel(song_frame, text=song_name, font=self.normal_font, fg_color=list_item_bg, text_color=list_item_fg, anchor="w", justify="left", cursor="hand2")
        song_label.pack(fill="x", padx=5)
        song_label.bind("<Button-1>", lambda e, idx=index: self.select_song(idx))
        song_label.bind("<Double-Button-1>", lambda e, idx=index: self.play_selected_song_by_index(idx))
        self.playlist_entries.append({"frame": song_frame, "label": song_label, "selected": False, "index": index})

    def select_song(self, index):
        if not (0 <= index < len(self.playlist_entries)): return
        theme = self.themes[self.current_theme_name]
        selected_color = theme["L3_accent_primary"]
        default_fg_color = theme["L6_text_light"]
        bg_color = theme["L1_bg"]
        for i, entry in enumerate(self.playlist_entries):
            is_selected = (i == index)
            text_color = selected_color if is_selected else default_fg_color
            try:
                if entry and entry.get("frame") and entry["frame"].winfo_exists():
                    entry["frame"].configure(fg_color=bg_color)
                if entry and entry.get("label") and entry["label"].winfo_exists():
                    entry["label"].configure(fg_color=bg_color, text_color=text_color)
            except Exception as e:
                if "invalid command name" not in str(e): print(f"Error configuring tracklist entry {i}: {e}")
            if entry: entry["selected"] = is_selected

    def play_selected_song_by_index(self, index):
        if 0 <= index < len(self.songs_list):
             self.abort_waveform_generation()
             self.current_song_index = index
             self.select_song(index)
             self.play_music() # Use play_music to start from beginning
        else: print(f"Warning: play_selected_song_by_index index {index} out of range.");

    def play_selected_song(self, event=None):
        selected_index = -1
        for index, entry in enumerate(self.playlist_entries):
            if entry and entry.get("frame") and entry["frame"].winfo_exists() and entry.get("selected"):
                selected_index = index; break
        if selected_index != -1: self.play_selected_song_by_index(selected_index)
        elif self.playlist_entries: self.play_selected_song_by_index(0)
        else: self._update_display_title()

    def remove_song(self):
        removed_index = -1; is_current_song_removed = False
        for i, entry in enumerate(self.playlist_entries):
             if entry and entry.get("frame") and entry["frame"].winfo_exists() and entry.get("selected"):
                removed_index = i; break
        if removed_index == -1: print("NO TRACK SELECTED"); return
        current_song_path = self.songs_list[removed_index] if removed_index < len(self.songs_list) else None
        if current_song_path and removed_index == self.current_song_index and self.current_song == current_song_path:
             is_current_song_removed = True
        if removed_index < len(self.playlist_entries):
             try:
                 if self.playlist_entries[removed_index]["frame"].winfo_exists(): self.playlist_entries[removed_index]["frame"].destroy()
             except Exception: pass
             self.playlist_entries.pop(removed_index)
        if removed_index < len(self.songs_list):
            removed_song_path = self.songs_list.pop(removed_index); print(f"Removed: {os.path.basename(removed_song_path)}")
        else: print("Warning: Index mismatch during remove."); return
        for i in range(removed_index, len(self.playlist_entries)):
            entry = self.playlist_entries[i]
            if entry:
                entry["index"] = i
                try:
                    if entry.get("label") and entry["label"].winfo_exists():
                        entry["label"].unbind("<Button-1>"); entry["label"].unbind("<Double-Button-1>")
                        entry["label"].bind("<Button-1>", lambda e, idx=i: self.select_song(idx))
                        entry["label"].bind("<Double-Button-1>", lambda e, idx=i: self.play_selected_song_by_index(idx))
                except Exception as e: print(f"Error re-binding tracklist entry {i}: {e}")
        if is_current_song_removed:
            self.stop(); self.current_song = ""; self.has_error = False; self.is_loading = False; self.is_generating_waveform = False;
            self._update_display_title(base_title="NO SONG LOADED")
            # Reset play button text
            if self.play_pause_button and self.play_pause_button.winfo_exists():
                self.play_pause_button.configure(text="▶")
            theme = self.themes[self.current_theme_name]; spine_color = theme['plot_spine']
            self.draw_initial_placeholder(self.ax_wave, self.fig_wave, spine_color, "TRACK REMOVED")
            self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color, "")
            self.raw_sample_data = None; self.waveform_peak_data = None; self.sample_rate = None; self.song_length = 0;
            if self.total_time_label and self.total_time_label.winfo_exists(): self.total_time_label.configure(text="00:00");
            if self.current_time_label and self.current_time_label.winfo_exists(): self.current_time_label.configure(text="00:00");
            if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.set(0); self.song_slider.configure(to=100)
        if len(self.songs_list) == 0:
            self.current_song_index = 0
            if not is_current_song_removed:
                 self.current_song = ""; self.has_error = False; self.is_loading = False; self.is_generating_waveform = False;
                 self._update_display_title(base_title="TRACKLIST EMPTY")
                 # Reset play button text
                 if self.play_pause_button and self.play_pause_button.winfo_exists():
                     self.play_pause_button.configure(text="▶")
                 theme = self.themes[self.current_theme_name]; spine_color = theme['plot_spine']
                 self.draw_initial_placeholder(self.ax_wave, self.fig_wave, spine_color, "TRACKLIST EMPTY")
                 self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color, "")
                 self.raw_sample_data = None; self.waveform_peak_data = None; self.sample_rate = None; self.song_length = 0;
                 if self.total_time_label and self.total_time_label.winfo_exists(): self.total_time_label.configure(text="00:00");
                 if self.current_time_label and self.current_time_label.winfo_exists(): self.current_time_label.configure(text="00:00");
                 if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.set(0); self.song_slider.configure(to=100)
        elif removed_index < self.current_song_index: self.current_song_index -= 1
        elif removed_index == self.current_song_index and not is_current_song_removed: self.current_song_index = min(removed_index, len(self.songs_list) - 1)
        if not is_current_song_removed and self.songs_list:
            new_index_to_select = min(self.current_song_index, len(self.playlist_entries) - 1)
            if new_index_to_select >= 0: self.select_song(new_index_to_select)

    def clear_playlist(self):
        self.stop();
        for entry in self.playlist_entries:
            try:
                 if entry and entry.get("frame") and entry["frame"].winfo_exists(): entry["frame"].destroy()
            except Exception: pass
        self.playlist_entries.clear(); self.songs_list.clear(); self.current_song_index = 0; self.current_song = ""
        self.has_error = False; self.is_loading = False; self.is_generating_waveform = False;
        self._update_display_title(base_title="TRACKLIST CLEARED")
        # Reset play button text
        if self.play_pause_button and self.play_pause_button.winfo_exists():
            self.play_pause_button.configure(text="▶")
        self.waveform_peak_data = None; self.raw_sample_data = None; self.sample_rate = None
        theme = self.themes[self.current_theme_name]; spine_color = theme['plot_spine']
        self.draw_initial_placeholder(self.ax_wave, self.fig_wave, spine_color, "TRACKLIST CLEARED")
        self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color, "")
        if self.total_time_label and self.total_time_label.winfo_exists(): self.total_time_label.configure(text="00:00");
        if self.current_time_label and self.current_time_label.winfo_exists(): self.current_time_label.configure(text="00:00");
        if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.set(0); self.song_slider.configure(to=100)
        self.song_length = 0; self._update_display_title(base_title="TRACKLIST EMPTY")

    def toggle_play_pause(self):
        """Handles the combined Play/Pause button action."""
        if not self.songs_list:
            self._update_display_title(base_title="TRACKLIST EMPTY")
            if self.play_pause_button and self.play_pause_button.winfo_exists():
                self.play_pause_button.configure(text="▶")
            return

        self.has_error = False
        theme = self.themes[self.current_theme_name]
        active_button_color = theme["L4_hover_bg"]
        # Determine default button background color based on theme
        default_button_color = COLOR_WHITE if self.current_theme_name == "light" else theme["L1_bg"]
        spine_color = theme['plot_spine']

        # --- Visual Feedback ---
        if self.play_pause_button and self.play_pause_button.winfo_exists():
            self.play_pause_button.configure(fg_color=active_button_color)
            self.root.after(100, lambda: self.play_pause_button.configure(fg_color=default_button_color) if self.play_pause_button and self.play_pause_button.winfo_exists() else None)

        # --- Logic ---
        if self.playing_state: # --- PAUSE ---
            if not self.paused: # Ensure we only pause if actually playing
                try:
                    current_pos_ms = 0
                    if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                        current_pos_ms = pygame.mixer.music.get_pos()
                        if current_pos_ms != -1:
                            time_since_last_play_sec = current_pos_ms / 1000.0
                            # Update stopped_position based on current play time + previous base time
                            self.stopped_position = self.stopped_position + time_since_last_play_sec
                            self.song_time = self.stopped_position # Update current time as well
                    pygame.mixer.music.pause()
                    self.paused = True; self.playing_state = False
                    self.thread_running = False # Stop updates
                    if self.play_pause_button and self.play_pause_button.winfo_exists():
                        self.play_pause_button.configure(text="▶") # Show Play symbol
                    self._update_display_title()
                    print(f"Playback Paused at {self.stopped_position:.2f}s (Raw mixer pos: {current_pos_ms}ms)")
                except pygame.error as e:
                    print(f"Pygame error during pause: {e}")
                    self.has_error = True; self._update_display_title()

        elif self.paused: # --- UNPAUSE ---
             try:
                 pygame.mixer.music.unpause()
                 self.paused = False; self.playing_state = True
                 # stopped_position remains the same, playback continues from there
                 if self.play_pause_button and self.play_pause_button.winfo_exists():
                     self.play_pause_button.configure(text="II") # Show Pause symbol
                 self._update_display_title(); self.start_update_thread()
                 print(f"Resumed playback from {self.stopped_position:.2f}s")
             except pygame.error as e:
                 print(f"Pygame error during unpause: {e}")
                 self.has_error = True; self._update_display_title()

        else: # --- PLAY (From stopped state or new song) ---
            song_to_play_index = -1; selected_idx = -1; is_resuming = False
            # Find selected song in list
            for i, entry in enumerate(self.playlist_entries):
                 if entry and entry.get("frame") and entry["frame"].winfo_exists() and entry.get("selected"):
                    selected_idx = i; break

            # Determine which song and if resuming
            if selected_idx != -1 and 0 <= selected_idx < len(self.songs_list):
                song_to_play_index = selected_idx
                # Check if we are resuming the *same* selected song
                is_resuming = (song_to_play_index == self.current_song_index and self.stopped_position > 0 and self.current_song == self.songs_list[song_to_play_index])
            elif self.current_song and self.stopped_position > 0 and 0 <= self.current_song_index < len(self.songs_list) and self.songs_list[self.current_song_index] == self.current_song:
                # If no selection, resume the previously stopped song if possible
                song_to_play_index = self.current_song_index; is_resuming = True
            elif self.songs_list:
                 # Fallback: Use selected index if valid, else current index, else first song
                 current_selected_index = -1
                 for i, entry in enumerate(self.playlist_entries):
                     if entry and entry.get("frame") and entry["frame"].winfo_exists() and entry.get("selected"):
                         current_selected_index = i; break
                 if 0 <= current_selected_index < len(self.songs_list):
                      song_to_play_index = current_selected_index
                 elif 0 <= self.current_song_index < len(self.songs_list):
                     song_to_play_index = self.current_song_index
                 else:
                     song_to_play_index = 0
                 # Check if this determined song is the one we stopped
                 is_resuming = (song_to_play_index == self.current_song_index and self.stopped_position > 0 and self.current_song == self.songs_list[song_to_play_index])

            if song_to_play_index != -1:
                new_song_path = self.songs_list[song_to_play_index]
                song_changed = (new_song_path != self.current_song)

                self.current_song_index = song_to_play_index
                self.current_song = new_song_path
                self.select_song(self.current_song_index) # Highlight song

                try:
                    self.is_loading = True; self._update_display_title()

                    if song_changed or not is_resuming: # Load if song changed OR not resuming
                         self.abort_waveform_generation()
                         self.update_song_info() # Get length etc.
                         self.draw_initial_placeholder(self.ax_wave, self.fig_wave, spine_color, "LOADING...")
                         self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color, "")
                         pygame.mixer.music.load(self.current_song)
                         start_pos = 0.0
                         self.stopped_position = 0.0 # Reset base time for new song/play
                         self.song_time = 0.0        # Reset current time
                         print(f"Starting new playback: {os.path.basename(self.current_song)}")
                    else: # Resuming the same song
                         start_pos = self.stopped_position # Use the recorded pause time
                         print(f"Resuming stopped playback: {os.path.basename(self.current_song)} at {start_pos:.2f}s")
                         # No need to reload, stopped_position is already set

                    # Play from the determined start position
                    pygame.mixer.music.play(start=start_pos)

                    self.playing_state = True; self.paused = False; self.is_loading = False
                    if self.play_pause_button and self.play_pause_button.winfo_exists():
                        self.play_pause_button.configure(text="II") # Show Pause symbol
                    self._update_display_title(); self.start_update_thread()
                    if song_changed or not is_resuming: # Generate waveform only if new
                        self.trigger_waveform_generation()

                except pygame.error as e:
                    print(f"Pygame Error: {e}"); self.has_error = True; self.is_loading = False; self._update_display_title(base_title=f"{os.path.basename(self.current_song)}"); self.playing_state = False; self.paused = False; self.current_song = ""
                    if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="▶") # Reset button
                except Exception as e:
                    print(f"Error: {e}"); traceback.print_exc(); self.has_error = True; self.is_loading = False; self._update_display_title(base_title=f"{os.path.basename(self.current_song)}"); self.playing_state = False; self.paused = False; self.current_song = ""
                    if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="▶") # Reset button
            else:
                 self._update_display_title(base_title="TRACKLIST EMPTY?")
                 if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="▶")


    def play_music(self):
        """Core function to load and play a song from the beginning. Called internally."""
        if not self.songs_list or not (0 <= self.current_song_index < len(self.songs_list)):
            self._update_display_title(base_title="INVALID SELECTION")
            if self.play_pause_button and self.play_pause_button.winfo_exists():
                self.play_pause_button.configure(text="▶")
            return
        self.has_error = False; self.current_song = self.songs_list[self.current_song_index]
        self.stopped_position = 0.0; self.song_time = 0.0 # Always start from 0
        theme = self.themes[self.current_theme_name]; spine_color = theme['plot_spine']
        try:
            self.abort_waveform_generation(); print(f"play_music: Loading {os.path.basename(self.current_song)}")
            self.is_loading = True; self._update_display_title()
            pygame.mixer.music.stop(); pygame.mixer.music.load(self.current_song)
            self.update_song_info(); pygame.mixer.music.play() # Play from start
            self.playing_state = True; self.paused = False; self.is_loading = False
            # Update button text to Pause
            if self.play_pause_button and self.play_pause_button.winfo_exists():
                 self.play_pause_button.configure(text="II")
            self.select_song(self.current_song_index); self._update_display_title()
            if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.set(0)
            if self.current_time_label and self.current_time_label.winfo_exists(): self.current_time_label.configure(text="00:00")
            self.draw_initial_placeholder(self.ax_wave, self.fig_wave, spine_color,"GENERATING...")
            self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color,"")
            self.trigger_waveform_generation(); self.start_update_thread()
        except pygame.error as e:
             print(f"Pygame Error: {e}"); self.has_error = True; self.is_loading = False; self._update_display_title(base_title=f"{os.path.basename(self.current_song)}"); self.playing_state = False; self.paused = False; self.current_song = "";
             if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="▶"); # Reset button
             self.draw_initial_placeholder(self.ax_wave, self.fig_wave, spine_color,"LOAD ERROR"); self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color,"")
        except Exception as e:
             print(f"Error: {e}"); traceback.print_exc(); self.has_error = True; self.is_loading = False; self._update_display_title(base_title=f"{os.path.basename(self.current_song)}"); self.playing_state = False; self.paused = False; self.current_song = "";
             if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="▶"); # Reset button
             self.draw_initial_placeholder(self.ax_wave, self.fig_wave, spine_color,"ERROR"); self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color,"")


    def stop(self):
        if self.playing_state or self.paused:
            final_pos = 0.0
            try:
                # If paused, the correct position is already stored in stopped_position
                if self.paused:
                    final_pos = self.stopped_position
                # If playing, calculate current absolute time
                elif self.playing_state and pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                    current_pos_ms = pygame.mixer.music.get_pos()
                    if current_pos_ms != -1:
                        final_pos = self.stopped_position + (current_pos_ms / 1000.0)
                    else: # Fallback if get_pos fails while playing
                        final_pos = self.song_time
                else: # Fallback if state is inconsistent
                    final_pos = self.song_time

                print(f"Stop called, final calculated pos: {final_pos:.2f}s")
                pygame.mixer.music.stop()
            except pygame.error as e: print(f"Pygame error during stop: {e}")
            finally:
                was_playing_or_paused = self.playing_state or self.paused
                self.playing_state = False; self.paused = False
                # Store the final calculated position as the new stopped_position
                self.stopped_position = np.clip(final_pos, 0.0, self.song_length if self.song_length > 0 else final_pos + 1.0)
                self.song_time = self.stopped_position # Sync song_time
                self._update_display_title(); self.thread_running = False
                # Update button text to Play
                if self.play_pause_button and self.play_pause_button.winfo_exists():
                    self.play_pause_button.configure(text="▶")

                if was_playing_or_paused:
                    slider_val = self.stopped_position
                    if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.set(slider_val)
                    if self.current_time_label and self.current_time_label.winfo_exists():
                         mins, secs = divmod(int(self.stopped_position), 60); self.current_time_label.configure(text=f"{mins:02d}:{secs:02d}")
                    theme = self.themes[self.current_theme_name]; spine_color = theme['plot_spine']
                    pos_ratio = np.clip(self.stopped_position / self.song_length, 0.0, 1.0) if self.song_length > 0 else 0.0
                    self.draw_waveform_position_indicator(pos_ratio)
                    if self.fig_wave and self.fig_wave.canvas: self.fig_wave.canvas.draw_idle()
                    self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color,"")
                    print(f"Stopped. Recorded pos: {self.stopped_position:.2f}s")
        else: # Already stopped
            self.thread_running = False
            self._update_display_title()
            # Ensure button shows Play if already stopped
            if self.play_pause_button and self.play_pause_button.winfo_exists():
                 self.play_pause_button.configure(text="▶")


    def previous_song(self):
        if not self.songs_list: self._update_display_title(base_title="TRACKLIST EMPTY"); return
        original_index = self.current_song_index; self.stop()
        if len(self.songs_list) > 0:
            self.current_song_index = (original_index - 1 + len(self.songs_list)) % len(self.songs_list)
            self.play_music()

    def next_song(self, auto_advance=False):
        if not self.songs_list: self._update_display_title(base_title="TRACKLIST EMPTY"); return
        original_index = self.current_song_index
        if not auto_advance: self.stop()
        else: # Auto-advance just resets state, doesn't call stop()
            self.playing_state = False; self.paused = False; self.thread_running = False
            self.abort_waveform_generation(); self.stopped_position = 0.0; self.song_time = 0.0
            # Let play_music set the button text
            print("Auto-advancing to next song.")
        if len(self.songs_list) > 0:
             self.current_song_index = (original_index + 1) % len(self.songs_list)
             self.play_music()

    def volume_adjust(self, value):
        volume = float(value)
        try: pygame.mixer.music.set_volume(volume)
        except Exception as e: print(f"Warning: Could not set volume: {e}"); return
        theme = self.themes[self.current_theme_name]
        # Determine base text color for 'VOL' based on current theme
        base_text_col = COLOR_BLACK if self.current_theme_name == "light" else theme["L6_text_light"]
        accent_col = theme["L3_accent_primary"]
        if volume > 0 and self.muted:
             self.muted = False
             if self.volume_button and self.volume_button.winfo_exists(): self.volume_button.configure(text="VOL", text_color=base_text_col)
        elif volume == 0 and not self.muted:
             self.muted = True
             if self.volume_button and self.volume_button.winfo_exists(): self.volume_button.configure(text="MUTED", text_color=accent_col)
        if volume > 0: self.previous_volume = volume

    def toggle_mute(self):
        theme = self.themes[self.current_theme_name]
        # Determine base text color for 'VOL' based on current theme
        base_text_col = COLOR_BLACK if self.current_theme_name == "light" else theme["L6_text_light"]
        accent_col = theme["L3_accent_primary"]
        if self.muted: # Unmute
             try:
                 pygame.mixer.music.set_volume(self.previous_volume)
                 if self.volume_slider and self.volume_slider.winfo_exists(): self.volume_slider.set(self.previous_volume)
                 self.muted = False
                 if self.volume_button and self.volume_button.winfo_exists(): self.volume_button.configure(text="VOL", text_color=base_text_col)
             except Exception as e: print(f"Warning: Could not set volume on unmute: {e}")
        else: # Mute
             try:
                 current_vol = pygame.mixer.music.get_volume()
                 if current_vol > 0: self.previous_volume = current_vol
                 pygame.mixer.music.set_volume(0)
                 if self.volume_slider and self.volume_slider.winfo_exists(): self.volume_slider.set(0)
                 self.muted = True
                 if self.volume_button and self.volume_button.winfo_exists(): self.volume_button.configure(text="MUTED", text_color=accent_col)
             except Exception as e: print(f"Warning: Could not set volume on mute: {e}")

    def toggle_mix(self):
        self.shuffle_state = not self.shuffle_state; print(f"Mix toggled: {'ON' if self.shuffle_state else 'OFF'}")
        theme = self.themes[self.current_theme_name]
        # Determine base text color based on current theme
        base_text_col = COLOR_BLACK if self.current_theme_name == "light" else theme["L6_text_light"]
        accent_col = theme["L3_accent_primary"]
        color = accent_col if self.shuffle_state else base_text_col
        if self.mix_button and self.mix_button.winfo_exists(): self.mix_button.configure(text_color=color)

    def toggle_loop(self):
        self.loop_state = (self.loop_state + 1) % 3
        theme = self.themes[self.current_theme_name]
        # Determine base text color based on current theme
        base_text_col = COLOR_BLACK if self.current_theme_name == "light" else theme["L6_text_light"]
        accent_col = theme["L3_accent_primary"]
        color = accent_col if self.loop_state > 0 else base_text_col
        loop_text = "LOOP";
        if self.loop_state == 1: loop_text = "LOOP ALL"
        elif self.loop_state == 2: loop_text = "LOOP ONE"
        if self.loop_button and self.loop_button.winfo_exists(): self.loop_button.configure(text_color=color, text=loop_text)
        print(f"Loop toggled: {loop_text}")

    def slider_start_scroll(self, event):
        if self.current_song and self.song_length > 0: self.slider_active = True
        else: self.slider_active = False

    def slider_stop_scroll(self, event):
        if not self.slider_active: return
        position = 0.0
        if self.song_slider and self.song_slider.winfo_exists(): position = float(self.song_slider.get())
        else: self.slider_active = False; return
        self.slider_active = False
        print(f"Slider release - Seeking to: {position:.2f}s"); self.seek_song(position)

    def slide_song(self, value):
        if not self.slider_active: return
        position = float(value)
        mins, secs = divmod(int(position), 60); time_str = f"{mins:02d}:{secs:02d}"
        if self.current_time_label and self.current_time_label.winfo_exists(): self.current_time_label.configure(text=time_str)
        pos_ratio = np.clip(position / self.song_length, 0.0, 1.0) if self.song_length > 0 else 0.0
        self.draw_waveform_position_indicator(pos_ratio)
        if self.fig_wave and self.fig_wave.canvas: self.fig_wave.canvas.draw_idle()

    def on_waveform_press(self, event):
        if (event.inaxes != self.ax_wave or self.waveform_peak_data is None or self.song_length <= 0):
            self.waveform_dragging = False; return
        self.waveform_dragging = True; self.slider_active = True
        self._update_position_from_waveform_event(event)

    def on_waveform_motion(self, event):
        if not self.waveform_dragging or event.inaxes != self.ax_wave: return
        self._update_position_from_waveform_event(event)

    def on_waveform_release(self, event):
        if not self.waveform_dragging: return
        target_time = 0.0
        if self.song_slider and self.song_slider.winfo_exists(): target_time = float(self.song_slider.get())
        else: self.waveform_dragging = False; self.slider_active = False; return
        self.waveform_dragging = False; self.slider_active = False
        print(f"Waveform release - Seeking to: {target_time:.2f}s"); self.seek_song(target_time)

    def on_waveform_leave(self, event):
        if self.waveform_dragging: print("Waveform leave while dragging - treating as release"); self.on_waveform_release(event)

    def _update_position_from_waveform_event(self, event):
        if self.waveform_peak_data is None or self.song_length <= 0 or event.xdata is None: return
        num_points = len(self.waveform_peak_data); x_coord = event.xdata
        x_max = (num_points - 1) if num_points > 1 else 1
        position_ratio = np.clip(x_coord / x_max, 0.0, 1.0) if x_max > 0 else 0.0
        target_time = position_ratio * self.song_length
        if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.set(target_time)
        if self.current_time_label and self.current_time_label.winfo_exists():
             mins, secs = divmod(int(target_time), 60); self.current_time_label.configure(text=f"{mins:02d}:{secs:02d}")
        self.draw_waveform_position_indicator(position_ratio)
        if self.fig_wave and self.fig_wave.canvas: self.fig_wave.canvas.draw_idle()

    def seek_song(self, position_seconds):
        if self.current_song and self.song_length > 0 and pygame.mixer.get_init():
            self.is_seeking = True
            try:
                self.has_error = False
                # Prevent seeking exactly to the end, pygame might have issues
                seek_pos = np.clip(position_seconds, 0.0, self.song_length - 0.1 if self.song_length > 0.1 else 0.0)
                print(f"Seeking to: {seek_pos:.2f}s (requested: {position_seconds:.2f}s)")

                self.stopped_position = seek_pos # THIS IS THE CRUCIAL UPDATE: Base time becomes seek target
                self.song_time = seek_pos       # Current time also becomes seek target

                if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.set(seek_pos)
                if self.current_time_label and self.current_time_label.winfo_exists():
                    mins, secs = divmod(int(seek_pos), 60); self.current_time_label.configure(text=f"{mins:02d}:{secs:02d}")
                pos_ratio = np.clip(seek_pos / self.song_length, 0.0, 1.0) if self.song_length > 0 else 0.0
                self.draw_waveform_position_indicator(pos_ratio)
                if self.fig_wave and self.fig_wave.canvas: self.fig_wave.canvas.draw_idle()
                if self.raw_sample_data is not None: self.update_oscilloscope() # Update scope immediately

                try:
                    if self.playing_state or self.paused:
                        was_paused = self.paused
                        # Play always restarts the timer from 0, seek is handled by start=
                        pygame.mixer.music.play(start=seek_pos)
                        if was_paused:
                            pygame.mixer.music.pause()
                            self.playing_state = False; self.paused = True
                            if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="▶") # Show Play
                        else:
                            self.playing_state = True; self.paused = False
                            if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="II") # Show Pause
                            self.start_update_thread()
                        self._update_display_title()
                    else: # Player was completely stopped
                         self._update_display_title()
                         if self.play_pause_button and self.play_pause_button.winfo_exists(): self.play_pause_button.configure(text="▶") # Show Play
                         print(f"Player stopped, updated next start pos to {seek_pos:.2f}s")
                except pygame.error as e: print(f"Pygame error on seek: {e}"); self.has_error = True; self._update_display_title()
                except Exception as e: print(f"General error on seek: {e}"); traceback.print_exc(); self.has_error = True; self._update_display_title()
            finally:
                self.root.after(50, self._clear_seeking_flag) # Delayed clearing
        else: print("Seek ignored: No song, zero length, or mixer not initialized.")


    def _clear_seeking_flag(self):
        self.is_seeking = False

    def update_song_info(self):
        if not self.current_song:
            self._update_display_title(base_title="NO SONG LOADED");
            if self.total_time_label and self.total_time_label.winfo_exists(): self.total_time_label.configure(text="00:00");
            if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.configure(to=100, number_of_steps=100); self.song_slider.set(0);
            self.song_length = 0.0; return
        song_name = os.path.basename(self.current_song)
        try:
            file_extension = os.path.splitext(self.current_song)[1].lower()
            audio = None
            if file_extension == '.mp3': audio = MP3(self.current_song)
            elif file_extension == '.flac': audio = FLAC_MUTAGEN(self.current_song)
            if audio and hasattr(audio, 'info') and hasattr(audio.info, 'length'):
                self.song_length = audio.info.length
                if not isinstance(self.song_length, (int, float)) or self.song_length <= 0: self.song_length = 0.0
                mins, secs = divmod(int(self.song_length), 60); self.total_time = f"{mins:02d}:{secs:02d}"
                if self.total_time_label and self.total_time_label.winfo_exists(): self.total_time_label.configure(text=self.total_time)
                slider_max = max(1.0, self.song_length); num_steps = max(100, int(slider_max * 10)) # Increased steps for finer control
                if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.configure(to=slider_max, number_of_steps=num_steps)
                # Only reset UI time/slider if we are truly at the beginning (stopped_position is 0)
                if self.stopped_position == 0 and not self.playing_state and not self.paused:
                    if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.set(0)
                    if self.current_time_label and self.current_time_label.winfo_exists(): self.current_time_label.configure(text="00:00")
            else: raise ValueError(f"Mutagen could not read info/length for {song_name}")
        except Exception as e:
            print(f"Error getting song info: {e}"); self.has_error = True; self._update_display_title(base_title=song_name); self.song_length = 0.0; self.total_time = "00:00";
            if self.total_time_label and self.total_time_label.winfo_exists(): self.total_time_label.configure(text=self.total_time);
            if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.configure(to=100, number_of_steps=100); self.song_slider.set(0);
            if self.current_time_label and self.current_time_label.winfo_exists(): self.current_time_label.configure(text="00:00")

    def trigger_waveform_generation(self):
        if self.waveform_thread and self.waveform_thread.is_alive():
            self.abort_waveform_generation(); time.sleep(0.05)
        if not self.current_song: return
        self.waveform_peak_data = None; self.raw_sample_data = None; self.sample_rate = None
        self.is_generating_waveform = True; self.has_error = False
        self._update_display_title()
        theme = self.themes[self.current_theme_name]; spine_color = theme['plot_spine']
        self.draw_initial_placeholder(self.ax_wave, self.fig_wave, spine_color,"GENERATING...")
        self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color,"")
        self.waveform_abort_flag.clear()
        self.waveform_thread = threading.Thread(target=self.generate_waveform_data_background, args=(self.current_song, self.waveform_abort_flag), daemon=True)
        self.waveform_thread.start()

    def generate_waveform_data_background(self, song_path, abort_flag):
        local_peak_data = None; local_raw_data = None; effective_sample_rate = None; error_message = None
        try:
            start_time = time.monotonic()
            if abort_flag.is_set(): return
            if not os.path.exists(song_path): raise FileNotFoundError(f"Audio file not found: {song_path}")
            try: sound = AudioSegment.from_file(song_path)
            except FileNotFoundError as fnf_err:
                if "ffmpeg" in str(fnf_err).lower() or "ffprobe" in str(fnf_err).lower(): raise ImportError("FFmpeg/FFprobe not found.")
                else: raise
            except Exception as load_err: raise RuntimeError(f"Pydub load failed: {load_err}")
            if abort_flag.is_set(): return
            original_sample_rate = sound.frame_rate
            bit_depth = sound.sample_width * 8 if sound.sample_width > 0 else 16
            calculated_max_val = sound.max_possible_amplitude if hasattr(sound, 'max_possible_amplitude') else 2**(bit_depth - 1)
            samples_array = np.array(sound.get_array_of_samples())
            if samples_array.size == 0: raise ValueError("Audio file contains no samples.")
            if sound.channels == 2: mono_samples = samples_array.astype(np.float64).reshape((-1, 2)).mean(axis=1)
            else: mono_samples = samples_array.astype(np.float64)
            if not np.any(mono_samples): print(f"Warning: Audio file {os.path.basename(song_path)} appears to be silent.")
            mono_samples_normalized = np.clip(mono_samples / calculated_max_val, -1.0, 1.0) if calculated_max_val != 0 else mono_samples
            if abort_flag.is_set(): return
            if self.osc_downsample_factor > 1:
                 local_raw_data = mono_samples_normalized[::self.osc_downsample_factor]
                 effective_sample_rate = original_sample_rate / self.osc_downsample_factor
            else: local_raw_data = mono_samples_normalized; effective_sample_rate = original_sample_rate
            if abort_flag.is_set(): return
            target_points = 500
            if len(mono_samples_normalized) > 0:
                chunk_size = max(1, len(mono_samples_normalized) // target_points); processed_peaks = []
                num_chunks = (len(mono_samples_normalized) + chunk_size - 1) // chunk_size
                for i in range(num_chunks):
                     if i % 50 == 0 and abort_flag.is_set(): return
                     start = i * chunk_size; end = min((i + 1) * chunk_size, len(mono_samples_normalized))
                     chunk = mono_samples_normalized[start:end]
                     peak = np.max(np.abs(chunk)) if len(chunk) > 0 else 0.0; processed_peaks.append(peak)
                local_peak_data = np.array(processed_peaks)
            else: local_peak_data = np.array([])
            print(f"BG_THREAD: Waveform gen finished: {os.path.basename(song_path)} in {time.monotonic() - start_time:.2f}s")
        except ImportError as e: error_message = f"WAVEFORM ERROR\n({e})"
        except FileNotFoundError as e: error_message = f"WAVEFORM ERROR\nFile Not Found"
        except MemoryError: error_message = "WAVEFORM ERROR\nMemory Error"
        except Exception as e: print(f"BG_THREAD: Error generating waveform:"); traceback.print_exc(); error_message = f"WAVEFORM ERROR\n({type(e).__name__})"
        finally:
            if not abort_flag.is_set():
                if self.root.winfo_exists(): self.root.after(1, self.process_waveform_result, song_path, local_peak_data, local_raw_data, effective_sample_rate, error_message)
            else: print(f"BG_THREAD: Waveform generation aborted, result not processed.")

    def process_waveform_result(self, song_path, peak_data, raw_data, sample_rate, error_message):
        if song_path != self.current_song: print(f"Ignoring stale waveform result for: {os.path.basename(song_path)}"); return
        self.is_generating_waveform = False
        theme = self.themes[self.current_theme_name]; spine_color = theme['plot_spine']
        if error_message:
            self.waveform_peak_data = None; self.raw_sample_data = None; self.sample_rate = None; self.has_error = True
            self._update_display_title(base_title=os.path.basename(song_path))
            self.draw_initial_placeholder(self.ax_wave, self.fig_wave, spine_color, error_message)
            self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color, "")
        elif peak_data is not None and raw_data is not None and sample_rate is not None:
            self.waveform_peak_data = peak_data; self.raw_sample_data = raw_data; self.sample_rate = sample_rate; self.has_error = False
            self._update_display_title(); self.draw_static_matplotlib_waveform(); self.update_song_position()
        else:
             self.waveform_peak_data = None; self.raw_sample_data = None; self.sample_rate = None; self.has_error = True
             self._update_display_title(base_title=os.path.basename(song_path))
             self.draw_initial_placeholder(self.ax_wave, self.fig_wave, spine_color,"GEN FAILED (Internal)")
             self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color,"")

    def draw_static_matplotlib_waveform(self):
        ax = self.ax_wave; fig = self.fig_wave; data = self.waveform_peak_data
        theme = self.themes[self.current_theme_name]; spine_color = theme['plot_spine']
        if data is None or not ax or not fig or not fig.canvas:
            if ax and fig and fig.canvas:
                placeholder_msg = "NO WAVEFORM DATA" if self.current_song else "LOAD A SONG"
                self.draw_initial_placeholder(ax, fig, spine_color, placeholder_msg)
            return
        try:
            ax.clear(); self._configure_axes(ax, fig, spine_color, theme["plot_bg"])
            if len(data) > 0:
                 x = np.arange(len(data)); y = data * 0.9
                 ax.fill_between(x, 0 - y, 0 + y, color=theme['plot_wave_main'], linewidth=0)
                 ax.set_ylim(-1, 1); ax.set_xlim(0, len(data) - 1 if len(data) > 1 else 1)
            else: # Handle empty/silent audio case visually
                 ax.set_ylim(-1, 1); ax.set_xlim(0, 1)
                 ax.plot([0, 1], [0, 0], color=theme['plot_wave_main'], linewidth=0.5) # Draw flat line
            self.position_indicator_line_wave = None
            # Use the current absolute song time for the indicator position
            current_display_time = np.clip(self.song_time, 0.0, self.song_length if self.song_length > 0 else self.song_time)
            pos_ratio = np.clip(current_display_time / self.song_length, 0.0, 1.0) if self.song_length > 0 else 0.0
            self.draw_waveform_position_indicator(pos_ratio); fig.canvas.draw_idle()
        except Exception as e: print(f"Error drawing static waveform: {e}"); traceback.print_exc(); self.draw_initial_placeholder(ax, fig, spine_color, "DRAW ERROR")


    def draw_waveform_position_indicator(self, position_ratio):
        ax = self.ax_wave; fig = self.fig_wave; data = self.waveform_peak_data; line_attr = 'position_indicator_line_wave'
        theme = self.themes[self.current_theme_name]; indicator_col = theme['plot_wave_indicator']
        if not ax or not fig or not fig.canvas: return
        try:
            num_points = len(data) if data is not None else 0
            x_max = (num_points - 1) if num_points > 1 else 1
            position_ratio = np.clip(position_ratio, 0.0, 1.0)
            x_pos = position_ratio * x_max
            # Ensure x_pos stays within valid range [0, x_max]
            x_pos = max(0, min(x_pos, x_max))

            old_line = getattr(self, line_attr, None)
            if old_line and old_line in ax.lines:
                try: old_line.remove()
                except (ValueError, AttributeError): pass
            if ax:
                 new_line = ax.axvline(x=x_pos, color=indicator_col, linewidth=1.2, ymin=0.05, ymax=0.95)
                 setattr(self, line_attr, new_line)
        except Exception as e: print(f"Error drawing position indicator: {e}"); traceback.print_exc(); setattr(self, line_attr, None)

    def update_oscilloscope(self):
        ax = self.ax_osc; fig = self.fig_osc; theme = self.themes[self.current_theme_name]
        spine_color = theme['plot_spine']; osc_col = theme['plot_osc_main']; bg_col = theme['plot_bg']
        # Conditions to skip update or clear plot
        if (self.raw_sample_data is None or len(self.raw_sample_data) == 0 or
            self.sample_rate is None or self.sample_rate <= 0 or
            not self.playing_state or self.paused or self.is_seeking or # Skip if not actively playing sound
            not ax or not fig or not fig.canvas):
            # Clear plot if stopped/paused/seeking and it currently has data
            if (not self.playing_state or self.paused or self.is_seeking) and ax and fig and fig.canvas and len(ax.lines) > 0:
                self.draw_initial_placeholder(ax, fig, spine_color, "")
            return
        try:
            # Use self.song_time for the current absolute position
            current_sample_index = int(self.song_time * self.sample_rate)
            window_samples = int(self.osc_window_seconds * self.sample_rate)
            if window_samples <= 0: window_samples = max(100, int(0.02 * self.sample_rate)) # Fallback

            # Calculate slice bounds, ensuring they are valid
            start_index = max(0, current_sample_index)
            end_index = min(len(self.raw_sample_data), start_index + window_samples)
            # Adjust start index if end hit boundary to maintain window size if possible
            start_index = max(0, end_index - window_samples)

            sample_slice = self.raw_sample_data[start_index:end_index]

            if len(sample_slice) > 0:
                ax.clear(); self._configure_axes(ax, fig, spine_color, bg_col)
                ax.set_ylim(-1.1, 1.1); x_osc = np.arange(len(sample_slice))
                ax.plot(x_osc, sample_slice, color=osc_col, linewidth=0.8)
                ax.set_xlim(0, len(sample_slice) - 1 if len(sample_slice) > 1 else 1)
                fig.canvas.draw_idle()
            elif len(ax.lines) > 0: # Clear if slice is empty (e.g., seeking past end)
                self.draw_initial_placeholder(ax, fig, spine_color, "")
        except Exception as e: print(f"Error updating oscilloscope: {e}")


    def update_song_position(self):
        """Updates UI elements based on current playback time."""
        # Skip UI updates if user is interacting or seeking programmatically
        if self.slider_active or self.waveform_dragging or self.is_seeking: return

        if self.playing_state and not self.paused:
             try:
                 if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                     current_pos_ms = pygame.mixer.music.get_pos()
                     if current_pos_ms != -1: # -1 indicates error/not playing
                         # Time elapsed since the last play/unpause/seek command
                         time_since_last_play_sec = current_pos_ms / 1000.0
                         # Absolute current time = base time + elapsed time
                         current_abs_time = self.stopped_position + time_since_last_play_sec

                         # Add buffer to prevent premature song end detection due to timing inaccuracies
                         buffer = 0.1 # Allow going slightly past reported length
                         current_abs_time = np.clip(current_abs_time, 0.0, (self.song_length + buffer) if self.song_length > 0 else current_abs_time + 1.0)

                         self.song_time = current_abs_time # Update internal absolute time

                         # --- UI Update Section ---
                         # Time used for slider and labels should be capped at song length
                         display_time_for_ui = np.clip(self.song_time, 0.0, self.song_length if self.song_length > 0 else self.song_time)

                         if self.song_slider and self.song_slider.winfo_exists():
                             self.song_slider.set(display_time_for_ui)
                         if self.current_time_label and self.current_time_label.winfo_exists():
                             mins, secs = divmod(int(display_time_for_ui), 60)
                             time_elapsed_str = f"{mins:02d}:{secs:02d}"
                             # Only update label if text changed to reduce overhead
                             if self.current_time_label.cget("text") != time_elapsed_str:
                                 self.current_time_label.configure(text=time_elapsed_str)

                         pos_ratio = np.clip(display_time_for_ui / self.song_length, 0.0, 1.0) if self.song_length > 0 else 0
                         self.draw_waveform_position_indicator(pos_ratio)
                         if self.fig_wave and self.fig_wave.canvas:
                              self.fig_wave.canvas.draw_idle() # Update waveform plot

                         self.update_oscilloscope() # Update oscilloscope plot
                         # --- End UI Update Section ---

                 else: # Mixer not busy, might have ended or encountered an issue
                     # Check if the internal time is past the song length (allowing for slight inaccuracies)
                     # Or if the mixer explicitly stopped reporting busy
                     if self.root.winfo_exists() and self.playing_state: # Check state again
                        is_past_end = (self.song_length > 0 and self.song_time >= self.song_length - 0.05) # Check against internal time
                        mixer_really_stopped = pygame.mixer.get_init() and not pygame.mixer.music.get_busy()

                        # Schedule end check if past end OR if mixer stopped unexpectedly
                        if is_past_end or mixer_really_stopped:
                            self.root.after(10, self.check_music_end_on_main_thread)


             except pygame.error as e: print(f"Pygame error in update: {e}"); self.has_error = True; self._update_display_title(); self.stop()
             except Exception as e:
                 if self.root.winfo_exists(): print(f"Error during UI update: {e}")
                 self.thread_running = False # Stop thread on other errors


    def start_update_thread(self):
        if not self.thread_running and self.playing_state and not self.paused:
            self.thread_running = True
            if self.update_thread and self.update_thread.is_alive(): return # Don't start if already running
            self.update_thread = threading.Thread(target=self.update_time, daemon=True); self.update_thread.start()
        elif not self.playing_state or self.paused: self.thread_running = False # Ensure flag is correct

    def update_time(self):
        """[Background Thread] Periodically schedules UI updates on main thread."""
        update_interval = 0.05 # Target ~20 FPS for UI updates
        while self.thread_running:
            start_loop_time = time.monotonic()
            try:
                if self.root.winfo_exists():
                     # Schedule update_song_position to run on the main thread
                     self.root.after(0, self.update_song_position)
                else: # Root window closed
                     self.thread_running = False; break
            except Exception as e: # Catch errors during scheduling
                 print(f"Update thread error: {e}"); self.thread_running = False; break

            # Calculate sleep time to maintain interval
            time_taken = time.monotonic() - start_loop_time
            sleep_time = max(0, update_interval - time_taken)
            time.sleep(sleep_time)

            # Re-check state after sleep, it might have changed (e.g., user paused)
            if not self.playing_state or self.paused:
                self.thread_running = False
        # print("Update thread finished.") # Optional debug


    def check_music_end_on_main_thread(self):
        """[Main Thread] Confirms song end and triggers next action."""
        # Double-check state, skip if paused, seeking, or already stopped
        if not self.playing_state or self.paused or self.is_seeking: return
        try:
            # Check if internal time is effectively at/past the end OR mixer stopped
            is_at_end = (self.song_length > 0 and self.song_time >= self.song_length - 0.05)
            mixer_stopped = pygame.mixer.get_init() and not pygame.mixer.music.get_busy()

            if mixer_stopped or is_at_end:
                 print(f"Detected song end: {os.path.basename(self.current_song)} (MixerStopped: {mixer_stopped}, IsAtEnd: {is_at_end})")
                 self.playing_state = False; self.paused = False; self.thread_running = False
                 # Set final position accurately to song length (or 0 if length is 0)
                 final_pos = self.song_length if self.song_length > 0 else 0
                 self.stopped_position = final_pos; self.song_time = final_pos

                 # Update UI to reflect exact end state
                 if self.song_length > 0:
                     if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.set(self.song_length)
                     if self.current_time_label and self.current_time_label.winfo_exists():
                         mins, secs = divmod(int(self.song_length), 60); self.current_time_label.configure(text=f"{mins:02d}:{secs:02d}")
                     self.draw_waveform_position_indicator(1.0) # Indicator at 100%
                 else: # Handle zero-length case
                     if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.set(0);
                     if self.current_time_label and self.current_time_label.winfo_exists(): self.current_time_label.configure(text="00:00");
                     self.draw_waveform_position_indicator(0.0)
                 if self.fig_wave and self.fig_wave.canvas: self.fig_wave.canvas.draw_idle() # Redraw waveform plot

                 # Update button text to Play '▶'
                 if self.play_pause_button and self.play_pause_button.winfo_exists():
                     self.play_pause_button.configure(text="▶")

                 # Clear oscilloscope
                 theme = self.themes[self.current_theme_name]; spine_color = theme['plot_spine']
                 self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color, "")

                 self._update_display_title() # Remove [PLAYING] prefix
                 # Schedule the next action (loop/next/stop)
                 self.root.after(50, self.handle_song_end_action)

            elif not pygame.mixer.get_init(): # Mixer unexpectedly quit
                 print("Mixer stopped unexpectedly.")
                 self.stop() # Ensure consistent state

        except pygame.error as e: print(f"Pygame error during end check: {e}"); self.has_error=True; self._update_display_title(); self.stop()
        except Exception as e: print(f"Error during end check: {e}"); traceback.print_exc(); self.has_error=True; self._update_display_title(); self.stop()


    def handle_song_end_action(self):
        """[Main Thread] Performs action after song ends (loop/next/shuffle/stop)."""
        theme = self.themes[self.current_theme_name]; spine_color = theme['plot_spine']
        if self.loop_state == 2: # Loop One
             print("Looping current song.")
             if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.set(0);
             if self.current_time_label and self.current_time_label.winfo_exists(): self.current_time_label.configure(text="00:00");
             self.play_music() # play_music resets time and starts playback
        elif self.loop_state == 1: # Loop All
             print("Looping all - playing next.")
             self.next_song(auto_advance=True)
        elif self.shuffle_state: # Mix
             print("Mix on - playing random.")
             self.play_random_song(auto_advance=True)
        else: # No Loop, No Mix
             if self.current_song_index >= len(self.songs_list) - 1: # End of playlist
                 print("End of tracklist reached.")
                 # Reset state to stopped at beginning
                 self.stopped_position = 0.0; self.song_time = 0.0; self.current_song_index = 0
                 if self.songs_list: self.select_song(self.current_song_index) # Highlight first song
                 if self.song_slider and self.song_slider.winfo_exists(): self.song_slider.set(0);
                 if self.current_time_label and self.current_time_label.winfo_exists(): self.current_time_label.configure(text="00:00");
                 self.draw_waveform_position_indicator(0)
                 if self.fig_wave and self.fig_wave.canvas: self.fig_wave.canvas.draw_idle()
                 self.draw_initial_placeholder(self.ax_osc, self.fig_osc, spine_color,"")
                 last_song_name = os.path.basename(self.current_song) if self.current_song else "TRACKLIST END"
                 self._update_display_title(base_title=last_song_name)
                 # Ensure button shows Play
                 if self.play_pause_button and self.play_pause_button.winfo_exists():
                     self.play_pause_button.configure(text="▶")
             else: # Play next song in sequence
                 print("Playing next song in sequence.")
                 self.next_song(auto_advance=True)


    def play_random_song(self, auto_advance=False):
        if not self.songs_list: self.stop(); return
        if not auto_advance: self.stop()
        else: # Auto-advance just resets state, doesn't call stop()
            self.playing_state = False; self.paused = False; self.thread_running = False;
            self.abort_waveform_generation(); self.stopped_position = 0.0; self.song_time = 0.0
            # Let play_music handle setting button text
            print("Auto-advancing to random song.")
        if len(self.songs_list) > 1:
             possible_indices = [i for i in range(len(self.songs_list)) if i != self.current_song_index]
             if not possible_indices: possible_indices = list(range(len(self.songs_list))) # Avoid empty list if only one song repeated
             self.current_song_index = random.choice(possible_indices)
        elif len(self.songs_list) == 1: self.current_song_index = 0
        else: self.clear_playlist(); return
        self.play_music() # play_music will start from beginning

    def abort_waveform_generation(self):
        if self.waveform_thread and self.waveform_thread.is_alive():
            if not self.waveform_abort_flag.is_set():
                 print(f"Signalling waveform thread to abort...")
                 self.waveform_abort_flag.set()
                 if self.is_generating_waveform:
                      self.is_generating_waveform = False
                      # Update title if it shows generating
                      if self.current_song and "[GENERATING...]" in self.song_title_var.get():
                          self._update_display_title()

    def on_closing(self):
        print("Closing application..."); self.thread_running = False; self.abort_waveform_generation()
        try:
            if pygame.mixer.get_init(): pygame.mixer.music.stop(); pygame.mixer.quit(); print("Pygame stopped.")
        except Exception as e: print(f"Error quitting pygame: {e}")
        try: plt.close(self.fig_wave)
        except Exception: pass
        try: plt.close(self.fig_osc)
        except Exception: pass
        if self.root: self.root.destroy(); print("Application closed.")

# --- Main Execution Block ---
if __name__ == "__main__":
    try:
        if os.name == 'nt':
             try: from ctypes import windll; windll.shcore.SetProcessDpiAwareness(1)
             except Exception: pass
        root = ctk.CTk()
        player = MN1MusicPlayer (root)
        root.mainloop()
    except Exception as main_error:
        print("\n--- FATAL APPLICATION ERROR ---"); print(f"Error: {main_error}"); traceback.print_exc()
        try: import tkinter as tk; from tkinter import messagebox; root_err = tk.Tk(); root_err.withdraw(); messagebox.showerror("Fatal Error", f"Critical error:\n\n{main_error}\n\nSee console."); root_err.destroy()
        except Exception: pass
        input("Press Enter to exit console.")