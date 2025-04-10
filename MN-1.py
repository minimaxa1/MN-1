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

# --- Appearance Configuration ---
# You might need to install pydub: pip install pydub
# You MUST have ffmpeg installed and accessible in your system's PATH
# for pydub to work with MP3 and other formats. Download from: https://ffmpeg.org/download.html

# Define colors for the minimal theme
COLOR_BLACK = "#000000"
COLOR_WHITE = "#FFFFFF"
COLOR_DEEP_RED = "#8B0000" # Deep Red
COLOR_SILVER = "#C0C0C0" # Silver color

# --- Main Music Player Class ---
class MN1MusicPlayer:
    def __init__(self, root):
        # Initialize the main window
        self.root = root
        self.root.title("MN-1")
        # Adjusted height for smaller visual elements
        self.root.geometry("800x650")
        self.root.configure(fg_color=COLOR_BLACK)
        self.root.resizable(True, True)

        # Initialize pygame mixer
        try:
            pygame.mixer.init()
            print("Pygame mixer initialized successfully.")
        except pygame.error as e:
            print(f"FATAL: Error initializing pygame mixer: {e}")
            # Show error message to user if possible
            try:
                import tkinter.messagebox
                tkinter.messagebox.showerror("Pygame Error", f"Could not initialize audio output.\nError: {e}\n\nThe application might not play sound.")
            except: pass # Ignore if messagebox fails

        # Global variables for player state
        self.current_song = ""
        self.songs_list = []
        self.current_song_index = 0
        self.playing_state = False # True if actively playing sound
        self.paused = False      # True if paused mid-playback
        self.shuffle_state = False
        self.loop_state = 0      # 0: Off, 1: Loop All, 2: Loop One
        self.muted = False
        self.previous_volume = 0.5
        self.stopped_position = 0.0 # Time in seconds where playback was last stopped/finished
        self.slider_active = False   # True if user is dragging the song slider
        self.waveform_dragging = False # True if user is dragging on the waveform

        # Set default volume
        try: pygame.mixer.music.set_volume(0.5)
        except Exception as e: print(f"Warning: Could not set initial volume: {e}")

        # Create fonts
        self.title_font = ("SF Mono", 16, "bold") # Slightly smaller title
        self.normal_font = ("SF Mono", 11)       # Slightly smaller normal text
        self.button_font = ("SF Mono", 13, "bold") # Slightly smaller button text

        # --- Matplotlib Setup ---
        # Reduce default figure size for smaller canvases
        self.fig_wave, self.ax_wave = plt.subplots(figsize=(5, 1.5)) # Smaller figsize
        self._configure_axes(self.ax_wave, self.fig_wave, COLOR_WHITE)
        self.mpl_canvas_widget_wave = None
        self.position_indicator_line_wave = None

        self.fig_osc, self.ax_osc = plt.subplots(figsize=(5, 0.8)) # Even smaller figsize
        self._configure_axes(self.ax_osc, self.fig_osc, COLOR_DEEP_RED)
        self.mpl_canvas_widget_osc = None
        self.ax_osc.set_ylim(-1.1, 1.1) # Keep y-limits for normalized data

        # --- Waveform/Sample Data Control ---
        self.waveform_peak_data = None # Stores downsampled peak data for static waveform
        self.raw_sample_data = None    # Stores downsampled raw audio data for oscilloscope
        self.sample_rate = None        # Sample rate of the raw_sample_data
        self.waveform_thread = None    # Thread object for background generation
        self.waveform_abort_flag = threading.Event() # Flag to signal thread abortion

        # --- Oscilloscope settings ---
        self.osc_window_seconds = 0.05 # Time window (in seconds) shown in oscilloscope
        self.osc_downsample_factor = 5 # Factor to downsample raw audio for performance

        # --- Time-related ---
        self.song_length = 0.0 # Duration of the current song in seconds
        self.song_time = 0.0   # Current playback position in seconds (driven by mixer or user interaction)
        self.time_elapsed = "00:00" # Formatted string for current time label
        self.total_time = "00:00"   # Formatted string for total duration label

        # --- Threading ---
        self.update_thread = None # Thread object for time/UI updates
        self.thread_running = False # Flag to control the update thread loop

        # --- Create UI Elements ---
        self.create_frames()
        self.create_player_area()
        self.create_waveform_display()
        self.create_oscilloscope_display()
        self.create_controls()
        self.create_playlist_area()

        # Initial state for visuals
        self.draw_initial_placeholder(self.ax_wave, self.fig_wave, COLOR_WHITE, "LOAD A SONG")
        self.draw_initial_placeholder(self.ax_osc, self.fig_osc, COLOR_DEEP_RED, "")

        # Bind window close event to custom cleanup function
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        print("UI Initialized.")

    def _configure_axes(self, ax, fig, spine_color):
        """Helper to configure matplotlib axes appearance."""
        fig.patch.set_facecolor(COLOR_BLACK)
        ax.set_facecolor(COLOR_BLACK)
        ax.tick_params(axis='both', colors=spine_color, labelsize=0, length=0) # Hide ticks
        for spine in ax.spines.values():
            spine.set_color(spine_color) # Set border color
        ax.margins(0); ax.set_yticks([]); ax.set_xticks([]) # Remove margins and axis labels
        # Adjust layout padding for potentially smaller figures
        try: fig.tight_layout(pad=0.05) # Reduced padding
        except Exception: # Fallback if tight_layout fails
             print("Warning: tight_layout failed."); fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)

    def create_frames(self):
        """Create the main frames for layout."""
        self.player_frame = ctk.CTkFrame(self.root, fg_color=COLOR_BLACK, corner_radius=0)
        self.player_frame.pack(pady=5, padx=10, fill="both", expand=True) # Reduced pady

        self.left_frame = ctk.CTkFrame(self.player_frame, fg_color=COLOR_BLACK, width=500, corner_radius=0)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5)) # Add padding between left/right

        self.right_frame = ctk.CTkFrame(self.player_frame, fg_color=COLOR_BLACK, width=300, corner_radius=0)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Frame for playback controls at the bottom of the left side
        self.controls_frame = ctk.CTkFrame(self.left_frame, fg_color=COLOR_BLACK, height=80, corner_radius=0)
        self.controls_frame.pack(side="bottom", fill="x", pady=(5,5)) # Reduced pady

        # Frame for visuals (info, waveform, oscilloscope, slider) at the top of the left side
        self.visual_frame = ctk.CTkFrame(self.left_frame, fg_color=COLOR_BLACK, corner_radius=0)
        self.visual_frame.pack(side="top", fill="both", expand=True, pady=(0,5))

    def create_player_area(self):
        """Create widgets within the visual_frame (info, plots, slider)."""
        # --- Info Section (Top) ---
        self.info_frame = ctk.CTkFrame(self.visual_frame, fg_color=COLOR_BLACK, corner_radius=0)
        self.info_frame.pack(fill="x", pady=(0,0)) # No vertical padding

        self.song_title_var = ctk.StringVar(value="NO SONG LOADED")
        self.song_title_label = ctk.CTkLabel(self.info_frame, textvariable=self.song_title_var, font=self.title_font, fg_color=COLOR_BLACK, text_color=COLOR_WHITE, anchor="w")
        self.song_title_label.pack(fill="x", padx=10, pady=(0, 2)) # Pad below title

        self.status_var = ctk.StringVar(value="IDLE")
        self.status_label = ctk.CTkLabel(self.info_frame, textvariable=self.status_var, font=self.normal_font, fg_color=COLOR_BLACK, text_color=COLOR_WHITE, anchor="w")
        self.status_label.pack(fill="x", padx=10, pady=(0, 5)) # Pad below status

        # --- Waveform Section (Fixed, smaller height) ---
        WAVEFORM_HEIGHT = 70 # Fixed height for waveform plot area
        self.waveform_frame = ctk.CTkFrame(self.visual_frame, fg_color=COLOR_BLACK, corner_radius=0, height=WAVEFORM_HEIGHT)
        # Pack with fixed height, minimal padding below
        self.waveform_frame.pack(fill="x", expand=False, padx=10, pady=(0, 1), ipady=0) # expand=False, pady=(top, bottom)

        # --- Oscilloscope Section (Even smaller fixed height) ---
        OSCILLOSCOPE_HEIGHT = 35 # Fixed height for oscilloscope plot area
        self.oscilloscope_frame = ctk.CTkFrame(self.visual_frame, fg_color=COLOR_BLACK, corner_radius=0, height=OSCILLOSCOPE_HEIGHT)
        # Pack immediately after waveform, minimal padding above
        self.oscilloscope_frame.pack(fill="x", expand=False, padx=10, pady=(1, 5), ipady=0) # expand=False, pady=(top, bottom)

        # --- Invisible Spacer Frame (Takes remaining vertical space) ---
        # This pushes the slider section down if the window is tall
        self.spacer_frame = ctk.CTkFrame(self.visual_frame, fg_color=COLOR_BLACK, height=0)
        # Pack the spacer AFTER the oscilloscope
        self.spacer_frame.pack(fill="both", expand=True, pady=0, padx=0)

        # --- Slider Section (Bottom of visual area) ---
        self.slider_frame = ctk.CTkFrame(self.visual_frame, fg_color=COLOR_BLACK, corner_radius=0)
        self.slider_frame.pack(fill="x", pady=(0,5), padx=10) # Packed last in visual_frame

        self.song_slider = ctk.CTkSlider(self.slider_frame, from_=0, to=100, fg_color=COLOR_BLACK, button_color=COLOR_SILVER, button_hover_color=COLOR_SILVER, progress_color=COLOR_DEEP_RED, command=self.slide_song, variable=ctk.DoubleVar())
        self.song_slider.pack(fill="x", pady=5)
        # Bind mouse events for seeking
        self.song_slider.bind("<ButtonPress-1>", self.slider_start_scroll)
        self.song_slider.bind("<ButtonRelease-1>", self.slider_stop_scroll)

        # Frame for time labels below slider
        self.time_frame = ctk.CTkFrame(self.slider_frame, fg_color=COLOR_BLACK, corner_radius=0)
        self.time_frame.pack(fill="x")
        self.current_time_label = ctk.CTkLabel(self.time_frame, text="00:00", font=self.normal_font, fg_color=COLOR_BLACK, text_color=COLOR_WHITE)
        self.current_time_label.pack(side="left", padx=(0, 5))
        self.total_time_label = ctk.CTkLabel(self.time_frame, text="00:00", font=self.normal_font, fg_color=COLOR_BLACK, text_color=COLOR_WHITE)
        self.total_time_label.pack(side="right", padx=(5, 0))

    def create_waveform_display(self):
        """Create the Matplotlib canvas for the static waveform."""
        # Ensure the matplotlib canvas uses the pre-configured figure
        self.mpl_canvas_widget_wave = FigureCanvasTkAgg(self.fig_wave, master=self.waveform_frame)
        tk_widget = self.mpl_canvas_widget_wave.get_tk_widget()
        tk_widget.pack(fill="both", expand=True)
        tk_widget.configure(bg=COLOR_BLACK) # Set background explicitly
        # Delay initial draw slightly
        self.root.after(50, lambda: self.fig_wave.canvas.draw_idle())
        # Connect mouse events for seeking
        self.fig_wave.canvas.mpl_connect('button_press_event', self.on_waveform_press)
        self.fig_wave.canvas.mpl_connect('motion_notify_event', self.on_waveform_motion)
        tk_widget.bind('<ButtonRelease-1>', self.on_waveform_release)
        tk_widget.bind('<Leave>', self.on_waveform_leave) # Handle mouse leaving plot while dragging

    def create_oscilloscope_display(self):
        """Create the Matplotlib canvas for the oscilloscope."""
        # Ensure the matplotlib canvas uses the pre-configured figure
        self.mpl_canvas_widget_osc = FigureCanvasTkAgg(self.fig_osc, master=self.oscilloscope_frame)
        tk_widget_osc = self.mpl_canvas_widget_osc.get_tk_widget()
        tk_widget_osc.pack(fill="both", expand=True)
        tk_widget_osc.configure(bg=COLOR_BLACK) # Set background explicitly
        # Delay initial draw slightly
        self.root.after(50, lambda: self.fig_osc.canvas.draw_idle())

    def draw_initial_placeholder(self, ax, fig, border_color, message=""):
        """Draws a placeholder message on a Matplotlib plot area."""
        if not ax or not fig or not fig.canvas: return # Check if plot elements are valid
        try:
            ax.clear(); self._configure_axes(ax, fig, border_color)
            # Adjust font size for potentially smaller plots
            font_size = 7 if fig == self.fig_osc else 9 # Smaller font for smaller plots
            if message: ax.text(0.5, 0.5, message, ha='center', va='center', fontsize=font_size, color=COLOR_WHITE, transform=ax.transAxes, fontfamily='SF Mono')
            if ax == self.ax_osc: ax.set_ylim(-1.1, 1.1) # Ensure ylim is set for oscilloscope placeholder
            fig.canvas.draw_idle() # Redraw the canvas
            if ax == self.ax_wave: self.position_indicator_line_wave = None # Reset indicator reference
        except Exception as e: print(f"Error drawing placeholder: {e}")

    def create_controls(self):
        """Create playback control buttons and volume slider."""
        # Frame for main playback buttons (Prev, Play, Pause, Next)
        self.buttons_frame = ctk.CTkFrame(self.controls_frame, fg_color=COLOR_BLACK, corner_radius=0)
        self.buttons_frame.pack(pady=(5,0), anchor="center") # Center horizontally
        button_kwargs = {"font": self.button_font, "fg_color": COLOR_BLACK, "text_color": COLOR_WHITE, "hover_color": COLOR_DEEP_RED, "border_width": 0, "corner_radius": 0, "width": 35, "height": 28} # Slightly smaller buttons
        self.prev_button = ctk.CTkButton(self.buttons_frame, text="◄◄", command=self.previous_song, **button_kwargs); self.prev_button.grid(row=0, column=0, padx=4)
        self.play_button = ctk.CTkButton(self.buttons_frame, text="▶", command=self.play, **button_kwargs); self.play_button.grid(row=0, column=1, padx=4)
        self.pause_button = ctk.CTkButton(self.buttons_frame, text="II", command=self.pause, **button_kwargs); self.pause_button.grid(row=0, column=2, padx=4)
        self.next_button = ctk.CTkButton(self.buttons_frame, text="►►", command=self.next_song, **button_kwargs); self.next_button.grid(row=0, column=3, padx=4)

        # Frame for extra controls (Shuffle, Loop, Volume)
        self.extra_frame = ctk.CTkFrame(self.controls_frame, fg_color=COLOR_BLACK, corner_radius=0)
        self.extra_frame.pack(pady=(2,5), anchor="center") # Center horizontally
        extra_button_kwargs = {"font": self.normal_font, "fg_color": COLOR_BLACK, "text_color": COLOR_WHITE, "hover_color": COLOR_DEEP_RED, "border_width": 0, "corner_radius": 0, "width": 65, "height": 25} # Smaller extra buttons
        self.shuffle_button = ctk.CTkButton(self.extra_frame, text="SHUFFLE", command=self.toggle_shuffle, **extra_button_kwargs); self.shuffle_button.grid(row=0, column=0, padx=3)
        self.loop_button = ctk.CTkButton(self.extra_frame, text="LOOP", command=self.toggle_loop, **extra_button_kwargs); self.loop_button.grid(row=0, column=1, padx=3)
        self.volume_button = ctk.CTkButton(self.extra_frame, text="VOL", command=self.toggle_mute, **extra_button_kwargs); self.volume_button.grid(row=0, column=2, padx=3)
        self.volume_slider = ctk.CTkSlider(self.extra_frame, from_=0, to=1, number_of_steps=100, fg_color=COLOR_BLACK, button_color=COLOR_SILVER, button_hover_color=COLOR_SILVER, progress_color=COLOR_DEEP_RED, command=self.volume_adjust, width=90, height=18); # Explicit size
        self.volume_slider.set(0.5); self.volume_slider.grid(row=0, column=3, padx=3, pady=(0,3)) # Pad slightly below slider

        # Simple text label (optional branding)
        self.mn1_label = ctk.CTkLabel(self.controls_frame, text="MN-1", font=("SF Mono", 9), fg_color=COLOR_BLACK, text_color=COLOR_SILVER)
        self.mn1_label.place(relx=0.01, rely=0.98, anchor="sw") # Place at bottom-left of controls frame

    def create_playlist_area(self):
        """Create the playlist display and management buttons."""
        self.playlist_label = ctk.CTkLabel(self.right_frame, text="PLAYLIST", font=self.title_font, fg_color=COLOR_BLACK, text_color=COLOR_WHITE)
        self.playlist_label.pack(pady=5)

        # Frame to contain the scrollable playlist
        self.playlist_frame = ctk.CTkFrame(self.right_frame, fg_color=COLOR_BLACK, corner_radius=0)
        self.playlist_frame.pack(fill="both", expand=True, padx=5, pady=0) # Remove bottom padding

        # Scrollable frame for playlist entries
        self.playlist_scrollable = ctk.CTkScrollableFrame(self.playlist_frame, fg_color=COLOR_BLACK, label_fg_color=COLOR_BLACK, label_text_color=COLOR_BLACK, scrollbar_button_color=COLOR_DEEP_RED, scrollbar_button_hover_color=COLOR_WHITE)
        self.playlist_scrollable.pack(fill="both", expand=True)
        self.playlist_entries = [] # List to hold playlist entry dicts {frame, label, selected, index}

        # Frame for playlist action buttons (Add, Remove, Clear)
        self.playlist_buttons_frame = ctk.CTkFrame(self.right_frame, fg_color=COLOR_BLACK, corner_radius=0)
        self.playlist_buttons_frame.pack(fill="x", pady=(5,10)) # Add padding top/bottom
        playlist_button_kwargs = {"font": self.normal_font, "fg_color": COLOR_BLACK, "text_color": COLOR_WHITE, "hover_color": COLOR_DEEP_RED, "border_width": 0, "corner_radius": 0, "width": 70, "height": 25} # Smaller playlist buttons
        self.add_button = ctk.CTkButton(self.playlist_buttons_frame, text="ADD", command=self.add_songs, **playlist_button_kwargs); self.add_button.pack(side="left", padx=5, expand=True) # Let buttons expand equally
        self.remove_button = ctk.CTkButton(self.playlist_buttons_frame, text="REMOVE", command=self.remove_song, **playlist_button_kwargs); self.remove_button.pack(side="left", padx=5, expand=True)
        self.clear_button = ctk.CTkButton(self.playlist_buttons_frame, text="CLEAR", command=self.clear_playlist, **playlist_button_kwargs); self.clear_button.pack(side="left", padx=5, expand=True)

    # --- Playlist Management Methods ---
    def add_songs(self):
        """Opens file dialog to add songs to the playlist."""
        songs = filedialog.askopenfilenames(title="Select Audio Files", filetypes=(("Audio Files", "*.mp3 *.flac"), ("MP3 Files", "*.mp3"), ("FLAC Files", "*.flac"), ("All Files", "*.*")))
        added_count = 0
        if not songs: return # No files selected

        for song_path in songs:
            if os.path.exists(song_path):
                 try:
                    file_ext = os.path.splitext(song_path)[1].lower()
                    # Basic validation with mutagen - ensures file is readable audio
                    if file_ext == ".mp3": MP3(song_path)
                    elif file_ext == ".flac": FLAC_MUTAGEN(song_path)
                    else: # Skip unsupported types for now
                        print(f"Skipping unsupported file type: {os.path.basename(song_path)}")
                        continue

                    song_name = os.path.basename(song_path)
                    # Prevent duplicates by checking full path
                    if song_path not in self.songs_list:
                        self.add_song_to_playlist(song_name, song_path)
                        self.songs_list.append(song_path)
                        added_count += 1
                    else: print(f"Song already in playlist: {song_name}")
                 except Exception as e: print(f"Skipping invalid/unreadable file: {os.path.basename(song_path)} - Error: {e}")
            else: print(f"Skipping non-existent file: {song_path}")

        # Update status message based on outcome
        if added_count > 0: self.status_var.set(f"{added_count} TRACK(S) ADDED")
        elif added_count == 0 and songs: self.status_var.set("NO NEW TRACKS ADDED") # Files selected but were duplicates/invalid

    def add_song_to_playlist(self, song_name, song_path):
        """Adds a single song entry to the playlist UI."""
        index = len(self.playlist_entries)
        # Create a frame for each entry
        song_frame = ctk.CTkFrame(self.playlist_scrollable, fg_color=COLOR_BLACK, corner_radius=0)
        song_frame.pack(fill="x", pady=1, ipady=1) # Minimal padding

        # Create the label within the frame
        song_label = ctk.CTkLabel(song_frame, text=song_name, font=self.normal_font, fg_color=COLOR_BLACK, text_color=COLOR_WHITE, anchor="w", justify="left", cursor="hand2")
        song_label.pack(fill="x", padx=5)

        # Bind mouse events using lambda to capture the correct index at creation time
        song_label.bind("<Button-1>", lambda e, idx=index: self.select_song(idx))
        song_label.bind("<Double-Button-1>", lambda e, idx=index: self.play_selected_song_by_index(idx))

        # Store references to the UI elements and state
        self.playlist_entries.append({"frame": song_frame, "label": song_label, "selected": False, "index": index})

    def select_song(self, index):
        """Highlights the selected song in the playlist UI."""
        # Check index bounds defensively
        if not (0 <= index < len(self.playlist_entries)):
            print(f"Warning: Invalid index {index} passed to select_song")
            return

        # Iterate through all playlist entries to update their appearance
        for i, entry in enumerate(self.playlist_entries):
             is_selected = (i == index)
             new_fg = COLOR_DEEP_RED if is_selected else COLOR_BLACK # Highlight color or background
             # Update frame and label background/text colors
             entry["frame"].configure(fg_color=new_fg)
             entry["label"].configure(fg_color=new_fg, text_color=COLOR_WHITE) # Keep text white for contrast
             entry["selected"] = is_selected # Update selected state

    def play_selected_song_by_index(self, index):
        """Plays the song at the specified index."""
        if 0 <= index < len(self.songs_list):
             self.abort_waveform_generation() # Stop any ongoing generation first
             self.current_song_index = index
             self.select_song(index) # Visually select the song
             self.play_music() # Call the main playback function
        else: print(f"Warning: play_selected_song_by_index index {index} out of range."); self.status_var.set("INVALID TRACK INDEX")

    def play_selected_song(self, event=None):
        """Plays the currently selected song, or the first if none selected."""
        selected_index = -1
        for index, entry in enumerate(self.playlist_entries):
            if entry["selected"]: selected_index = index; break

        if selected_index != -1: # Play the found selected song
            self.play_selected_song_by_index(selected_index)
        elif self.playlist_entries: # If no song is selected, play the first one
             print("No song selected, playing first song.")
             self.play_selected_song_by_index(0)
        else: # Playlist is empty
             self.status_var.set("PLAYLIST EMPTY")

    def remove_song(self):
        """Removes the currently selected song from the playlist."""
        removed_index = -1
        is_current_song_removed = False
        # Find the selected song index
        for i, entry in enumerate(self.playlist_entries):
            if entry["selected"]: removed_index = i; break

        if removed_index == -1: self.status_var.set("NO TRACK SELECTED"); return # Nothing selected to remove

        # Check if the song being removed is the one currently loaded/playing/paused
        # Check both index and the actual song path for robustness
        if removed_index == self.current_song_index and self.current_song and self.current_song == self.songs_list[removed_index]:
             is_current_song_removed = True

        # --- Remove from UI and data structures ---
        self.playlist_entries[removed_index]["frame"].destroy() # Remove frame from UI
        self.playlist_entries.pop(removed_index) # Remove entry dict from list
        removed_song_path = self.songs_list.pop(removed_index) # Remove path from list
        print(f"Removed: {os.path.basename(removed_song_path)}")

        # --- Re-index remaining entries and re-bind events ---
        # Necessary because indices in the list shift after pop()
        for i in range(removed_index, len(self.playlist_entries)):
            entry = self.playlist_entries[i]
            entry["index"] = i # Update the stored index
            # Unbind old lambdas (important!) and re-bind with the new correct index
            entry["label"].unbind("<Button-1>")
            entry["label"].unbind("<Double-Button-1>")
            entry["label"].bind("<Button-1>", lambda e, idx=i: self.select_song(idx))
            entry["label"].bind("<Double-Button-1>", lambda e, idx=i: self.play_selected_song_by_index(idx))

        # --- Handle playback state if the active song was removed ---
        if is_current_song_removed:
            self.stop() # Stop playback immediately
            self.current_song = "" # Clear current song info
            self.song_title_var.set("NO SONG LOADED")
            # Clear visuals
            self.draw_initial_placeholder(self.ax_wave, self.fig_wave, COLOR_WHITE, "TRACK REMOVED")
            self.draw_initial_placeholder(self.ax_osc, self.fig_osc, COLOR_DEEP_RED, "")
            self.raw_sample_data = None; self.waveform_peak_data = None; self.sample_rate = None
            self.song_length = 0; self.total_time_label.configure(text="00:00"); self.current_time_label.configure(text="00:00"); self.song_slider.set(0); self.song_slider.configure(to=100)

        # --- Adjust current_song_index if necessary ---
        if len(self.songs_list) == 0: # Playlist is now empty
            self.current_song_index = 0 # Reset index
            # If playlist became empty now (and current wasn't just removed), clear visuals
            if not is_current_song_removed:
                 self.song_title_var.set("NO SONG LOADED"); self.draw_initial_placeholder(self.ax_wave, self.fig_wave, COLOR_WHITE, "PLAYLIST EMPTY"); self.draw_initial_placeholder(self.ax_osc, self.fig_osc, COLOR_DEEP_RED, "")
                 self.raw_sample_data = None; self.waveform_peak_data = None; self.sample_rate = None; self.song_length = 0; self.total_time_label.configure(text="00:00"); self.current_time_label.configure(text="00:00"); self.song_slider.set(0); self.song_slider.configure(to=100)
        elif removed_index < self.current_song_index:
             self.current_song_index -= 1 # Adjust index down if removed item was before current
        elif removed_index == self.current_song_index and not is_current_song_removed:
             # Item at current index removed, but it wasn't the active song
             # Keep index same unless it was the very last item
             self.current_song_index = min(removed_index, len(self.songs_list) - 1)

        # Reselect the (potentially new) current song visually if list not empty
        if not is_current_song_removed and self.songs_list:
            self.select_song(self.current_song_index)

        self.status_var.set("TRACK REMOVED")

    def clear_playlist(self):
        """Removes all songs from the playlist and stops playback."""
        self.stop(); # Stop playback first
        # Destroy UI elements for each entry
        for entry in self.playlist_entries: entry["frame"].destroy()
        # Clear data structures
        self.playlist_entries.clear(); self.songs_list.clear(); self.current_song_index = 0; self.current_song = ""
        # Reset UI display to initial state
        self.song_title_var.set("NO SONG LOADED")
        self.waveform_peak_data = None; self.raw_sample_data = None; self.sample_rate = None
        self.draw_initial_placeholder(self.ax_wave, self.fig_wave, COLOR_WHITE, "PLAYLIST CLEARED")
        self.draw_initial_placeholder(self.ax_osc, self.fig_osc, COLOR_DEEP_RED, "")
        self.status_var.set("PLAYLIST CLEARED")
        self.total_time_label.configure(text="00:00"); self.current_time_label.configure(text="00:00"); self.song_slider.set(0); self.song_slider.configure(to=100)
        self.song_length = 0

    # --- Playback Control Methods ---
    def play(self):
        """Handles the Play button action: plays selected, resumes paused, or resumes stopped."""
        if not self.songs_list: self.status_var.set("PLAYLIST EMPTY"); return # Nothing to play

        if self.paused: # --- Unpause ---
            self.play_button.configure(fg_color=COLOR_DEEP_RED); self.root.after(100, lambda: self.play_button.configure(fg_color=COLOR_BLACK)) # Button flash
            try:
                pygame.mixer.music.unpause()
                self.paused = False; self.playing_state = True # Update state
                self.status_var.set("PLAYING")
                self.start_update_thread() # Restart timer updates
            except pygame.error as e: print(f"Pygame error during unpause: {e}")

        elif not self.playing_state: # --- Play new or resume stopped ---
            song_to_play_index = -1; selected_idx = -1
            # 1. Check if a song is selected in the playlist
            for i, entry in enumerate(self.playlist_entries):
                 if entry["selected"]: selected_idx = i; break

            # 2. Determine which index to actually play
            if selected_idx != -1 and 0 <= selected_idx < len(self.songs_list):
                song_to_play_index = selected_idx # Play selected if valid
            elif self.current_song and self.stopped_position > 0 and 0 <= self.current_song_index < len(self.songs_list) and self.songs_list[self.current_song_index] == self.current_song:
                 # If nothing selected, resume the previously stopped song if possible
                 song_to_play_index = self.current_song_index
            elif self.songs_list: # Otherwise, play the first song
                song_to_play_index = 0

            # 3. Proceed if a valid index was found
            if song_to_play_index != -1:
                # Check if we are resuming the *exact same* song that was stopped
                is_resuming = (song_to_play_index == self.current_song_index and
                               self.stopped_position > 0 and
                               self.current_song == self.songs_list[song_to_play_index])

                # Update state *before* loading/playing
                self.current_song_index = song_to_play_index
                self.current_song = self.songs_list[self.current_song_index]
                self.select_song(self.current_song_index) # Visually select it

                try:
                    self.play_button.configure(fg_color=COLOR_DEEP_RED); self.root.after(100, lambda: self.play_button.configure(fg_color=COLOR_BLACK)) # Button flash
                    self.abort_waveform_generation() # Abort any pending generation

                    pygame.mixer.music.load(self.current_song)
                    start_pos = self.stopped_position if is_resuming else 0.0
                    pygame.mixer.music.play(start=start_pos) # Play from start_pos
                    if not is_resuming: self.stopped_position = 0.0 # Reset stopped pos if not resuming

                    # Update state *after* successful play command
                    self.playing_state = True
                    self.paused = False
                    self.status_var.set("PLAYING")
                    self.update_song_info() # Update labels, slider range
                    self.start_update_thread() # Start time updates
                    self.trigger_waveform_generation() # Start background waveform generation

                except pygame.error as e: print(f"Pygame Error during play: {e}"); self.status_var.set(f"ERROR: Cannot play track"); self.playing_state = False; self.paused = False; self.current_song = ""
                except Exception as e: print(f"Error during play setup: {e}"); traceback.print_exc(); self.status_var.set(f"ERROR: {type(e).__name__}"); self.playing_state = False; self.paused = False; self.current_song = ""
            else: # Should be rare now
                self.status_var.set("PLAYLIST EMPTY?")

    def play_music(self):
        """
        Core function to load and play a song from the beginning.
        Called by next/prev, double-click, shuffle, loop-one.
        """
        # Validate state
        if not self.songs_list or not (0 <= self.current_song_index < len(self.songs_list)):
            self.status_var.set("INVALID SELECTION"); print("play_music: Invalid state."); return

        self.current_song = self.songs_list[self.current_song_index]
        self.stopped_position = 0.0 # Always start from beginning for this function

        try:
            self.abort_waveform_generation() # Abort previous generation if any
            print(f"play_music: Loading {os.path.basename(self.current_song)}")

            # Stop previous playback completely before loading new track
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.play() # Play from start (default)

            # Update state after successful play command
            self.playing_state = True
            self.paused = False
            self.update_song_info() # Update title, duration, slider range, etc.
            self.select_song(self.current_song_index) # Visually select in playlist
            self.status_var.set("PLAYING")

            # Reset visuals before generation starts
            self.draw_initial_placeholder(self.ax_wave, self.fig_wave, COLOR_WHITE,"GENERATING...")
            self.draw_initial_placeholder(self.ax_osc, self.fig_osc, COLOR_DEEP_RED,"")

            # Start background generation and time updates
            self.trigger_waveform_generation()
            self.start_update_thread()

        except pygame.error as e: print(f"Pygame Error during play_music load/play: {e}"); self.status_var.set(f"ERROR: Cannot load/play"); self.playing_state = False; self.paused = False; self.current_song = ""; self.draw_initial_placeholder(self.ax_wave, self.fig_wave, COLOR_WHITE,"LOAD ERROR"); self.draw_initial_placeholder(self.ax_osc, self.fig_osc, COLOR_DEEP_RED,"")
        except Exception as e: print(f"Error during play_music setup: {e}"); traceback.print_exc(); self.status_var.set(f"ERROR: {type(e).__name__}"); self.playing_state = False; self.paused = False; self.current_song = ""; self.draw_initial_placeholder(self.ax_wave, self.fig_wave, COLOR_WHITE,"ERROR"); self.draw_initial_placeholder(self.ax_osc, self.fig_osc, COLOR_DEEP_RED,"")

    def pause(self):
        """Handles the Pause button action: pauses or unpauses playback."""
        if self.playing_state and not self.paused: # --- Pause ---
            self.pause_button.configure(fg_color=COLOR_DEEP_RED); self.root.after(100, lambda: self.pause_button.configure(fg_color=COLOR_BLACK)) # Button flash
            try:
                pygame.mixer.music.pause()
                self.paused = True; self.playing_state = False # Logically, not actively playing
                self.status_var.set("PAUSED")
                # Stop the update thread when paused
                self.thread_running = False
                print("Playback Paused.")
            except pygame.error as e: print(f"Pygame error during pause: {e}")

        elif self.paused: # --- Unpause --- (Functionally same as play() when paused)
            self.play() # Delegate to play function which handles unpausing

    def stop(self):
        """Stops playback completely and records the position."""
        if self.playing_state or self.paused: # Only act if playing or paused
            try:
                # Get position *before* stopping, using self.song_time as the reliable source
                # get_pos() can be inaccurate after pause/resume or near end
                self.stopped_position = self.song_time
                print(f"Stop called, recording position from song_time: {self.song_time:.2f}s")
                pygame.mixer.music.stop()
            except pygame.error as e: print(f"Pygame error during stop: {e}")
            finally:
                # Update state regardless of pygame errors
                was_playing_or_paused = self.playing_state or self.paused
                self.playing_state = False
                self.paused = False
                self.status_var.set("STOPPED")
                self.thread_running = False # Ensure update thread stops
                self.abort_waveform_generation() # Abort any pending generation

                # Update UI to reflect stopped position only if it was playing/paused
                if was_playing_or_paused:
                    self.song_slider.set(self.stopped_position)
                    mins, secs = divmod(int(self.stopped_position), 60)
                    self.current_time_label.configure(text=f"{mins:02d}:{secs:02d}")

                    # Update waveform indicator to the stopped position
                    if self.song_length > 0:
                        pos_ratio = np.clip(self.stopped_position / self.song_length, 0.0, 1.0)
                        self.draw_waveform_position_indicator(pos_ratio)
                    else:
                        self.draw_waveform_position_indicator(0)

                    # Clear oscilloscope plot
                    self.draw_initial_placeholder(self.ax_osc, self.fig_osc, COLOR_DEEP_RED,"")
                    print(f"Stopped. Position recorded: {self.stopped_position:.2f}s")
        else:
             # print("Stop called but not playing or paused.") # Reduce console noise
             # Ensure thread isn't running if somehow stuck
             self.thread_running = False

    def previous_song(self):
        """Stops current song and plays the previous one in the list."""
        if not self.songs_list: self.status_var.set("PLAYLIST EMPTY"); return
        original_index = self.current_song_index
        self.stop() # Stop current song playback before switching
        if len(self.songs_list) > 0:
            # Calculate previous index with wrap-around
            self.current_song_index = (original_index - 1 + len(self.songs_list)) % len(self.songs_list)
            self.play_music() # play_music starts the new song from beginning
        # else: # Should not happen if first check passes
            # self.clear_playlist()

    def next_song(self, auto_advance=False):
        """Plays the next song in the list, stopping current if manual."""
        if not self.songs_list: self.status_var.set("PLAYLIST EMPTY"); return
        original_index = self.current_song_index

        # Stop or prepare state based on context
        if not auto_advance:
            self.stop() # Manual next: Stop playback first
        else:
            # Auto advance: Reset state cleanly without calling stop() UI updates
            self.playing_state = False
            self.paused = False
            self.thread_running = False # Stop updates
            self.abort_waveform_generation()
            self.stopped_position = 0.0 # Ensure next song starts at 0
            print("Auto-advancing to next song.")

        if len(self.songs_list) > 0:
             # Calculate next index with wrap-around
            self.current_song_index = (original_index + 1) % len(self.songs_list)
            self.play_music() # play_music starts the new song from beginning
        # else: # Should not happen if first check passes
             # self.clear_playlist()

    # --- Volume/Shuffle/Loop ---
    def volume_adjust(self, value):
        """Callback for volume slider change."""
        volume = float(value)
        try: pygame.mixer.music.set_volume(volume)
        except Exception as e: print(f"Warning: Could not set volume: {e}"); return

        # Update mute button state based on slider value
        if volume > 0 and self.muted: # Unmuting via slider
             self.muted = False; self.volume_button.configure(text="VOL", text_color=COLOR_WHITE)
        elif volume == 0 and not self.muted: # Muting via slider
             self.muted = True; self.volume_button.configure(text="MUTED", text_color=COLOR_DEEP_RED)
        # Store the last non-zero volume for unmuting
        if volume > 0: self.previous_volume = volume

    def toggle_mute(self):
        """Toggles mute state on/off."""
        if self.muted: # --- Unmute ---
             try:
                 pygame.mixer.music.set_volume(self.previous_volume)
                 self.volume_slider.set(self.previous_volume)
                 self.muted = False
                 self.volume_button.configure(text="VOL", text_color=COLOR_WHITE)
             except Exception as e: print(f"Warning: Could not set volume on unmute: {e}")
        else: # --- Mute ---
             try:
                 # Store current volume before muting if > 0
                 current_vol = pygame.mixer.music.get_volume()
                 if current_vol > 0: self.previous_volume = current_vol
                 pygame.mixer.music.set_volume(0)
                 self.volume_slider.set(0)
                 self.muted = True
                 self.volume_button.configure(text="MUTED", text_color=COLOR_DEEP_RED)
             except Exception as e: print(f"Warning: Could not set volume on mute: {e}")

    def toggle_shuffle(self):
        """Toggles shuffle mode on/off."""
        self.shuffle_state = not self.shuffle_state
        state_text = "ON" if self.shuffle_state else "OFF"
        color = COLOR_DEEP_RED if self.shuffle_state else COLOR_WHITE
        self.shuffle_button.configure(text_color=color)
        self.status_var.set(f"SHUFFLE {state_text}")
        print(f"Shuffle toggled: {state_text}")

    def toggle_loop(self):
        """Cycles through loop modes: Off -> All -> One -> Off."""
        self.loop_state = (self.loop_state + 1) % 3 # Cycle 0, 1, 2
        if self.loop_state == 0: # Off
            self.loop_button.configure(text_color=COLOR_WHITE, text="LOOP")
            self.status_var.set("LOOP OFF"); print("Loop toggled: OFF")
        elif self.loop_state == 1: # Loop All
            self.loop_button.configure(text_color=COLOR_DEEP_RED, text="LOOP ALL")
            self.status_var.set("LOOP ALL"); print("Loop toggled: ALL")
        else: # Loop One (loop_state == 2)
            self.loop_button.configure(text_color=COLOR_DEEP_RED, text="LOOP ONE")
            self.status_var.set("LOOP ONE"); print("Loop toggled: ONE")

    # --- Slider & Waveform Interaction ---
    def slider_start_scroll(self, event):
        """Called when mouse button is pressed on the song slider."""
        # Activate seeking only if a song is loaded and has duration
        if self.current_song and self.song_length > 0:
            self.slider_active = True
            # print("Slider press") # Reduce console noise
        else:
            self.slider_active = False # Ignore if no song or zero length
            # print("Slider press ignored (no song/duration)")

    def slider_stop_scroll(self, event):
        """Called when mouse button is released after dragging the song slider."""
        if not self.slider_active: return # Only act if dragging was initiated properly
        self.slider_active = False
        # Get final position from slider and seek
        position = float(self.song_slider.get())
        print(f"Slider release - Seeking to: {position:.2f}s")
        self.seek_song(position)

    def slide_song(self, value):
        """Callback called continuously while the song slider is dragged."""
        # Update visuals only if actively dragging to avoid conflicts with mixer updates
        if not self.slider_active: return

        position = float(value)
        # Update internal time state immediately for responsiveness
        self.song_time = position
        # Update time label display
        mins, secs = divmod(int(position), 60)
        self.current_time_label.configure(text=f"{mins:02d}:{secs:02d}")
        # Update waveform position indicator line
        if self.song_length > 0:
            position_ratio = np.clip(position / self.song_length, 0.0, 1.0)
            self.draw_waveform_position_indicator(position_ratio)
        else:
            self.draw_waveform_position_indicator(0)
        # Update oscilloscope based on dragged position (if data available)
        if self.raw_sample_data is not None:
             self.update_oscilloscope()

    def on_waveform_press(self, event):
        """Called when mouse button is pressed on the waveform plot."""
        # Check if click is within the axes, data exists, and song has duration
        if (event.inaxes != self.ax_wave or self.waveform_peak_data is None or
            len(self.waveform_peak_data) == 0 or self.song_length <= 0):
            self.waveform_dragging = False; return

        self.waveform_dragging = True
        self.slider_active = True # Treat waveform drag like slider drag for update logic
        # print("Waveform press") # Reduce console noise
        self._update_position_from_waveform_event(event) # Update visuals immediately

    def on_waveform_motion(self, event):
        """Called when mouse moves while pressed on the waveform plot."""
        if not self.waveform_dragging or event.inaxes != self.ax_wave: return
        self._update_position_from_waveform_event(event) # Update visuals continuously

    def on_waveform_release(self, event):
        """Called when mouse button is released after clicking/dragging on waveform."""
        if not self.waveform_dragging: return
        self.waveform_dragging = False
        self.slider_active = False
        # Get the final target time from the slider (which was updated by motion events)
        target_time = float(self.song_slider.get())
        print(f"Waveform release - Seeking to: {target_time:.2f}s")
        self.seek_song(target_time)

    def on_waveform_leave(self, event):
        """Called when mouse leaves the waveform plot area."""
        # If dragging and mouse leaves, treat it as a release to seek
        if self.waveform_dragging:
            print("Waveform leave while dragging - treating as release")
            self.on_waveform_release(event)

    def _update_position_from_waveform_event(self, event):
        """Helper to update UI visuals based on waveform click/drag event."""
        # Guard clauses
        if (self.waveform_peak_data is None or len(self.waveform_peak_data) == 0 or
            self.song_length <= 0 or event.xdata is None): return

        num_points = len(self.waveform_peak_data)
        x_coord = event.xdata
        # Calculate position ratio based on click coordinate relative to data points
        position_ratio = np.clip(x_coord / (num_points - 1), 0.0, 1.0) if num_points > 1 else 0.0
        target_time = position_ratio * self.song_length

        # --- Update UI elements directly for immediate feedback ---
        self.song_time = target_time # Update internal time state
        self.song_slider.set(target_time) # Update slider position to match
        mins, secs = divmod(int(target_time), 60)
        self.current_time_label.configure(text=f"{mins:02d}:{secs:02d}") # Update time label
        self.draw_waveform_position_indicator(position_ratio) # Update indicator line
        if self.raw_sample_data is not None: self.update_oscilloscope() # Update oscilloscope

    # --- Seeking Logic ---
    def seek_song(self, position_seconds):
        """Seeks playback to the specified time in seconds."""
        # Only seek if a song is loaded and has a valid duration
        if self.current_song and self.song_length > 0:
            # 1. Clamp the requested position within valid bounds [0, song_length]
            seek_pos = np.clip(position_seconds, 0.0, self.song_length)
            print(f"Seeking to: {seek_pos:.2f}s (requested: {position_seconds:.2f}s)")

            # 2. Update internal time state and UI immediately for responsiveness
            self.song_time = seek_pos
            self.song_slider.set(seek_pos)
            mins, secs = divmod(int(seek_pos), 60)
            self.current_time_label.configure(text=f"{mins:02d}:{secs:02d}")
            pos_ratio = np.clip(seek_pos / self.song_length, 0.0, 1.0)
            self.draw_waveform_position_indicator(pos_ratio)
            # Update oscilloscope immediately if data is available
            if self.raw_sample_data is not None:
                 self.update_oscilloscope()

            # 3. Handle actual audio playback based on current state
            try:
                if self.playing_state or self.paused: # If currently playing or paused
                    was_paused = self.paused # Remember if paused before seeking
                    # Use pygame.mixer.music.play(start=...) for seeking
                    # This is generally preferred over stop -> load -> play for seeking
                    pygame.mixer.music.play(start=seek_pos)

                    if was_paused:
                        pygame.mixer.music.pause() # Re-pause immediately if it was paused
                        self.playing_state = False # Ensure state reflects pause
                        self.paused = True
                    else:
                        # Ensure state reflects active playback
                        self.playing_state = True
                        self.paused = False
                        # Make sure update thread is running if it wasn't
                        self.start_update_thread()

                else: # If player was stopped, just update the position for the *next* play command
                    self.stopped_position = seek_pos
                    print(f"Player stopped, updated next start position to {seek_pos:.2f}s")

            except pygame.error as e: print(f"Pygame error on seek playback: {e}"); self.status_var.set("ERROR SEEKING")
            except Exception as e: print(f"General error on seek playback: {e}"); traceback.print_exc(); self.status_var.set("ERROR SEEKING")
        else: print("Seek ignored: No song loaded or song length is zero.")

    # --- Song Info & Metadata ---
    def update_song_info(self):
        """Updates labels and slider range based on the current song's metadata."""
        if not self.current_song: # Reset if no song is loaded
            self.song_title_var.set("NO SONG LOADED")
            self.total_time_label.configure(text="00:00")
            self.song_slider.configure(to=100, number_of_steps=100)
            self.song_slider.set(0)
            self.song_length = 0.0
            return

        song_name = os.path.basename(self.current_song)
        self.song_title_var.set(song_name) # Set title label

        try:
            # Use Mutagen to get accurate duration
            file_extension = os.path.splitext(self.current_song)[1].lower()
            audio = None
            if file_extension == '.mp3': audio = MP3(self.current_song)
            elif file_extension == '.flac': audio = FLAC_MUTAGEN(self.current_song)
            # Add elif for other supported types if needed

            if audio and hasattr(audio, 'info') and hasattr(audio.info, 'length'):
                self.song_length = audio.info.length
                # Basic validation for song length read from file
                if not isinstance(self.song_length, (int, float)) or self.song_length <= 0:
                    print(f"Warning: Invalid song length read ({self.song_length}). Setting to 0.")
                    self.song_length = 0.0

                # Update total time label
                mins, secs = divmod(int(self.song_length), 60)
                self.total_time = f"{mins:02d}:{secs:02d}"
                self.total_time_label.configure(text=self.total_time)

                # Update slider range and steps
                slider_max = max(1.0, self.song_length) # Ensure slider max is at least 1
                # Set number_of_steps for potentially smoother seeking granularity
                num_steps = max(100, int(slider_max * 5)) # e.g., 5 steps per second
                self.song_slider.configure(to=slider_max, number_of_steps=num_steps)

                # Reset slider position only if starting from beginning or stopped
                if self.stopped_position == 0 and not self.playing_state:
                    self.song_slider.set(0)
                    self.current_time_label.configure(text="00:00") # Ensure time label is also reset

            else: # Mutagen couldn't read info or unsupported type
                print(f"Could not get audio info for: {song_name}")
                raise ValueError(f"Mutagen info error or unsupported format")

        except Exception as e: # Catch errors during info reading (file access, Mutagen error)
            print(f"Error getting song info for {self.current_song}: {e}")
            self.song_length = 0.0; self.total_time = "00:00"
            self.total_time_label.configure(text=self.total_time)
            self.song_slider.configure(to=100, number_of_steps=100); self.song_slider.set(0)
            self.song_title_var.set(f"{song_name} (Info Error)")
            self.current_time_label.configure(text="00:00")

    # --- Waveform Generation ---
    def trigger_waveform_generation(self):
        """Initiates background waveform data generation for the current song."""
        # Check if generation is already running for this song
        if self.waveform_thread and self.waveform_thread.is_alive():
            # If already running, signal the old thread to stop
            print("Waveform generation already in progress. Aborting previous.")
            self.abort_waveform_generation()
            time.sleep(0.05) # Give abort a moment to register

        if not self.current_song: print("trigger_waveform_generation: No current song."); return

        # Clear previous data immediately
        self.waveform_peak_data = None; self.raw_sample_data = None; self.sample_rate = None
        # Draw placeholders while generating
        self.draw_initial_placeholder(self.ax_wave, self.fig_wave, COLOR_WHITE,"GENERATING...")
        self.draw_initial_placeholder(self.ax_osc, self.fig_osc, COLOR_DEEP_RED,"")

        # Start the background thread
        self.waveform_abort_flag.clear() # Reset abort flag for the new thread
        self.waveform_thread = threading.Thread(
            target=self.generate_waveform_data_background,
            args=(self.current_song, self.waveform_abort_flag), # Pass path and flag
            daemon=True # Allow program to exit even if thread is running
        )
        print(f"trigger_waveform_generation: Starting thread for {os.path.basename(self.current_song)}")
        self.waveform_thread.start()

    def generate_waveform_data_background(self, song_path, abort_flag):
        """
        [Runs in a background thread]
        Loads audio file, processes samples, generates peak and raw data.
        Uses pydub (requires ffmpeg).
        """
        print(f"BG_THREAD: Starting waveform generation for: {os.path.basename(song_path)}")
        local_peak_data = None; local_raw_data = None; effective_sample_rate = None; error_message = None
        try:
            start_time = time.monotonic()
            # --- Early abort check ---
            if abort_flag.is_set(): print(f"BG_THREAD: ...aborted early"); return
            if not os.path.exists(song_path): raise FileNotFoundError(f"Audio file not found: {song_path}")

            # --- Load audio using pydub ---
            # This requires ffmpeg/ffprobe to be installed and in the PATH
            try:
                 sound = AudioSegment.from_file(song_path)
            except FileNotFoundError: # Specifically catch if ffmpeg/ffprobe is missing
                raise ImportError("FFmpeg/FFprobe not found. Please install and add to PATH.")
            except Exception as load_err: # Catch other pydub loading errors
                 raise RuntimeError(f"Pydub failed to load file: {load_err}")

            print(f"BG_THREAD: Loaded '{os.path.basename(song_path)}' in {time.monotonic() - start_time:.2f}s")
            load_time = time.monotonic()
            # --- Abort check after loading ---
            if abort_flag.is_set(): print(f"BG_THREAD: ...aborted after load"); return

            # --- Get audio properties ---
            original_sample_rate = sound.frame_rate
            bit_depth = sound.sample_width * 8
            if bit_depth == 0: bit_depth = 16; print(f"BG_THREAD: Warning: Assuming 16-bit depth.")
            # Max possible value for signed PCM audio of this bit depth
            calculated_max_val = 2**(bit_depth - 1)
            if calculated_max_val <= 0: calculated_max_val = 32768; print(f"BG_THREAD: Warning: Using 16-bit max value (32768).")
            print(f"BG_THREAD: Detected {bit_depth}-bit audio @ {original_sample_rate} Hz. Max abs value used: {calculated_max_val}")

            # --- Convert to NumPy array and normalize ---
            samples_array = np.array(sound.get_array_of_samples())
            if samples_array.size == 0: raise ValueError("Audio file contains no samples.")

            # Convert to mono if stereo
            if sound.channels == 2:
                samples_float = samples_array.astype(np.float64)
                # Reshape to (n_samples, 2) and average columns
                mono_samples = samples_float.reshape((-1, 2)).mean(axis=1)
            else: # Already mono
                mono_samples = samples_array.astype(np.float64)

            # Normalize samples to [-1.0, 1.0] range
            mono_samples_normalized = mono_samples / calculated_max_val
            # Clip to handle potential floating point inaccuracies exceeding the range slightly
            mono_samples_normalized = np.clip(mono_samples_normalized, -1.0, 1.0)
            print(f"BG_THREAD: Converted to mono/float/normalized in {time.monotonic() - load_time:.2f}s")
            norm_time = time.monotonic()
            # --- Abort check after normalization ---
            if abort_flag.is_set(): print(f"BG_THREAD: ...aborted after normalization"); return

            # --- Generate downsampled raw data for oscilloscope ---
            if self.osc_downsample_factor > 1:
                 local_raw_data = mono_samples_normalized[::self.osc_downsample_factor]
                 effective_sample_rate = original_sample_rate / self.osc_downsample_factor
                 # print(f"BG_THREAD: Downsampled raw data by {self.osc_downsample_factor}x (Effective SR: {effective_sample_rate:.0f} Hz)") # Reduce noise
            else:
                 local_raw_data = mono_samples_normalized
                 effective_sample_rate = original_sample_rate
            raw_gen_time = time.monotonic()
            # --- Abort check after raw data generation ---
            if abort_flag.is_set(): print(f"BG_THREAD: ...aborted during raw processing"); return

            # --- Generate peak data for static waveform plot ---
            target_points = 500 # Target number of points for the static waveform display
            if len(mono_samples_normalized) == 0:
                print(f"BG_THREAD: Warning: No samples found after normalization..."); local_peak_data = np.array([])
            else:
                chunk_size = max(1, len(mono_samples_normalized) // target_points)
                processed_peaks = []
                num_chunks = (len(mono_samples_normalized) + chunk_size - 1) // chunk_size
                # print(f"BG_THREAD: Generating ~{target_points} peak points from ~{num_chunks} chunks...") # Reduce noise
                for i in range(0, len(mono_samples_normalized), chunk_size):
                     # Check abort flag frequently during this potentially long loop
                     if i % 100 == 0 and abort_flag.is_set(): print(f"BG_THREAD: ...aborted during peak processing (chunk {i//chunk_size}/{num_chunks})"); return
                     chunk = mono_samples_normalized[i:i + chunk_size]
                     # Find the maximum absolute value in the chunk
                     peak = np.max(np.abs(chunk)) if len(chunk) > 0 else 0.0
                     processed_peaks.append(peak)
                local_peak_data = np.array(processed_peaks)
            peak_gen_time = time.monotonic()
            # print(f"BG_THREAD: Raw data gen: {raw_gen_time - norm_time:.2f}s, Peak data gen: {peak_gen_time - raw_gen_time:.2f}s") # Reduce noise
            print(f"BG_THREAD: Finished waveform generation for: {os.path.basename(song_path)} in {time.monotonic() - start_time:.2f}s total")

        except ImportError as e: error_message = f"WAVEFORM ERROR\n({e})"; print(f"BG_THREAD: {error_message}") # Include ffmpeg message
        except FileNotFoundError as e: error_message = f"WAVEFORM ERROR\nFile Not Found"; print(f"BG_THREAD: Error: {e}")
        except MemoryError: error_message = "WAVEFORM ERROR\nMemory Error"; print("BG_THREAD: MemoryError during waveform generation.")
        except Exception as e: print(f"BG_THREAD: Error generating waveform:"); traceback.print_exc(); error_message = f"WAVEFORM ERROR\n({type(e).__name__})"
        finally:
            # Schedule the result processing back on the main thread ONLY if not aborted
            if not abort_flag.is_set():
                self.root.after(1, self.process_waveform_result, song_path, local_peak_data, local_raw_data, effective_sample_rate, error_message)
            else: # If aborted, just log it
                print(f"BG_THREAD: Waveform generation aborted for {os.path.basename(song_path)}, result not processed.")

    def process_waveform_result(self, song_path, peak_data, raw_data, sample_rate, error_message):
        """
        [Runs on Main Thread via root.after]
        Processes the results from the background waveform generation thread.
        Updates internal state and redraws plots.
        """
        # --- Check if the result is still relevant ---
        # User might have quickly changed songs while generation was running
        if song_path != self.current_song:
            print(f"Ignoring stale waveform result for: {os.path.basename(song_path)}")
            return

        print(f"Processing waveform result for: {os.path.basename(song_path)}")
        # --- Handle errors first ---
        if error_message:
            self.waveform_peak_data = None; self.raw_sample_data = None; self.sample_rate = None
            # Display error message on the waveform plot
            self.draw_initial_placeholder(self.ax_wave, self.fig_wave, COLOR_WHITE, error_message)
            # Clear oscilloscope plot
            self.draw_initial_placeholder(self.ax_osc, self.fig_osc, COLOR_DEEP_RED, "")
            # Update status only if it was showing 'generating'
            current_status = self.status_var.get()
            if "GENERATING" in current_status: self.status_var.set("ERROR")
            print(f"Waveform error processed: {error_message}")

        # --- Handle success case (valid data received) ---
        elif peak_data is not None and raw_data is not None and sample_rate is not None and len(peak_data) > 0 and len(raw_data) > 0:
            # Store the generated data
            self.waveform_peak_data = peak_data
            self.raw_sample_data = raw_data
            self.sample_rate = sample_rate
            # Draw the new static waveform plot
            self.draw_static_matplotlib_waveform()
            # Update status only if it was showing 'generating'
            current_status = self.status_var.get()
            if "GENERATING" in current_status:
                 # Set status based on current playback state
                 self.status_var.set("PLAYING" if self.playing_state else "STOPPED")
            # Immediately update the position indicator and oscilloscope based on current time
            # This ensures visuals sync up right after data is ready
            self.update_song_position()
            print("Waveform data processed successfully.")

        # --- Handle case where generation technically succeeded but produced empty/invalid data ---
        else:
             print(f"Received empty or invalid waveform data for: {os.path.basename(song_path)}")
             self.waveform_peak_data = None; self.raw_sample_data = None; self.sample_rate = None
             self.draw_initial_placeholder(self.ax_wave, self.fig_wave, COLOR_WHITE,"GEN FAILED")
             self.draw_initial_placeholder(self.ax_osc, self.fig_osc, COLOR_DEEP_RED,"")
             current_status = self.status_var.get()
             if "GENERATING" in current_status: self.status_var.set("ERROR")

    def draw_static_matplotlib_waveform(self):
        """Draws the static peak waveform using Matplotlib."""
        ax = self.ax_wave; fig = self.fig_wave; data = self.waveform_peak_data

        # Check if data and plot elements are valid
        if data is None or len(data) == 0 or not ax or not fig or not fig.canvas:
            # If no data, ensure a placeholder is drawn (e.g., if generation failed)
            if ax and fig and fig.canvas:
                self.draw_initial_placeholder(ax, fig, COLOR_WHITE, "NO WAVEFORM DATA" if self.current_song else "LOAD A SONG")
            else: print("draw_static_matplotlib_waveform: Cannot draw, no data or axes.")
            return

        try:
            ax.clear(); self._configure_axes(ax, fig, COLOR_WHITE) # Clear and reconfigure axes
            x = np.arange(len(data)); y = data; center_y = 0.0
            # Scale y data visually (e.g., use 90% of the vertical plot height)
            scaled_y = y * 0.9
            # Use fill_between for a solid waveform appearance
            ax.fill_between(x, center_y - scaled_y, center_y + scaled_y, color=COLOR_WHITE, linewidth=0)
            # Set plot limits
            ax.set_ylim(-1, 1); ax.set_xlim(0, len(data) - 1 if len(data) > 1 else 1)
            # Explicitly draw the canvas to update the UI
            fig.canvas.draw_idle()
            self.position_indicator_line_wave = None # Clear old indicator line reference
            # print("Static Matplotlib waveform drawn.") # Reduce console noise

        except Exception as e: print(f"Error drawing static waveform: {e}"); traceback.print_exc(); self.draw_initial_placeholder(ax, fig, COLOR_WHITE, "DRAW ERROR")

    def draw_waveform_position_indicator(self, position_ratio):
        """Draws or updates the vertical line indicating playback position on the waveform."""
        ax = self.ax_wave; fig = self.fig_wave; data = self.waveform_peak_data; line_attr = 'position_indicator_line_wave'

        # Only draw if data exists and plot elements are valid
        if data is None or len(data) == 0 or not ax or not fig or not fig.canvas: return

        try:
            num_points = len(data)
            position_ratio = np.clip(position_ratio, 0.0, 1.0) # Ensure ratio is valid [0, 1]
            # Calculate x-coordinate based on data points and ratio
            x_pos = position_ratio * (num_points - 1) if num_points > 1 else 0
            x_pos = max(0, min(x_pos, num_points - 1)) if num_points > 1 else 0 # Clamp x_pos

            # --- Efficiently update the line ---
            old_line = getattr(self, line_attr, None)
            # Remove the old line *if it exists and is still plotted*
            if old_line and old_line in ax.lines:
                try: old_line.remove()
                except (ValueError, AttributeError): pass # Ignore if already removed or invalid

            # Draw the new vertical line
            if ax: # Ensure ax is valid before drawing
                 # Make line slightly thinner for smaller plot
                 new_line = ax.axvline(x=x_pos, color=COLOR_DEEP_RED, linewidth=1.2, ymin=0.05, ymax=0.95) # Limit vertical extent slightly for aesthetics
                 setattr(self, line_attr, new_line) # Store reference to the new line object

            # Redraw the canvas only if necessary (implicitly handled by draw_idle)
            fig.canvas.draw_idle()

        except Exception as e: print(f"Error drawing position indicator: {e}"); traceback.print_exc(); setattr(self, line_attr, None) # Clear reference on error

    def update_oscilloscope(self):
        """Updates the oscilloscope plot based on current playback time."""
        ax = self.ax_osc; fig = self.fig_osc

        # --- Check all required conditions before proceeding ---
        if (self.raw_sample_data is None or len(self.raw_sample_data) == 0 or
            self.sample_rate is None or self.sample_rate <= 0 or
            not self.playing_state or self.paused or # Only update if actively playing
            not ax or not fig or not fig.canvas):
            # Optionally clear oscilloscope if not playing/paused to avoid stale display
            if (not self.playing_state or self.paused) and ax and fig and fig.canvas:
                 if len(ax.lines) > 0: # Check if it needs clearing
                      self.draw_initial_placeholder(ax, fig, COLOR_DEEP_RED, "")
            return

        try:
            # Calculate the sample index corresponding to the current playback time
            current_sample_index = int(self.song_time * self.sample_rate)
            # Calculate the number of samples to display in the window
            window_samples = int(self.osc_window_seconds * self.sample_rate)
            if window_samples <= 0: window_samples = max(100, int(0.02 * self.sample_rate)) # Use a small default if calculation fails

            # --- Determine slice indices, ensuring they are within bounds ---
            start_index = max(0, current_sample_index)
            # Ensure end_index doesn't exceed data length
            end_index = min(len(self.raw_sample_data), start_index + window_samples)
            # Adjust start_index if end_index hit the boundary, to try and get a full window
            start_index = max(0, end_index - window_samples)

            sample_slice = self.raw_sample_data[start_index:end_index]

            # --- Draw the slice if valid ---
            if len(sample_slice) > 0:
                # Optimize drawing: clear, reconfigure axes, plot, set limits, draw
                ax.clear()
                self._configure_axes(ax, fig, COLOR_DEEP_RED) # Reapply custom styling
                ax.set_ylim(-1.1, 1.1) # Re-apply y-limits after clear
                x_osc = np.arange(len(sample_slice))
                # Make line slightly thinner for smaller plot
                ax.plot(x_osc, sample_slice, color=COLOR_DEEP_RED, linewidth=0.8)
                ax.set_xlim(0, len(sample_slice) - 1 if len(sample_slice) > 1 else 1) # Re-apply x-limits
                fig.canvas.draw_idle() # Redraw the canvas to show update
            else: # If slice is somehow empty, clear the plot
                 if len(ax.lines) > 0: # Clear only if not already empty
                     self.draw_initial_placeholder(ax, fig, COLOR_DEEP_RED, "")

        except Exception as e: print(f"Error updating oscilloscope: {e}") # Keep error concise


    # --- Time Update Thread ---
    def update_song_position(self):
        """
        [Runs periodically via root.after from update_time thread]
        Syncs UI (slider, time labels, plot indicators) with the current playback time.
        Reads position from pygame mixer if playing.
        """
        # Don't update if user is actively interacting with slider or waveform
        if self.slider_active or self.waveform_dragging: return

        # Only update if actively playing and not paused
        if self.playing_state and not self.paused:
             try:
                 if pygame.mixer.music.get_busy(): # Check if mixer is actually playing
                     current_pos_ms = pygame.mixer.music.get_pos() # Get position in milliseconds
                     if current_pos_ms != -1: # -1 indicates error or not playing
                         current_time_sec = current_pos_ms / 1000.0

                         # Update internal time state based on mixer feedback
                         # Add a small buffer when comparing to song_length to prevent slight overshoots if length is exact int
                         if self.song_length > 0:
                             self.song_time = min(current_time_sec, self.song_length + 0.1)
                         else: # If song length is unknown/zero
                             self.song_time = current_time_sec

                         # ---- Update UI based on the possibly just updated self.song_time ----
                         self.song_slider.set(self.song_time) # Update slider position

                         # Update current time label display
                         mins, secs = divmod(int(self.song_time), 60)
                         self.time_elapsed = f"{mins:02d}:{secs:02d}"
                         self.current_time_label.configure(text=self.time_elapsed)

                         # Update waveform position indicator line
                         if self.song_length > 0:
                             position_ratio = np.clip(self.song_time / self.song_length, 0.0, 1.0)
                         else: position_ratio = 0 # Default to start if no length
                         self.draw_waveform_position_indicator(position_ratio)

                         # Update oscilloscope plot
                         self.update_oscilloscope()

                 else: # Mixer is not busy, but state says playing -> song likely just ended
                     # Schedule the end-of-song check on the main thread to avoid race conditions modifying UI
                     self.root.after(10, self.check_music_end_on_main_thread)
             except pygame.error as e:
                 print(f"Pygame error in update_song_position: {e}")
                 self.stop() # Stop playback on error

    def start_update_thread(self):
        """Starts the background thread for updating time and visuals if not already running."""
        # Only start if actually playing and not paused, and if thread isn't already running
        if not self.thread_running and self.playing_state and not self.paused:
            self.thread_running = True
            # Check if thread object exists and is alive (shouldn't be if thread_running was false, but defensive)
            if self.update_thread and self.update_thread.is_alive():
                print("Warning: Update thread restart requested while already active.")
                return
            print("Starting update thread.")
            self.update_thread = threading.Thread(target=self.update_time, daemon=True)
            self.update_thread.start()
        elif not self.playing_state or self.paused:
            # If trying to start while not playing/paused, ensure flag is correctly set to false
            self.thread_running = False

    def update_time(self):
        """
        [Runs in background thread]
        Periodically schedules update_song_position to run on the main thread.
        """
        update_interval = 0.05 # Target ~20 Hz updates for smooth visuals
        # print(f"Update thread loop started.") # Reduce console noise
        while self.thread_running:
            start_loop_time = time.monotonic()

            # Schedule the UI update function to run on the main thread
            # Use after(0) for minimal delay, letting Tkinter manage execution timing efficiently
            if self.root.winfo_exists(): # Check if root window still exists
                 self.root.after(0, self.update_song_position)
            else: # Stop thread if window is closed
                 self.thread_running = False; break

            # Calculate sleep time to maintain the target interval
            end_loop_time = time.monotonic(); time_taken = end_loop_time - start_loop_time
            sleep_time = max(0, update_interval - time_taken)
            time.sleep(sleep_time)

            # Re-check the flag *after* sleep, in case stop/pause was called while sleeping
            if not self.playing_state or self.paused:
                self.thread_running = False # Ensure flag is false if state changed

        # print("Update thread loop finished.") # Reduce console noise

    def check_music_end_on_main_thread(self):
        """
        [Runs on Main Thread via root.after]
        Checks if the music has finished playing and handles looping/shuffle/next.
        """
        # Double-check the state when the function actually runs, as it might have changed
        if not self.playing_state or self.paused: return

        try:
            # Check mixer status again *within the main thread* for safety
            if not pygame.mixer.music.get_busy():
                 print(f"Detected song end for: {os.path.basename(self.current_song)}")
                 # --- Update State ---
                 # State changes MUST happen here in the main thread
                 self.playing_state = False
                 self.paused = False # Ensure paused is false
                 self.thread_running = False # Signal thread should stop (if it hasn't already)
                 self.stopped_position = self.song_length # Record end position accurately

                 # --- Handle End-of-Song Logic ---
                 if self.loop_state == 2: # Loop One
                     print("Looping current song.")
                     self.song_slider.set(0) # Reset slider visually
                     self.current_time_label.configure(text="00:00")
                     self.play_music() # Restart the current song

                 elif self.loop_state == 1: # Loop All
                     print("Looping all - playing next.")
                     self.next_song(auto_advance=True) # Play next song

                 elif self.shuffle_state: # Shuffle
                     print("Shuffle on - playing random.")
                     self.play_random_song(auto_advance=True) # Play a random different song

                 else: # No Loop, No Shuffle - Advance or Stop
                     # Check if it was the last song in the playlist
                     if self.current_song_index >= len(self.songs_list) - 1:
                         print("End of playlist reached.")
                         # Call stop to finalize state and UI for stopped player
                         self.stop()
                         # Optionally reset index/selection to the beginning for next manual play
                         self.current_song_index = 0
                         if self.songs_list: self.select_song(self.current_song_index)
                         # Ensure visuals are fully reset after stop
                         self.song_slider.set(0)
                         self.current_time_label.configure(text="00:00")
                         self.draw_waveform_position_indicator(0)
                         self.draw_initial_placeholder(self.ax_osc, self.fig_osc, COLOR_DEEP_RED,"")
                     else: # Play next song in sequence
                         print("Playing next song in sequence.")
                         self.next_song(auto_advance=True)

        except pygame.error as e: print(f"Pygame error during end check: {e}"); self.stop()
        except Exception as e: print(f"Error during music end check: {e}"); traceback.print_exc(); self.stop()

    def play_random_song(self, auto_advance=False):
        """Plays a random song from the playlist, different from the current one if possible."""
        if not self.songs_list: self.stop(); return # Nothing to play

        # Prepare state based on context (manual shuffle vs. auto-advance)
        if not auto_advance:
             self.stop() # Stop current playback if triggered manually
        else:
             # Reset state cleanly without calling stop() UI updates
             self.playing_state = False; self.paused = False; self.thread_running = False
             self.abort_waveform_generation(); self.stopped_position = 0.0
             print("Auto-advancing to random song.")

        if len(self.songs_list) > 1:
             # Generate a list of possible indices (excluding the current one)
             possible_indices = [i for i in range(len(self.songs_list)) if i != self.current_song_index]
             self.current_song_index = random.choice(possible_indices) # Choose randomly
        elif len(self.songs_list) == 1:
             self.current_song_index = 0 # Play the only song available
        else: # Playlist became empty somehow?
             self.clear_playlist(); return

        self.play_music() # Play the chosen random song from start

    def abort_waveform_generation(self):
        """Signals the background waveform generation thread to stop."""
        if self.waveform_thread and self.waveform_thread.is_alive():
            # Set the flag only if it's not already set to avoid redundant logs
            if not self.waveform_abort_flag.is_set():
                 print(f"Signalling waveform thread to abort...")
                 self.waveform_abort_flag.set()
            # Optionally wait a very short time for the thread to acknowledge, but be careful not to block UI
            # self.waveform_thread.join(0.1)

    def on_closing(self):
        """Handles cleanup when the application window is closed."""
        print("Closing application...");
        # 1. Stop background threads cleanly
        self.thread_running = False # Signal update thread to stop its loop
        self.abort_waveform_generation() # Signal waveform thread to stop processing

        # 2. Stop Pygame mixer and quit Pygame
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            print("Pygame mixer stopped and quit.")
        except Exception as e: print(f"Error during pygame quit: {e}")

        # 3. Close Matplotlib figures to release resources
        try: plt.close(self.fig_wave)
        except Exception as e: print(f"Error closing waveform figure: {e}")
        try: plt.close(self.fig_osc)
        except Exception as e: print(f"Error closing oscilloscope figure: {e}")

        # Give threads a brief moment to exit (optional, depends on daemon status)
        # time.sleep(0.1)

        # 4. Destroy the Tkinter window
        if self.root:
            self.root.destroy()
        print("Application closed.")

# --- Main Execution Block ---
if __name__ == "__main__":
    print("Starting MN-1 Music Player...")
    try:
        # Set DPI Awareness (Windows) for clearer UI elements
        if os.name == 'nt':
             try: from ctypes import windll; windll.shcore.SetProcessDpiAwareness(1)
             except Exception as e: print(f"Could not set DPI awareness: {e}")

        # Set CustomTkinter appearance
        ctk.set_appearance_mode("dark") # Options: "dark", "light", "system"
        # ctk.set_default_color_theme("blue") # Optional theme: "blue", "green", "dark-blue"

        # Create the main application window
        root = ctk.CTk()
        player = MN1MusicPlayer (root) # Instantiate the player class
        root.mainloop() # Start the Tkinter event loop

    except Exception as main_error:
        # Catch any unexpected errors during initialization or runtime
        print("\n--- FATAL APPLICATION ERROR ---")
        print(f"An unhandled error occurred:")
        traceback.print_exc()
        # Attempt to show a simple Tkinter error box as a last resort
        try:
             import tkinter as tk; from tkinter import messagebox
             root_err = tk.Tk()
             root_err.withdraw() # Hide the empty root window
             messagebox.showerror("Fatal Error", f"The application encountered a critical error and needs to close.\n\nError: {main_error}\n\nPlease check the console output for details.")
             root_err.destroy()
        except Exception as tk_error: print(f"(Displaying Tkinter error message also failed: {tk_error})")
        input("Press Enter to exit console.") # Keep console open to see the error
