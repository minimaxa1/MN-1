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
        self.root.title("MN-1")
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

        self.song_slider = ctk.CTkSlider(self.slider_frame, from_=0, to=100, command=self.slide_song, variable=ctk.DoubleVar()) # Added command back
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
            text="MN-1",
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

        # Theme button text is now always "MN-1"
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
                    text=theme_button_display_text, # Set text to "MN-1"
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
                # self.fig_wave.canvas.draw_idle() # Draw handled by draw_static_matplotlib_waveform

            # Oscilloscope Plot
            if self.ax_osc and self.fig_osc and self.fig_osc.canvas:
                 self._configure_axes(self.ax_osc, self.fig_osc, theme["plot_osc_main"], theme["plot_bg"]) # Use accent color for border too
                 if self.playing_state and self.raw_sample_data is not None:
                     self.update_oscilloscope() # Will redraw with new colors
                 else:
                      self.draw_initial_placeholder(self.ax_osc, self.fig_osc, theme["plot_osc_main"], "", theme["plot_text"]) # Redraw placeholder
                 # self.fig_osc.canvas.draw_idle() # Draw handled by update_oscilloscope or placeholder draw

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


    # --- Playback Control Methods ---
    def play(self):
        """Handles the Play button action."""
        if not self.songs_list:
             self._update_display_title(base_title="TRACKLIST EMPTY"); return

        self.has_error = False

        theme = self.themes[self.current_theme_name] # Get current theme
        active_button_color = theme['button_hover'] # Or define a specific 'active' color
        default_button_color = theme['button_fg']

        if self.paused: # Unpause
            self.play_button.configure(fg_color=active_button_color); self.root.after(100, lambda: self.play_button.configure(fg_color=default_button_color))
            try:
                pygame.mixer.music.unpause()
                self.paused = False; self.playing_state = True
                self._update_display_title()
                self.start_update_thread()
            except pygame.error as e: print(f"Pygame error during unpause: {e}")

        elif not self.playing_state: # Play new or resume stopped
            song_to_play_index = -1; selected_idx = -1
            for i, entry in enumerate(self.playlist_entries):
                 # Check entry exists before accessing 'selected'
                 if entry and entry.get("frame") and entry["frame"].winfo_exists() and entry.get("selected"):
                    selected_idx = i
                    break

            # Determine index: 1) Selected song, 2) Current song if stopped, 3) First song
            if selected_idx != -1 and 0 <= selected_idx < len(self.songs_list):
                song_to_play_index = selected_idx
            elif self.current_song and self.stopped_position > 0 and 0 <= self.current_song_index < len(self.songs_list) and self.songs_list[self.current_song_index] == self.current_song:
                song_to_play_index = self.current_song_index
            elif self.songs_list:
                 # If nothing specific, play the currently selected index if valid, otherwise 0
                 current_selected_index = -1
                 for i, entry in enumerate(self.playlist_entries):
                     # Check entry exists before accessing 'selected'
                     if entry and entry.get("frame") and entry["frame"].winfo_exists() and entry.get("selected"):
                         current_selected_index = i
                         break
                 if 0 <= current_selected_index < len(self.songs_list):
                      song_to_play_index = current_selected_index
                 elif 0 <= self.current_song_index < len(self.songs_list): # Fallback to internal index
                     song_to_play_index = self.current_song_index
                 else:
                     song_to_play_index = 0 # Fallback to first song

            if song_to_play_index != -1:
                is_resuming = (song_to_play_index == self.current_song_index and self.stopped_position > 0 and self.current_song == self.songs_list[song_to_play_index])
                new_song_path = self.songs_list[song_to_play_index]
                song_changed = (new_song_path != self.current_song)

                self.current_song_index = song_to_play_index
                self.current_song = new_song_path
                self.select_song(self.current_song_index) # Ensure UI highlights the song being played

                try:
                    self.play_button.configure(fg_color=active_button_color); self.root.after(100, lambda: self.play_button.configure(fg_color=default_button_color))
                    self.is_loading = True; self._update_display_title()

                    if song_changed:
                         self.abort_waveform_generation()
                         self.update_song_info() # Get length etc. before loading waveform
                         self.draw_initial_placeholder(self.ax_wave, self.fig_wave, theme['plot_spine'], "LOADING...")
                         self.draw_initial_placeholder(self.ax_osc, self.fig_osc, theme['plot_osc_main'], "")

                    pygame.mixer.music.load(self.current_song)
                    start_pos = self.stopped_position if is_resuming else 0.0
                    pygame.mixer.music.play(start=start_pos)
                    if not is_resuming: self.stopped_position = 0.0 # Reset stopped position if playing from start

                    self.playing_state = True; self.paused = False; self.is_loading = False
                    self._update_display_title()
                    self.start_update_thread()
                    if song_changed: self.trigger_waveform_generation() # Generate waveform for the new song

                except pygame.error as e: print(f"Pygame Error: {e}"); self.has_error = True; self.is_loading = False; self._update_display_title(base_title=f"{os.path.basename(self.current_song)}"); self.playing_state = False; self.paused = False; self.current_song = ""
                except Exception as e: print(f"Error: {e}"); traceback.print_exc(); self.has_error = True; self.is_loading = False; self._update_display_title(base_title=f"{os.path.basename(self.current_song)}"); self.playing_state = False; self.paused = False; self.current_song = ""
            else: self._update_display_title(base_title="TRACKLIST EMPTY?")

    def play_music(self):
        """Core function to load and play a song from the beginning."""
        if not self.songs_list or not (0 <= self.current_song_index < len(self.songs_list)):
            self._update_display_title(base_title="INVALID SELECTION"); return

        self.has_error = False
        self.current_song = self.songs_list[self.current_song_index]
        self.stopped_position = 0.0 # Playing from start resets this
        theme = self.themes[self.current_theme_name]

        try:
            self.abort_waveform_generation() # Stop any previous generation
            print(f"play_music: Loading {os.path.basename(self.current_song)}")
            self.is_loading = True; self._update_display_title()

            pygame.mixer.music.stop() # Ensure previous playback is stopped
            pygame.mixer.music.load(self.current_song)
            self.update_song_info() # Get length etc. after loading, before playing
            pygame.mixer.music.play()

            self.playing_state = True; self.paused = False; self.is_loading = False
            self.select_song(self.current_song_index) # Ensure correct song is highlighted
            self._update_display_title()

            # Update UI immediately after starting play
            self.song_slider.set(0)
            self.current_time_label.configure(text="00:00")
            self.draw_initial_placeholder(self.ax_wave, self.fig_wave, theme['plot_spine'],"GENERATING...")
            self.draw_initial_placeholder(self.ax_osc, self.fig_osc, theme['plot_osc_main'],"")

            self.trigger_waveform_generation() # Start generating waveform in background
            self.start_update_thread() # Start updating time display

        except pygame.error as e: print(f"Pygame Error: {e}"); self.has_error = True; self.is_loading = False; self._update_display_title(base_title=f"{os.path.basename(self.current_song)}"); self.playing_state = False; self.paused = False; self.current_song = ""; self.draw_initial_placeholder(self.ax_wave, self.fig_wave, theme['plot_spine'],"LOAD ERROR"); self.draw_initial_placeholder(self.ax_osc, self.fig_osc, theme['plot_osc_main'],"")
        except Exception as e: print(f"Error: {e}"); traceback.print_exc(); self.has_error = True; self.is_loading = False; self._update_display_title(base_title=f"{os.path.basename(self.current_song)}"); self.playing_state = False; self.paused = False; self.current_song = ""; self.draw_initial_placeholder(self.ax_wave, self.fig_wave, theme['plot_spine'],"ERROR"); self.draw_initial_placeholder(self.ax_osc, self.fig_osc, theme['plot_osc_main'],"")


    def pause(self):
        """Handles the Pause button action."""
        theme = self.themes[self.current_theme_name] # Get current theme
        active_button_color = theme['button_hover']
        default_button_color = theme['button_fg']

        if self.playing_state and not self.paused: # Pause
            self.pause_button.configure(fg_color=active_button_color); self.root.after(100, lambda: self.pause_button.configure(fg_color=default_button_color))
            try:
                pygame.mixer.music.pause()
                self.paused = True; self.playing_state = False
                self._update_display_title()
                self.thread_running = False # Stop the update thread while paused
                print("Playback Paused.")
            except pygame.error as e: print(f"Pygame error during pause: {e}")
        elif self.paused: # Unpause (calls play which handles unpausing)
            self.play()

    def stop(self):
        """Stops playback completely and records the position."""
        if self.playing_state or self.paused:
            try:
                # Ensure song_time is updated before stopping if possible
                if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                    current_pos_ms = pygame.mixer.music.get_pos()
                    if current_pos_ms != -1:
                        self.song_time = current_pos_ms / 1000.0
                self.stopped_position = self.song_time
                print(f"Stop called, recording pos: {self.song_time:.2f}s")
                pygame.mixer.music.stop()
            except pygame.error as e: print(f"Pygame error during stop: {e}")
            finally:
                was_playing_or_paused = self.playing_state or self.paused
                self.playing_state = False; self.paused = False
                self._update_display_title() # Update title to remove [PLAYING]/[PAUSED]
                self.thread_running = False

                if was_playing_or_paused:
                    # Make sure slider reflects the *stopped* position
                    if self.stopped_position > 0:
                         # Ensure slider value is within bounds
                         slider_val = np.clip(self.stopped_position, 0.0, self.song_length if self.song_length > 0 else 100.0)
                         self.song_slider.set(slider_val)
                         mins, secs = divmod(int(self.stopped_position), 60)
                         self.current_time_label.configure(text=f"{mins:02d}:{secs:02d}")
                         theme = self.themes[self.current_theme_name]
                         if self.song_length > 0:
                             pos_ratio = np.clip(self.stopped_position / self.song_length, 0.0, 1.0)
                             self.draw_waveform_position_indicator(pos_ratio)
                             if self.fig_wave and self.fig_wave.canvas: self.fig_wave.canvas.draw_idle() # Ensure redraw
                         else:
                             self.draw_waveform_position_indicator(0)
                             if self.fig_wave and self.fig_wave.canvas: self.fig_wave.canvas.draw_idle() # Ensure redraw

                         self.draw_initial_placeholder(self.ax_osc, self.fig_osc, theme['plot_osc_main'],"")
                         print(f"Stopped. Pos recorded: {self.stopped_position:.2f}s")
                    else: # Stopped at beginning
                         self.song_slider.set(0); self.current_time_label.configure(text="00:00")
                         self.draw_waveform_position_indicator(0)
                         if self.fig_wave and self.fig_wave.canvas: self.fig_wave.canvas.draw_idle() # Ensure redraw
                         theme = self.themes[self.current_theme_name]
                         self.draw_initial_placeholder(self.ax_osc, self.fig_osc, theme['plot_osc_main'],"")

        else: # If already stopped, just ensure thread is stopped
             self.thread_running = False
             if self.current_song: self._update_display_title() # Ensure title reflects stopped state


    def previous_song(self):
        """Stops current song and plays the previous one."""
        if not self.songs_list: self._update_display_title(base_title="TRACKLIST EMPTY"); return
        original_index = self.current_song_index
        self.stop() # Stop current playback first
        if len(self.songs_list) > 0:
            self.current_song_index = (original_index - 1 + len(self.songs_list)) % len(self.songs_list)
            self.play_music() # Play the new song from the beginning

    def next_song(self, auto_advance=False):
        """Plays the next song in the list."""
        if not self.songs_list: self._update_display_title(base_title="TRACKLIST EMPTY"); return
        original_index = self.current_song_index

        if not auto_advance: self.stop() # Stop manually if not auto-advancing
        else:
            # If auto-advancing, just update state without stopping pygame mixer explicitly
            self.playing_state = False; self.paused = False; self.thread_running = False
            self.abort_waveform_generation(); self.stopped_position = 0.0
            print("Auto-advancing to next song.")

        if len(self.songs_list) > 0:
             self.current_song_index = (original_index + 1) % len(self.songs_list)
             self.play_music() # Play the new song from the beginning

    # --- Volume/Mix/Loop ---
    def volume_adjust(self, value):
        """Callback for volume slider change."""
        volume = float(value)
        try: pygame.mixer.music.set_volume(volume)
        except Exception as e: print(f"Warning: Could not set volume: {e}"); return

        theme = self.themes[self.current_theme_name]
        if volume > 0 and self.muted: # Unmuting via slider
             self.muted = False; self.volume_button.configure(text="VOL", text_color=theme["inactive_button_fg"])
        elif volume == 0 and not self.muted: # Muting via slider
             self.muted = True; self.volume_button.configure(text="MUTED", text_color=theme["muted_fg"])
        if volume > 0: self.previous_volume = volume # Store last non-zero volume

    def toggle_mute(self):
        """Toggles mute state on/off."""
        theme = self.themes[self.current_theme_name]
        if self.muted: # Unmute
             try:
                 pygame.mixer.music.set_volume(self.previous_volume)
                 self.volume_slider.set(self.previous_volume)
                 self.muted = False
                 self.volume_button.configure(text="VOL", text_color=theme["inactive_button_fg"])
             except Exception as e: print(f"Warning: Could not set volume on unmute: {e}")
        else: # Mute
             try:
                 current_vol = pygame.mixer.music.get_volume()
                 if current_vol > 0: self.previous_volume = current_vol # Store current volume before muting
                 pygame.mixer.music.set_volume(0)
                 self.volume_slider.set(0)
                 self.muted = True
                 self.volume_button.configure(text="MUTED", text_color=theme["muted_fg"])
             except Exception as e: print(f"Warning: Could not set volume on mute: {e}")

    def toggle_mix(self):
        """Toggles mix (shuffle) mode on/off."""
        self.shuffle_state = not self.shuffle_state
        state_text = "ON" if self.shuffle_state else "OFF"
        theme = self.themes[self.current_theme_name]
        # Use active/inactive colors defined in the theme
        color = theme["active_button_fg"] if self.shuffle_state else theme["inactive_button_fg"]
        self.mix_button.configure(text_color=color)
        print(f"Mix toggled: {state_text}")

    def toggle_loop(self):
        """Cycles through loop modes."""
        self.loop_state = (self.loop_state + 1) % 3
        theme = self.themes[self.current_theme_name]
        # Use active/inactive colors defined in the theme
        color = theme["active_button_fg"] if self.loop_state > 0 else theme["inactive_button_fg"]
        self.loop_button.configure(text_color=color)

        if self.loop_state == 0: print("Loop toggled: OFF"); self.loop_button.configure(text="LOOP")
        elif self.loop_state == 1: print("Loop toggled: ALL"); self.loop_button.configure(text="LOOP ALL")
        else: print("Loop toggled: ONE"); self.loop_button.configure(text="LOOP ONE")

    # --- Slider & Waveform Interaction ---
    def slider_start_scroll(self, event):
        if self.current_song and self.song_length > 0: self.slider_active = True
        else: self.slider_active = False

    def slider_stop_scroll(self, event):
        if not self.slider_active: return
        self.slider_active = False
        position = float(self.song_slider.get())
        print(f"Slider release - Seeking to: {position:.2f}s")
        self.seek_song(position)

    # <<< --- slide_song METHOD ADDED BACK --- >>>
    def slide_song(self, value):
        """Callback function for when the song slider is actively moved."""
        # Only update visuals if the user is actively dragging the slider
        if not self.slider_active:
            return

        position = float(value)
        self.song_time = position # Update internal time temporarily for display consistency
        # Format time display
        mins, secs = divmod(int(position), 60)
        time_str = f"{mins:02d}:{secs:02d}"
        # Update the current time label
        if self.current_time_label and self.current_time_label.winfo_exists():
            self.current_time_label.configure(text=time_str)

        # Update the waveform position indicator
        if self.song_length > 0:
            position_ratio = np.clip(position / self.song_length, 0.0, 1.0)
            self.draw_waveform_position_indicator(position_ratio)
            # Ensure the plot redraws to show the moving indicator
            if self.fig_wave and self.fig_wave.canvas:
                self.fig_wave.canvas.draw_idle()
        else:
            self.draw_waveform_position_indicator(0)
            if self.fig_wave and self.fig_wave.canvas:
                self.fig_wave.canvas.draw_idle()
    # <<< --- END OF slide_song METHOD --- >>>


    def on_waveform_press(self, event):
        if (event.inaxes != self.ax_wave or self.waveform_peak_data is None or len(self.waveform_peak_data) == 0 or self.song_length <= 0):
            self.waveform_dragging = False; return
        self.waveform_dragging = True; self.slider_active = True # Treat waveform drag like slider drag
        self._update_position_from_waveform_event(event)

    def on_waveform_motion(self, event):
        if not self.waveform_dragging or event.inaxes != self.ax_wave: return
        self._update_position_from_waveform_event(event)

    def on_waveform_release(self, event):
        if not self.waveform_dragging: return
        self.waveform_dragging = False; self.slider_active = False
        # Get the final target time from the UI elements updated during drag
        target_time = float(self.song_slider.get())
        print(f"Waveform release - Seeking to: {target_time:.2f}s")
        self.seek_song(target_time)

    def on_waveform_leave(self, event):
        # If mouse leaves plot area while dragging, treat it as a release
        if self.waveform_dragging:
            print("Waveform leave while dragging - treating as release")
            self.on_waveform_release(event) # Trigger the seek

    def _update_position_from_waveform_event(self, event):
        """Updates slider/time label based on mouse position during waveform drag."""
        if (self.waveform_peak_data is None or len(self.waveform_peak_data) == 0 or self.song_length <= 0 or event.xdata is None): return
        num_points = len(self.waveform_peak_data)
        x_coord = event.xdata
        # Calculate position ratio based on x-coordinate within the plot axes
        position_ratio = np.clip(x_coord / (num_points - 1), 0.0, 1.0) if num_points > 1 else 0.0
        target_time = position_ratio * self.song_length
        self.song_time = target_time # Keep internal time synced
        self.song_slider.set(target_time) # Update slider position visually
        mins, secs = divmod(int(target_time), 60)
        self.current_time_label.configure(text=f"{mins:02d}:{secs:02d}") # Update time label
        self.draw_waveform_position_indicator(position_ratio) # Update indicator line
        if self.fig_wave and self.fig_wave.canvas: self.fig_wave.canvas.draw_idle() # Redraw needed


    # --- Seeking Logic ---
    def seek_song(self, position_seconds):
        """Seeks playback to the specified time in seconds."""
        if self.current_song and self.song_length > 0:
            self.has_error = False
            seek_pos = np.clip(position_seconds, 0.0, self.song_length)
            print(f"Seeking to: {seek_pos:.2f}s (requested: {position_seconds:.2f}s)")

            # Update UI immediately to reflect the seek target
            self.song_time = seek_pos
            self.song_slider.set(seek_pos)
            mins, secs = divmod(int(seek_pos), 60)
            self.current_time_label.configure(text=f"{mins:02d}:{secs:02d}")
            pos_ratio = np.clip(seek_pos / self.song_length, 0.0, 1.0)
            self.draw_waveform_position_indicator(pos_ratio)
            if self.fig_wave and self.fig_wave.canvas: self.fig_wave.canvas.draw_idle() # Redraw wave plot
            if self.raw_sample_data is not None: self.update_oscilloscope() # Update scope to new position

            # Handle audio playback seek
            try:
                if self.playing_state or self.paused: # If currently playing or paused
                    was_paused = self.paused
                    # Pygame's play(start=...) handles seeking
                    pygame.mixer.music.play(start=seek_pos)
                    if was_paused:
                        pygame.mixer.music.pause() # Re-pause if it was paused before seek
                        self.playing_state = False; self.paused = True # Ensure state is correct
                    else:
                        self.playing_state = True; self.paused = False # Ensure state is correct
                        self.start_update_thread() # Restart thread if it was playing
                    self._update_display_title()
                else: # If player was completely stopped
                    self.stopped_position = seek_pos # Update the position for the next play press
                    self._update_display_title()
                    print(f"Player stopped, updated next start pos to {seek_pos:.2f}s")

            except pygame.error as e: print(f"Pygame error on seek: {e}"); self.has_error = True; self._update_display_title()
            except Exception as e: print(f"General error on seek: {e}"); traceback.print_exc(); self.has_error = True; self._update_display_title()
        else: print("Seek ignored: No song or zero length.")

    # --- Song Info & Metadata ---
    def update_song_info(self):
        """Updates labels and slider range based on the current song's metadata."""
        if not self.current_song:
            self._update_display_title(base_title="NO SONG LOADED"); self.total_time_label.configure(text="00:00"); self.song_slider.configure(to=100, number_of_steps=100); self.song_slider.set(0); self.song_length = 0.0; return

        song_name = os.path.basename(self.current_song)
        try:
            file_extension = os.path.splitext(self.current_song)[1].lower()
            audio = None
            if file_extension == '.mp3': audio = MP3(self.current_song)
            elif file_extension == '.flac': audio = FLAC_MUTAGEN(self.current_song)

            if audio and hasattr(audio, 'info') and hasattr(audio.info, 'length'):
                self.song_length = audio.info.length
                if not isinstance(self.song_length, (int, float)) or self.song_length <= 0:
                     print(f"Warning: Invalid song length detected for {song_name}: {self.song_length}")
                     self.song_length = 0.0

                mins, secs = divmod(int(self.song_length), 60); self.total_time = f"{mins:02d}:{secs:02d}"
                self.total_time_label.configure(text=self.total_time)

                slider_max = max(1.0, self.song_length) # Ensure slider max is at least 1
                num_steps = max(100, int(slider_max * 5)) # More steps for longer songs
                self.song_slider.configure(to=slider_max, number_of_steps=num_steps)

                # Reset time display only if starting from beginning
                if self.stopped_position == 0 and not self.playing_state:
                    self.song_slider.set(0)
                    self.current_time_label.configure(text="00:00")

            else: raise ValueError(f"Mutagen could not read info/length for {song_name}")
        except Exception as e:
            print(f"Error getting song info: {e}"); self.has_error = True; self._update_display_title(base_title=song_name); self.song_length = 0.0; self.total_time = "00:00"; self.total_time_label.configure(text=self.total_time); self.song_slider.configure(to=100, number_of_steps=100); self.song_slider.set(0); self.current_time_label.configure(text="00:00")

    # --- Waveform Generation ---
    def trigger_waveform_generation(self):
        """Initiates background waveform data generation."""
        if self.waveform_thread and self.waveform_thread.is_alive():
            print("Waveform generation already in progress. Aborting previous.")
            self.abort_waveform_generation(); time.sleep(0.05) # Give thread time to exit
        if not self.current_song: return

        self.waveform_peak_data = None; self.raw_sample_data = None; self.sample_rate = None
        self.is_generating_waveform = True; self.has_error = False
        self._update_display_title() # Show [GENERATING...]
        theme = self.themes[self.current_theme_name]
        self.draw_initial_placeholder(self.ax_wave, self.fig_wave, theme['plot_spine'],"GENERATING...")
        self.draw_initial_placeholder(self.ax_osc, self.fig_osc, theme['plot_osc_main'],"")

        self.waveform_abort_flag.clear()
        self.waveform_thread = threading.Thread(target=self.generate_waveform_data_background, args=(self.current_song, self.waveform_abort_flag), daemon=True)
        print(f"Trigger waveform generation: Starting thread for {os.path.basename(self.current_song)}")
        self.waveform_thread.start()

    def generate_waveform_data_background(self, song_path, abort_flag):
        """[Background Thread] Loads audio and processes samples."""
        print(f"BG_THREAD: Starting waveform generation for: {os.path.basename(song_path)}")
        local_peak_data = None; local_raw_data = None; effective_sample_rate = None; error_message = None
        try:
            start_time = time.monotonic()
            if abort_flag.is_set(): print(f"BG_THREAD: Aborted early"); return
            if not os.path.exists(song_path): raise FileNotFoundError(f"Audio file not found: {song_path}")

            # --- Load with Pydub ---
            try:
                sound = AudioSegment.from_file(song_path)
            except FileNotFoundError as fnf_err:
                # Check if it's the ffmpeg dependency error
                if "ffmpeg" in str(fnf_err).lower() or "ffprobe" in str(fnf_err).lower():
                     raise ImportError("FFmpeg/FFprobe not found.")
                else:
                     raise # Re-raise original FileNotFoundError
            except Exception as load_err:
                 raise RuntimeError(f"Pydub load failed: {load_err}")

            if abort_flag.is_set(): print(f"BG_THREAD: Aborted after load"); return

            # --- Process Samples ---
            original_sample_rate = sound.frame_rate
            bit_depth = sound.sample_width * 8 if sound.sample_width > 0 else 16 # Default to 16 if unknown
            # Use pydub's max possible amplitude for normalization
            calculated_max_val = sound.max_possible_amplitude if hasattr(sound, 'max_possible_amplitude') else 2**(bit_depth - 1)

            samples_array = np.array(sound.get_array_of_samples())
            if samples_array.size == 0: raise ValueError("Audio file contains no samples.")

            # Convert to mono float64 [-1.0, 1.0]
            if sound.channels == 2:
                mono_samples = samples_array.astype(np.float64).reshape((-1, 2)).mean(axis=1)
            else:
                mono_samples = samples_array.astype(np.float64)

            mono_samples_normalized = np.clip(mono_samples / calculated_max_val, -1.0, 1.0)

            if abort_flag.is_set(): print(f"BG_THREAD: Aborted after normalization"); return

            # --- Prepare Raw Data (for Oscilloscope) ---
            if self.osc_downsample_factor > 1:
                 local_raw_data = mono_samples_normalized[::self.osc_downsample_factor]
                 effective_sample_rate = original_sample_rate / self.osc_downsample_factor
            else:
                 local_raw_data = mono_samples_normalized
                 effective_sample_rate = original_sample_rate

            if abort_flag.is_set(): print(f"BG_THREAD: Aborted during raw processing"); return

            # --- Prepare Peak Data (for Waveform) ---
            target_points = 500 # Number of points for the static waveform display
            if len(mono_samples_normalized) > 0:
                chunk_size = max(1, len(mono_samples_normalized) // target_points)
                processed_peaks = []
                num_chunks = (len(mono_samples_normalized) + chunk_size - 1) // chunk_size
                for i in range(num_chunks):
                     # Check abort flag periodically
                     if i % 100 == 0 and abort_flag.is_set(): print(f"BG_THREAD: Aborted peak processing"); return
                     start = i * chunk_size
                     end = min((i + 1) * chunk_size, len(mono_samples_normalized))
                     chunk = mono_samples_normalized[start:end]
                     peak = np.max(np.abs(chunk)) if len(chunk) > 0 else 0.0
                     processed_peaks.append(peak)
                local_peak_data = np.array(processed_peaks)
            else:
                local_peak_data = np.array([]) # Handle empty input

            print(f"BG_THREAD: Finished waveform generation for: {os.path.basename(song_path)} in {time.monotonic() - start_time:.2f}s")

        except ImportError as e: error_message = f"WAVEFORM ERROR\n({e})"
        except FileNotFoundError as e: error_message = f"WAVEFORM ERROR\nFile Not Found"
        except MemoryError: error_message = "WAVEFORM ERROR\nMemory Error"
        except Exception as e: print(f"BG_THREAD: Error generating waveform:"); traceback.print_exc(); error_message = f"WAVEFORM ERROR\n({type(e).__name__})"
        finally:
            # Schedule result processing on main thread if not aborted
            if not abort_flag.is_set():
                if self.root.winfo_exists():
                    self.root.after(1, self.process_waveform_result, song_path, local_peak_data, local_raw_data, effective_sample_rate, error_message)
                else:
                    print(f"BG_THREAD: Root window closed, skipping result.")
            else:
                print(f"BG_THREAD: Waveform generation aborted, result not processed.")

    def process_waveform_result(self, song_path, peak_data, raw_data, sample_rate, error_message):
        """[Main Thread] Processes results from background waveform generation."""
        # Check if the result is still relevant for the currently loaded song
        if song_path != self.current_song:
            print(f"Ignoring stale waveform result for: {os.path.basename(song_path)}")
            # If this was the last active thread, reset the flag
            if self.waveform_thread and not self.waveform_thread.is_alive():
                self.is_generating_waveform = False
            return

        print(f"Processing waveform result for: {os.path.basename(song_path)}")
        self.is_generating_waveform = False # Mark generation as complete
        theme = self.themes[self.current_theme_name]

        if error_message:
            self.waveform_peak_data = None; self.raw_sample_data = None; self.sample_rate = None; self.has_error = True
            self._update_display_title(base_title=os.path.basename(song_path)) # Show error in title
            self.draw_initial_placeholder(self.ax_wave, self.fig_wave, theme['plot_spine'], error_message)
            self.draw_initial_placeholder(self.ax_osc, self.fig_osc, theme['plot_osc_main'], "")
            print(f"Waveform error processed: {error_message}")
        elif peak_data is not None and raw_data is not None and sample_rate is not None and len(peak_data) > 0 and len(raw_data) > 0:
            self.waveform_peak_data = peak_data; self.raw_sample_data = raw_data; self.sample_rate = sample_rate; self.has_error = False
            self._update_display_title() # Update title (remove generating message)
            self.draw_static_matplotlib_waveform() # Draw the new waveform
            # Update position indicator and oscilloscope based on current playback time
            self.update_song_position()
            print("Waveform data processed successfully.")
        else: # Handle cases where data is empty or invalid but no specific error message was set
             self.waveform_peak_data = None; self.raw_sample_data = None; self.sample_rate = None; self.has_error = True
             self._update_display_title(base_title=os.path.basename(song_path))
             self.draw_initial_placeholder(self.ax_wave, self.fig_wave, theme['plot_spine'],"GEN FAILED (No Data)")
             self.draw_initial_placeholder(self.ax_osc, self.fig_osc, theme['plot_osc_main'],"")

    def draw_static_matplotlib_waveform(self):
        """Draws the static peak waveform using theme colors."""
        ax = self.ax_wave; fig = self.fig_wave; data = self.waveform_peak_data
        theme = self.themes[self.current_theme_name]

        if data is None or len(data) == 0 or not ax or not fig or not fig.canvas:
            if ax and fig and fig.canvas:
                # Show appropriate placeholder if no data
                placeholder_msg = "NO WAVEFORM DATA" if self.current_song else "LOAD A SONG"
                self.draw_initial_placeholder(ax, fig, theme['plot_spine'], placeholder_msg)
            return
        try:
            ax.clear(); self._configure_axes(ax, fig, theme['plot_spine'], theme['plot_bg'])
            x = np.arange(len(data)); y = data * 0.9 # Scale down slightly from edges
            ax.fill_between(x, 0 - y, 0 + y, color=theme['plot_wave_main'], linewidth=0) # Uses plot_wave_main from theme
            ax.set_ylim(-1, 1); ax.set_xlim(0, len(data) - 1 if len(data) > 1 else 1)
            # fig.canvas.draw_idle() # Draw handled by indicator draw
            self.position_indicator_line_wave = None # Clear old indicator line reference
            # Re-draw indicator at current position after drawing waveform
            if self.song_length > 0:
                self.draw_waveform_position_indicator(np.clip(self.song_time / self.song_length, 0.0, 1.0))
            else:
                self.draw_waveform_position_indicator(0.0)
            # Ensure canvas redraws after indicator
            fig.canvas.draw_idle()


        except Exception as e: print(f"Error drawing static waveform: {e}"); traceback.print_exc(); self.draw_initial_placeholder(ax, fig, theme['plot_spine'], "DRAW ERROR")

    def draw_waveform_position_indicator(self, position_ratio):
        """Draws the position indicator using theme color."""
        ax = self.ax_wave; fig = self.fig_wave; data = self.waveform_peak_data; line_attr = 'position_indicator_line_wave'
        theme = self.themes[self.current_theme_name]

        # Ensure we have data and a valid plot area
        if data is None or len(data) == 0 or not ax or not fig or not fig.canvas: return
        try:
            num_points = len(data)
            position_ratio = np.clip(position_ratio, 0.0, 1.0)
            # Calculate x-coordinate based on ratio and number of points
            x_pos = position_ratio * (num_points - 1) if num_points > 1 else 0
            # Ensure x_pos stays within the valid range of the x-axis
            x_pos = max(0, min(x_pos, num_points - 1)) if num_points > 1 else 0

            # Remove the previous indicator line if it exists
            old_line = getattr(self, line_attr, None)
            if old_line and old_line in ax.lines:
                try: old_line.remove()
                except (ValueError, AttributeError): pass # Ignore if already removed

            # Draw the new vertical line using the theme color
            if ax:
                 new_line = ax.axvline(x=x_pos, color=theme['plot_wave_indicator'], linewidth=1.2, ymin=0.05, ymax=0.95) # Inset slightly
                 setattr(self, line_attr, new_line) # Store reference to the new line
            # fig.canvas.draw_idle() # Delay draw until caller ensures it
        except Exception as e: print(f"Error drawing position indicator: {e}"); traceback.print_exc(); setattr(self, line_attr, None)

    def update_oscilloscope(self):
        """Updates the oscilloscope plot using theme colors."""
        ax = self.ax_osc; fig = self.fig_osc
        theme = self.themes[self.current_theme_name]

        # Conditions to skip update
        if (self.raw_sample_data is None or len(self.raw_sample_data) == 0 or
            self.sample_rate is None or self.sample_rate <= 0 or
            not self.playing_state or self.paused or # Only update if actively playing
            not ax or not fig or not fig.canvas):
            # If stopped/paused, clear the oscilloscope if it has lines drawn
            if (not self.playing_state or self.paused) and ax and fig and fig.canvas:
                 if len(ax.lines) > 0: # Only clear if something is drawn
                    self.draw_initial_placeholder(ax, fig, theme['plot_osc_main'], "")
            return
        try:
            # Calculate sample indices based on current time and window size
            current_sample_index = int(self.song_time * self.sample_rate)
            window_samples = int(self.osc_window_seconds * self.sample_rate)
            if window_samples <= 0: window_samples = max(100, int(0.02 * self.sample_rate)) # Fallback window size

            # Ensure indices are within bounds of the raw data array
            start_index = max(0, current_sample_index)
            end_index = min(len(self.raw_sample_data), start_index + window_samples)
            # Adjust start index if end index hit the boundary, to maintain window size
            start_index = max(0, end_index - window_samples)

            sample_slice = self.raw_sample_data[start_index:end_index]

            if len(sample_slice) > 0:
                ax.clear() # Clear previous plot
                self._configure_axes(ax, fig, theme['plot_osc_main'], theme['plot_bg']) # Reapply theme styling (bg, spines)
                ax.set_ylim(-1.1, 1.1) # Ensure y-limits are correct
                x_osc = np.arange(len(sample_slice)) # X-axis for the slice
                ax.plot(x_osc, sample_slice, color=theme['plot_osc_main'], linewidth=0.8) # Draw with theme color
                ax.set_xlim(0, len(sample_slice) - 1 if len(sample_slice) > 1 else 1) # Set x-limits to fit slice
                fig.canvas.draw_idle() # Redraw the plot
            else:
                 # If the slice is empty, clear the plot
                 if len(ax.lines) > 0: self.draw_initial_placeholder(ax, fig, theme['plot_osc_main'], "")
        except Exception as e: print(f"Error updating oscilloscope: {e}")


    # --- Time Update Thread ---
    def update_song_position(self):
        """[Main Thread] Syncs UI with playback time. Scheduled by background thread."""
        # Skip UI updates if user is interacting with slider or waveform
        if self.slider_active or self.waveform_dragging: return

        if self.playing_state and not self.paused:
             try:
                 # Check mixer is initialized and music is actually playing
                 if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                     current_pos_ms = pygame.mixer.music.get_pos()
                     if current_pos_ms != -1: # -1 indicates an error or not playing
                         current_time_sec = current_pos_ms / 1000.0
                         # Update internal time state, ensuring it doesn't exceed song length much
                         self.song_time = min(current_time_sec, self.song_length + 0.1) if self.song_length > 0 else current_time_sec
                         # Update UI elements if they exist
                         if self.song_slider and self.song_slider.winfo_exists():
                             self.song_slider.set(self.song_time)
                         if self.current_time_label and self.current_time_label.winfo_exists():
                             mins, secs = divmod(int(self.song_time), 60); self.time_elapsed = f"{mins:02d}:{secs:02d}"
                             self.current_time_label.configure(text=self.time_elapsed)

                         pos_ratio = np.clip(self.song_time / self.song_length, 0.0, 1.0) if self.song_length > 0 else 0
                         self.draw_waveform_position_indicator(pos_ratio)
                         # Ensure plots redraw after potential indicator update
                         if self.fig_wave and self.fig_wave.canvas: self.fig_wave.canvas.draw_idle()
                         self.update_oscilloscope()
                 else:
                     # Music not busy, might have ended. Schedule end check.
                     if self.root.winfo_exists():
                         self.root.after(10, self.check_music_end_on_main_thread)

             except pygame.error as e: print(f"Pygame error in update: {e}"); self.has_error = True; self._update_display_title(); self.stop()
             except Exception as e:
                 # Catch other potential UI errors
                 if self.root.winfo_exists(): print(f"Error during UI update: {e}")
                 self.thread_running = False # Stop thread on error


    def start_update_thread(self):
        """Starts the background thread for updating time if not already running."""
        if not self.thread_running and self.playing_state and not self.paused:
            self.thread_running = True
            # Avoid starting multiple threads if one is already initializing
            if self.update_thread and self.update_thread.is_alive():
                 # print("Update thread already running.") # Can be noisy
                 return
            print("Starting update thread.")
            self.update_thread = threading.Thread(target=self.update_time, daemon=True)
            self.update_thread.start()
        elif not self.playing_state or self.paused:
             self.thread_running = False # Ensure flag is false if stopping/pausing


    def update_time(self):
        """[Background Thread] Periodically schedules UI updates on the main thread."""
        update_interval = 0.05 # Target interval for updates (e.g., 20 FPS)
        while self.thread_running:
            start_loop_time = time.monotonic()
            try:
                # Check if the root window still exists before scheduling
                if self.root.winfo_exists():
                    # Use after(0, ...) to schedule the update ASAP on the main thread
                    self.root.after(0, self.update_song_position)
                else:
                    # Root window closed, stop the thread
                    self.thread_running = False; break
            except Exception as e:
                # Catch errors during scheduling (e.g., tkinter errors)
                print(f"Update thread error: {e}"); self.thread_running = False; break

            # Calculate sleep time to maintain the desired update interval
            end_loop_time = time.monotonic(); time_taken = end_loop_time - start_loop_time
            sleep_time = max(0, update_interval - time_taken)
            time.sleep(sleep_time)

            # Check again if state changed (e.g., paused/stopped) while sleeping
            if not self.playing_state or self.paused:
                self.thread_running = False
        # print("Update thread finished.") # Can be noisy


    def check_music_end_on_main_thread(self):
        """[Main Thread] Checks if music finished and schedules the next action."""
        # Only proceed if we thought we were playing
        if not self.playing_state or self.paused: return
        try:
            # Check if mixer is still initialized and music is NOT busy
            if pygame.mixer.get_init() and not pygame.mixer.music.get_busy():
                 print(f"Detected song end for: {os.path.basename(self.current_song)}")
                 # Update state: no longer playing/paused, thread should stop
                 self.playing_state = False; self.paused = False; self.thread_running = False
                 self.stopped_position = self.song_length # Mark as finished at the end

                 # Update UI to show end time and full slider
                 if self.song_length > 0:
                     self.song_slider.set(self.song_length)
                     mins, secs = divmod(int(self.song_length), 60)
                     self.current_time_label.configure(text=f"{mins:02d}:{secs:02d}")
                     self.draw_waveform_position_indicator(1.0)
                     if self.fig_wave and self.fig_wave.canvas: self.fig_wave.canvas.draw_idle() # Ensure draw
                 else: # Handle zero-length songs
                     self.song_slider.set(0); self.current_time_label.configure(text="00:00")
                     self.draw_waveform_position_indicator(0.0)
                     if self.fig_wave and self.fig_wave.canvas: self.fig_wave.canvas.draw_idle() # Ensure draw


                 # Clear oscilloscope
                 theme = self.themes[self.current_theme_name]
                 self.draw_initial_placeholder(self.ax_osc, self.fig_osc, theme['plot_osc_main'], "")

                 self._update_display_title() # Remove [PLAYING] prefix

                 # Schedule the actual next action (loop/next/etc.) after a short delay
                 # This allows the UI changes above to render first
                 self.root.after(50, self.handle_song_end_action)

            elif not pygame.mixer.get_init():
                 # Mixer likely quit unexpectedly
                 print("Mixer stopped unexpectedly during end check.")
                 self.stop() # Ensure player state is consistent

        except pygame.error as e: print(f"Pygame error during end check: {e}"); self.has_error=True; self._update_display_title(); self.stop()
        except Exception as e: print(f"Error during end check: {e}"); traceback.print_exc(); self.has_error=True; self._update_display_title(); self.stop()

    def handle_song_end_action(self):
        """[Main Thread] Performs the action after a song ends (loop/next/shuffle/stop)."""
        if self.loop_state == 2: # Loop One
             print("Looping current song."); self.song_slider.set(0); self.current_time_label.configure(text="00:00"); self.play_music()
        elif self.loop_state == 1: # Loop All
             print("Looping all - playing next."); self.next_song(auto_advance=True)
        elif self.shuffle_state: # Mix
             print("Mix on - playing random."); self.play_random_song(auto_advance=True)
        else: # No Loop, No Mix - Check if end of playlist
             if self.current_song_index >= len(self.songs_list) - 1:
                 print("End of tracklist reached.");
                 # Don't call self.stop() again, just update UI for stopped state at beginning
                 self.current_song_index = 0 # Reset index conceptually
                 if self.songs_list: self.select_song(self.current_song_index) # Select first song
                 self.song_slider.set(0); self.current_time_label.configure(text="00:00"); self.draw_waveform_position_indicator(0)
                 if self.fig_wave and self.fig_wave.canvas: self.fig_wave.canvas.draw_idle() # Draw indicator update
                 theme = self.themes[self.current_theme_name]
                 self.draw_initial_placeholder(self.ax_osc, self.fig_osc, theme['plot_osc_main'],"")
                 # Keep title as the last song played, but remove prefix
                 last_song_name = os.path.basename(self.current_song) if self.current_song else "TRACKLIST END"
                 self._update_display_title(base_title=last_song_name)
             else:
                 # Not end of playlist, play next song
                 print("Playing next song in sequence."); self.next_song(auto_advance=True)


    def play_random_song(self, auto_advance=False):
        """Plays a random song from the tracklist, avoiding immediate repeat."""
        if not self.songs_list: self.stop(); return # Cannot play if list is empty

        if not auto_advance: self.stop() # Stop manually if not auto-advancing
        else:
            # If auto-advancing, just update state
            self.playing_state = False; self.paused = False; self.thread_running = False
            self.abort_waveform_generation(); self.stopped_position = 0.0; print("Auto-advancing to random song.")

        if len(self.songs_list) > 1:
             # Create a list of possible indices excluding the current one
             possible_indices = [i for i in range(len(self.songs_list)) if i != self.current_song_index]
             self.current_song_index = random.choice(possible_indices) # Pick randomly from the rest
        elif len(self.songs_list) == 1:
             self.current_song_index = 0 # Only one song, play it
        else:
             self.clear_playlist(); return # Should not happen if check at start passed

        self.play_music() # Play the selected random song

    def abort_waveform_generation(self):
        """Signals the background waveform thread to stop."""
        if self.waveform_thread and self.waveform_thread.is_alive():
            if not self.waveform_abort_flag.is_set():
                 print(f"Signalling waveform thread to abort...")
                 self.waveform_abort_flag.set()
                 # If the UI currently shows generating, update it
                 if self.is_generating_waveform:
                      self.is_generating_waveform = False
                      if "[GENERATING...]" in self.song_title_var.get():
                           self._update_display_title() # Remove generating message

    def on_closing(self):
        """Handles cleanup when the application window is closed."""
        print("Closing application...");
        self.thread_running = False; self.abort_waveform_generation()
        try:
            if pygame.mixer.get_init(): # Check if mixer is initialized before quitting
                 pygame.mixer.music.stop(); pygame.mixer.quit(); print("Pygame stopped.")
        except Exception as e: print(f"Error quitting pygame: {e}")
        # Close matplotlib figures gracefully
        try: plt.close(self.fig_wave)
        except Exception as e: print(f"Error closing wave fig: {e}")
        try: plt.close(self.fig_osc)
        except Exception as e: print(f"Error closing osc fig: {e}")
        # Destroy the main window
        if self.root: self.root.destroy()
        print("Application closed.")

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