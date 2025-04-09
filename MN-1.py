import customtkinter as ctk
from tkinter import filedialog
import pygame
import os
from PIL import Image, ImageTk
from mutagen.mp3 import MP3
import time
import random
import threading
import numpy as np
from pydub import AudioSegment

# Define colors for the minimal theme
COLOR_BLACK = "#000000"
COLOR_WHITE = "#FFFFFF"
COLOR_DEEP_RED = "#8B0000" # Deep Red, you can adjust this to your preferred shade
COLOR_SILVER = "#C0C0C0" # Silver color defined

class CyberpunkMusicPlayer:
    def __init__(self, root):
        # Initialize the main window
        self.root = root
        self.root.title("MN-1") # Updated title to MN-1
        self.root.geometry("800x600")
        self.root.configure(fg_color=COLOR_BLACK)  # Black background
        self.root.resizable(True, True) # Modified line to allow resizing

        # Initialize pygame mixer
        pygame.mixer.init()

        # Global variables
        self.current_song = ""
        self.songs_list = []
        self.current_song_index = 0
        self.playing_state = False
        self.paused = False
        self.shuffle_state = False
        self.loop_state = 0  # 0: no loop, 1: loop all, 2: loop one  <- Renamed repeat_state to loop_state
        self.muted = False
        self.previous_volume = 0.5
        self.stopped_position = 0.0 # Store stopped position
        self.slider_active = False # Flag to indicate slider interaction

        # Set default volume
        pygame.mixer.music.set_volume(0.5)

        # Create fonts - Cyberpunk style fonts
        self.title_font = ("SF Mono", 18, "bold")  # SF Mono or similar monospace
        self.normal_font = ("SF Mono", 12)
        self.button_font = ("SF Mono", 14, "bold")

        # Create main frames
        self.create_frames()

        # Create all widgets
        self.create_player_area()
        self.create_waveform_display()
        self.create_controls()
        self.create_playlist_area()

        # Initialize time-related variables
        self.song_length = 0
        self.song_time = 0
        self.time_elapsed = "00:00"
        self.total_time = "00:00"

        # Initialize waveform variables
        self.waveform_data = []
        self.waveform_position = 0
        self.waveform_update_interval = 100  # milliseconds
        self.waveform_static_image = None # To store the static waveform image

        # Thread for updating song position
        self.update_thread = None
        self.thread_running = False

        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_frames(self):
        # Main frames for organization
        self.player_frame = ctk.CTkFrame(self.root, fg_color=COLOR_BLACK, corner_radius=0)
        self.player_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Left side - player controls and visuals
        self.left_frame = ctk.CTkFrame(self.player_frame, fg_color=COLOR_BLACK, width=500, corner_radius=0)
        self.left_frame.pack(side="left", fill="both", expand=True)

        # Right side - playlist
        self.right_frame = ctk.CTkFrame(self.player_frame, fg_color=COLOR_BLACK, width=300, corner_radius=0)  # Slightly lighter for playlist contrast - now black as well for minimal look
        self.right_frame.pack(side="right", fill="both", expand=True)

        # Controls frame at bottom
        self.controls_frame = ctk.CTkFrame(self.left_frame, fg_color=COLOR_BLACK, height=100, corner_radius=0)
        self.controls_frame.pack(side="bottom", fill="x", pady=10)

        # Visual frame
        self.visual_frame = ctk.CTkFrame(self.left_frame, fg_color=COLOR_BLACK, corner_radius=0)
        self.visual_frame.pack(side="top", fill="both", expand=True, pady=10)

    def create_player_area(self):
        # Song info frame
        self.info_frame = ctk.CTkFrame(self.visual_frame, fg_color=COLOR_BLACK, corner_radius=0)
        self.info_frame.pack(fill="x", pady=10)

        # Song title
        self.song_title_var = ctk.StringVar()
        self.song_title_var.set("NO SONG LOADED")
        self.song_title_label = ctk.CTkLabel(self.info_frame,
                                             textvariable=self.song_title_var,
                                             font=self.title_font,
                                             fg_color=COLOR_BLACK,
                                             text_color=COLOR_WHITE,  # White for song title
                                             anchor="w")
        self.song_title_label.pack(fill="x", padx=10)

        # Status label
        self.status_var = ctk.StringVar()
        self.status_var.set("IDLE")
        self.status_label = ctk.CTkLabel(self.info_frame,
                                         textvariable=self.status_var,
                                         font=self.normal_font,
                                         fg_color=COLOR_BLACK,
                                         text_color=COLOR_WHITE,  # White for status
                                         anchor="w")
        self.status_label.pack(fill="x", padx=10)

        # Waveform frame (Pack waveform frame first)
        self.waveform_frame = ctk.CTkFrame(self.visual_frame, fg_color=COLOR_BLACK, corner_radius=0)
        self.waveform_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Time slider frame (Then pack slider frame)
        self.slider_frame = ctk.CTkFrame(self.visual_frame, fg_color=COLOR_BLACK, corner_radius=0)
        self.slider_frame.pack(fill="x", pady=5, padx=10)

        # Song position slider
        self.song_slider = ctk.CTkSlider(self.slider_frame,
                                         from_=0,
                                         to=100,
                                         fg_color=COLOR_BLACK,
                                         button_color=COLOR_SILVER, # Silver fader knob
                                         button_hover_color=COLOR_SILVER, # Silver fader knob hover
                                         progress_color=COLOR_DEEP_RED,
                                         command=self.slide_song,
                                         variable=ctk.DoubleVar()) # Use DoubleVar to handle float values
        self.song_slider.pack(fill="x", pady=5)
        self.song_slider.bind("<ButtonPress-1>", self.slider_start_scroll) # Bind mouse press event
        self.song_slider.bind("<ButtonRelease-1>", self.slider_stop_scroll) # Bind mouse release event


        # Time labels frame
        self.time_frame = ctk.CTkFrame(self.slider_frame, fg_color=COLOR_BLACK, corner_radius=0)
        self.time_frame.pack(fill="x")

        # Current time
        self.current_time_label = ctk.CTkLabel(self.time_frame,
                                              text="00:00",
                                              font=self.normal_font,
                                              fg_color=COLOR_BLACK,
                                              text_color=COLOR_WHITE)
        self.current_time_label.pack(side="left")

        # Total time
        self.total_time_label = ctk.CTkLabel(self.time_frame,
                                            text="00:00",
                                            font=self.normal_font,
                                            fg_color=COLOR_BLACK,
                                            text_color=COLOR_WHITE)
        self.total_time_label.pack(side="right")

    def create_waveform_display(self):
        # Waveform frame is already created in `create_player_area`
        # Waveform canvas - using standard tkinter Canvas as CTkCanvas might not exist
        self.waveform_canvas = ctk.CTkCanvas(self.waveform_frame,
                                           bg=COLOR_BLACK,
                                           highlightthickness=1,
                                           highlightbackground=COLOR_WHITE,  # White grid
                                           height=200)
        self.waveform_canvas.pack(fill="both", expand=True)

        # Draw initial empty waveform grid
        self.draw_waveform_grid()

    def draw_waveform_grid(self):
        """Draw grid lines on the waveform canvas"""
        width = self.waveform_canvas.winfo_width() or 460
        height = self.waveform_canvas.winfo_height() or 200

        # Clear canvas
        self.waveform_canvas.delete("all")

        # Draw horizontal center line
        self.waveform_canvas.create_line(
            0, height/2, width, height/2,
            fill=COLOR_WHITE, width=1, dash=(4, 4)
        )

        # Draw vertical grid lines
        grid_spacing = width / 10
        for i in range(1, 10):
            x = i * grid_spacing
            self.waveform_canvas.create_line(
                x, 0, x, height,
                fill=COLOR_WHITE, width=1, dash=(2, 6)
            )

    def create_controls(self):
        # Create buttons frame
        self.buttons_frame = ctk.CTkFrame(self.controls_frame, fg_color=COLOR_BLACK, corner_radius=0)
        self.buttons_frame.pack(pady=5)

        # Button style configuration
        button_kwargs = {
            "font": self.button_font,
            "fg_color": COLOR_BLACK,  # Black button color
            "text_color": COLOR_WHITE,  # White button text
            "hover_color": COLOR_DEEP_RED,  # Deep Red hover
            "border_width": 0,
            "corner_radius": 0, # Sharp edges for buttons
            "width": 40,
            "height": 30
        }

        # Previous button
        self.prev_button = ctk.CTkButton(self.buttons_frame, text="◄◄", command=self.previous_song, **button_kwargs)
        self.prev_button.grid(row=0, column=0, padx=5)

        # Play button
        self.play_button = ctk.CTkButton(self.buttons_frame, text="▶", command=self.play, **button_kwargs)
        self.play_button.grid(row=0, column=1, padx=5)

        # Pause button
        self.pause_button = ctk.CTkButton(self.buttons_frame, text="II", command=self.pause, **button_kwargs)
        self.pause_button.grid(row=0, column=2, padx=5)

        # Next button
        self.next_button = ctk.CTkButton(self.buttons_frame, text="►►", command=self.next_song, **button_kwargs)
        self.next_button.grid(row=0, column=3, padx=5)

        # Stop button - DELETED
        # self.stop_button = ctk.CTkButton(self.buttons_frame, text="■", command=self.stop, **button_kwargs)
        # self.stop_button.grid(row=0, column=3, padx=5)

        # Additional controls
        self.extra_frame = ctk.CTkFrame(self.controls_frame, fg_color=COLOR_BLACK, corner_radius=0)
        self.extra_frame.pack(pady=5)

        # Extra buttons style configuration
        extra_button_kwargs = {
            "font": self.normal_font,
            "fg_color": COLOR_BLACK,
            "text_color": COLOR_WHITE,  # White text for extra buttons initially
            "hover_color": COLOR_DEEP_RED,
            "border_width": 0,
            "corner_radius": 0, # Sharp edges for extra buttons
            "width": 80
        }

        # Shuffle button
        self.shuffle_button = ctk.CTkButton(self.extra_frame, text="SHUFFLE", command=self.toggle_shuffle, **extra_button_kwargs)
        self.shuffle_button.grid(row=0, column=0, padx=5)

        # Loop button  <- Renamed Repeat button to Loop button
        self.loop_button = ctk.CTkButton(self.extra_frame, text="LOOP", command=self.toggle_loop, **extra_button_kwargs) # <- Renamed Repeat button to Loop button
        self.loop_button.grid(row=0, column=1, padx=5) # <- Renamed repeat_button to loop_button

        # Volume button
        self.volume_button = ctk.CTkButton(self.extra_frame, text="VOL", command=self.toggle_mute, **extra_button_kwargs)
        self.volume_button.grid(row=0, column=2, padx=5)

        # Volume slider
        self.volume_slider = ctk.CTkSlider(self.extra_frame,
                                          from_=0,
                                          to=1,
                                          number_of_steps=100,
                                          fg_color=COLOR_BLACK,
                                          button_color=COLOR_SILVER, # Silver fader knob
                                          button_hover_color=COLOR_SILVER, # Silver fader knob hover
                                          progress_color=COLOR_DEEP_RED,
                                          command=self.volume_adjust)
        self.volume_slider.set(0.5)
        self.volume_slider.grid(row=0, column=3, padx=5)

        # MN-1 Label - Placed in the bottom left corner of controls_frame, above shuffle
        self.mn1_label = ctk.CTkLabel(self.controls_frame,
                                        text="MN-1",
                                        font=self.normal_font,
                                        fg_color=COLOR_BLACK,
                                        text_color=COLOR_WHITE)
        self.mn1_label.place(relx=0.01, rely=0.45, anchor="sw") # Place in bottom-left, adjust rely as needed


    def create_playlist_area(self):
        # Playlist label
        self.playlist_label = ctk.CTkLabel(self.right_frame,
                                          text="PLAYLIST",
                                          font=self.title_font,
                                          fg_color=COLOR_BLACK,
                                          text_color=COLOR_WHITE)  # White playlist title
        self.playlist_label.pack(pady=5)

        # Playlist frame
        self.playlist_frame = ctk.CTkFrame(self.right_frame, fg_color=COLOR_BLACK, corner_radius=0)
        self.playlist_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Create a custom list box using CTkScrollableFrame and CTkLabels
        self.playlist_scrollable = ctk.CTkScrollableFrame(self.playlist_frame, fg_color=COLOR_BLACK)
        self.playlist_scrollable.pack(fill="both", expand=True)

        # Store playlist entries for reference
        self.playlist_entries = []

        # Playlist control buttons
        self.playlist_buttons_frame = ctk.CTkFrame(self.right_frame, fg_color=COLOR_BLACK, corner_radius=0)
        self.playlist_buttons_frame.pack(fill="x", pady=10)

        # Playlist buttons style configuration
        playlist_button_kwargs = {
            "font": self.normal_font,
            "fg_color": COLOR_BLACK,
            "text_color": COLOR_WHITE,  # White for playlist buttons
            "hover_color": COLOR_DEEP_RED,
            "border_width": 0,
            "corner_radius": 0, # Sharp edges for playlist buttons
            "width": 80
        }

        # Add button
        self.add_button = ctk.CTkButton(self.playlist_buttons_frame, text="ADD", command=self.add_songs, **playlist_button_kwargs)
        self.add_button.pack(side="left", padx=5)

        # Remove button
        self.remove_button = ctk.CTkButton(self.playlist_buttons_frame, text="REMOVE", command=self.remove_song, **playlist_button_kwargs)
        self.remove_button.pack(side="left", padx=5)

        # Clear button
        self.clear_button = ctk.CTkButton(self.playlist_buttons_frame, text="CLEAR", command=self.clear_playlist, **playlist_button_kwargs)
        self.clear_button.pack(side="left", padx=5)

    def add_songs(self):
        """Add songs to the playlist"""
        # Get song paths
        songs = filedialog.askopenfilenames(
            title="Select MP3 Files",
            filetypes=(("MP3 Files", "*.mp3"), ("All Files", "*.*"))
        )

        # Add songs to playlist
        for song in songs:
            # Extract filename from path
            song_name = os.path.basename(song)
            self.add_song_to_playlist(song_name, song)
            self.songs_list.append(song)

        # Update status
        if songs and not self.playing_state:
            self.status_var.set(f"{len(songs)} TRACK(S) ADDED")

    def add_song_to_playlist(self, song_name, song_path):
        """Add a song to the CustomTkinter playlist"""
        # Create frame for the song entry
        index = len(self.playlist_entries)
        song_frame = ctk.CTkFrame(self.playlist_scrollable, fg_color=COLOR_BLACK, corner_radius=0)
        song_frame.pack(fill="x", pady=2)

        # Create label for the song
        song_label = ctk.CTkLabel(
            song_frame,
            text=song_name,
            font=self.normal_font,
            fg_color=COLOR_BLACK,
            text_color=COLOR_WHITE,
            anchor="w"
        )
        song_label.pack(fill="x", padx=5)

        # Bind click event
        song_label.bind("<Button-1>", lambda e, idx=index: self.select_song(idx))
        song_label.bind("<Double-Button-1>", lambda e, idx=index: self.play_selected_song_by_index(idx))

        # Store reference to frame and label
        self.playlist_entries.append({
            "frame": song_frame,
            "label": song_label,
            "selected": False,
            "index": index # Store index for easier management if needed
        })

    def select_song(self, index):
        """Select a song in the playlist and highlight it red."""
        # Clear previous selection
        for entry in self.playlist_entries:
            entry["frame"].configure(fg_color=COLOR_BLACK)
            entry["label"].configure(fg_color=COLOR_BLACK, text_color=COLOR_WHITE)
            entry["selected"] = False

        # Select new song and highlight it red
        if 0 <= index < len(self.playlist_entries): # Check if index is valid
            self.playlist_entries[index]["frame"].configure(fg_color=COLOR_DEEP_RED)
            self.playlist_entries[index]["label"].configure(fg_color=COLOR_DEEP_RED, text_color=COLOR_WHITE) # Keep text white for contrast
            self.playlist_entries[index]["selected"] = True
        else:
            print(f"Warning: select_song index {index} out of range.")


    def play_selected_song_by_index(self, index):
        """Play the song at the given index and ensure it is selected and highlighted."""
        if 0 <= index < len(self.songs_list): # Check if index is valid
            self.current_song_index = index
            self.select_song(index) # Select and highlight the song before playing
            self.play_music()
        else:
            print(f"Warning: play_selected_song_by_index index {index} out of range.")
            self.status_var.set("INVALID TRACK INDEX")


    def play_selected_song(self, event=None):
        """Play currently selected song"""
        selected_index = -1
        for index, entry in enumerate(self.playlist_entries):
            if entry["selected"]:
                selected_index = index
                break

        if selected_index != -1:
            self.play_selected_song_by_index(selected_index)
        # If no song is selected, try to play the first one
        elif self.playlist_entries:
            self.play_selected_song_by_index(0)
        else:
            self.status_var.set("NO TRACK SELECTED")

    def remove_song(self):
        """Remove selected song from playlist"""
        removed_index = -1
        for index, entry in enumerate(self.playlist_entries):
            if entry["selected"]:
                removed_index = index
                # Remove from UI
                entry["frame"].destroy()
                break # Exit loop after finding and removing the selected song

        if removed_index != -1:
            # Remove from lists
            self.playlist_entries.pop(removed_index)
            self.songs_list.pop(removed_index)

            # Re-index playlist entries after removal
            for i in range(removed_index, len(self.playlist_entries)):
                self.playlist_entries[i]["index"] = i # Update stored index

            # Adjust current song index if needed
            if self.current_song_index >= removed_index:
                self.current_song_index = max(0, self.current_song_index - 1)

            # Clear selection if playlist becomes empty or selection was the last song
            if not self.playlist_entries:
                pass # Playlist is empty, no selection
            elif removed_index <= len(self.playlist_entries): # If removed song was before or at current index
                # If current song index is still valid after removal, re-select it
                if 0 <= self.current_song_index < len(self.playlist_entries):
                    self.select_song(self.current_song_index)
                elif self.playlist_entries: # if playlist is not empty, select first song
                     self.select_song(0)
                else: # if playlist is empty, clear selection
                    pass


            # Update status
            self.status_var.set("TRACK REMOVED")
        else:
            self.status_var.set("NO TRACK SELECTED")


    def clear_playlist(self):
        """Clear the entire playlist"""
        # Stop if playing
        if self.playing_state:
            self.stop()

        # Clear UI
        for entry in self.playlist_entries:
            entry["frame"].destroy()

        # Clear data
        self.playlist_entries.clear()
        self.songs_list.clear()
        self.current_song_index = 0

        # Update status
        self.status_var.set("PLAYLIST CLEARED")

    def play(self):
        """Play button handler"""
        if self.songs_list:
            if self.paused:
                # Resume paused song
                self.play_button.configure(fg_color=COLOR_DEEP_RED) # Make button red on press
                self.root.after(100, lambda: self.play_button.configure(fg_color=COLOR_BLACK)) # Revert color after 100ms
                pygame.mixer.music.unpause()
                self.paused = False
                self.playing_state = True
                self.status_var.set("PLAYING")
                self.start_update_thread()
            elif not self.playing_state: # If stopped and play is pressed
                if self.current_song: # if a song was loaded before stop
                    try:
                        self.play_button.configure(fg_color=COLOR_DEEP_RED) # Make button red on press
                        self.root.after(100, lambda: self.play_button.configure(fg_color=COLOR_BLACK)) # Revert color after 100ms
                        pygame.mixer.music.load(self.current_song)
                        pygame.mixer.music.play(0, self.stopped_position) # Resume from stopped position
                        self.playing_state = True
                        self.paused = False
                        self.status_var.set("PLAYING")
                        self.start_update_thread()
                        # Ensure current song is highlighted when resuming play
                        self.select_song(self.current_song_index)
                    except Exception as e:
                        self.status_var.set(f"ERROR: {str(e)}")
                else: # if no song was loaded, play from start of playlist
                    self.play_music()
            else:
                # if already playing, do nothing
                pass
        else:
            self.status_var.set("PLAYLIST EMPTY")

    def play_music(self):
        """Play the current song"""
        if self.songs_list:
            # Get current song
            self.current_song = self.songs_list[self.current_song_index]

            try:
                # Generate waveform data
                self.generate_waveform_data()

                # Draw static waveform
                self.draw_static_waveform()

                # Load and play the song
                pygame.mixer.music.load(self.current_song)
                pygame.mixer.music.play()

                # Update state variables
                self.playing_state = True
                self.paused = False

                # Update UI
                self.update_song_info()
                self.select_song(self.current_song_index) # Ensure current song is highlighted when starting play

                # Start thread to update slider
                self.start_update_thread()

                # Set status
                self.status_var.set("PLAYING")
            except Exception as e:
                self.status_var.set(f"ERROR: {str(e)}")

    def update_song_info(self):
        """Update song information in the UI"""
        # Get song name
        song_name = os.path.basename(self.current_song)
        self.song_title_var.set(song_name)

        # Get song length
        try:
            audio = MP3(self.current_song)
            self.song_length = audio.info.length
            # Convert to time format
            mins, secs = divmod(int(self.song_length), 60)
            self.total_time = f"{mins:02d}:{secs:02d}"
            self.total_time_label.configure(text=self.total_time)

            # Set slider maximum
            self.song_slider.configure(to=int(self.song_length))
            self.song_slider.configure(to=self.song_length) # Set slider max to song length
        except Exception as e:
            # Default values if song length can't be determined
            print(f"Error getting song info: {e}")
            self.song_length = 0
            self.total_time = "00:00"
            self.total_time_label.configure(text=self.total_time)
            self.song_slider.configure(to=100) # Fallback to a default max if length is unknown

    def generate_waveform_data(self):
        """Generate waveform data from the current song"""
        try:
            # Status update
            self.status_var.set("GENERATING WAVEFORM...")
            self.root.update()

            # Convert MP3 to temporary WAV for processing
            sound = AudioSegment.from_file(self.current_song)

            # Get audio data
            samples = sound.get_array_of_samples()

            # For stereo, take average of channels
            if sound.channels == 2:
                samples = np.array(samples).reshape((-1, 2))
                samples = samples.mean(axis=1)

            # Reduce data points for visualization
            # We'll take max value in chunks to preserve peaks
            chunk_size = max(1, len(samples) // 300)  # Divide into ~300 data points
            self.waveform_data = []

            for i in range(0, len(samples), chunk_size):
                chunk = samples[i:i+chunk_size]
                if len(chunk) > 0:
                    # Get normalized value (-1 to 1)
                    value = np.abs(chunk).max() / 32768.0  # Assuming 16-bit audio
                    self.waveform_data.append(value)

            # Reset position
            self.waveform_position = 0

            # Status update
            self.status_var.set("WAVEFORM READY")
            self.root.update()

        except Exception as e:
            print(f"Error generating waveform: {e}")
            self.waveform_data = [0] * 100  # Default empty waveform
            self.status_var.set("WAVEFORM ERROR")

    def draw_static_waveform(self):
        """Draw the static waveform on canvas in solid white and store as image"""
        if not self.waveform_data:
            self.draw_waveform_grid()
            return

        # Get canvas dimensions
        width = self.waveform_canvas.winfo_width() or 460
        height = self.waveform_canvas.winfo_height() or 200

        # Clear canvas
        self.waveform_canvas.delete("all")

        # Draw grid
        self.draw_waveform_grid()

        # Draw waveform
        center_y = height / 2
        max_amplitude = height / 2 - 10  # Leave some margin

        # Calculate width per segment
        segment_width = width / len(self.waveform_data)

        # Draw each segment of the waveform in solid white
        for i, amplitude in enumerate(self.waveform_data):
            x = i * segment_width
            bar_height = amplitude * max_amplitude

            # Draw bar (from center up and down)
            self.waveform_canvas.create_line(
                x, center_y - bar_height,
                x, center_y + bar_height,
                fill=COLOR_WHITE, width=1
            )

    def draw_waveform_position_indicator(self, position_ratio):
        """Draw only the position indicator on the waveform canvas"""
        width = self.waveform_canvas.winfo_width() or 460
        height = self.waveform_canvas.winfo_height() or 200

        # Delete previous position indicator
        self.waveform_canvas.delete("position_indicator")

        # Calculate position
        position_x = int(width * position_ratio)

        # Draw position indicator - Deep Red, tagged as "position_indicator" for deletion
        self.waveform_canvas.create_line(
            position_x, 0, position_x, height,
            fill=COLOR_DEEP_RED, width=2, tag="position_indicator"  # Thicker indicator, tagged
        )


    def pause(self):
        """Pause button handler"""
        if self.playing_state and not self.paused:
            self.pause_button.configure(fg_color=COLOR_DEEP_RED) # Make button red on press
            self.root.after(100, lambda: self.pause_button.configure(fg_color=COLOR_BLACK)) # Revert color after 100ms
            pygame.mixer.music.pause()
            self.paused = True
            self.status_var.set("PAUSED")
        elif self.paused:
            self.pause_button.configure(fg_color=COLOR_DEEP_RED) # Make button red on press
            self.root.after(100, lambda: self.pause_button.configure(fg_color=COLOR_BLACK)) # Revert color after 100ms
            pygame.mixer.music.unpause()
            self.paused = False
            self.status_var.set("PLAYING")
            self.start_update_thread()

    def stop(self):
        """Stop button handler"""
        if self.playing_state:
            self.stopped_position = self.song_time # Store current song time as stopped position
            pygame.mixer.music.stop()
            self.playing_state = False
            self.paused = False
            self.status_var.set("STOPPED")

            # Reset slider and time display - No Reset, keep current position displayed
            # self.song_slider.set(0)
            # self.current_time_label.configure(text="00:00")

            # Reset waveform position - No Reset, keep current position displayed
            # self.draw_waveform(0)

            # Stop thread
            self.thread_running = False

    def previous_song(self):
        """Play previous song in playlist"""
        if self.songs_list:
            # Decrease index or loop to end
            if self.current_song_index > 0:
                self.current_song_index -= 1
            else:
                self.current_song_index = len(self.songs_list) - 1

            # Stop current and play new
            pygame.mixer.music.stop()
            self.thread_running = False
            self.stopped_position = 0.0 # Reset stopped position when changing song
            self.play_music()

    def next_song(self):
        """Play next song in playlist"""
        if self.songs_list:
            # Increase index or loop to start
            if self.current_song_index < len(self.songs_list) - 1:
                self.current_song_index += 1
            else:
                self.current_song_index = 0

            # Stop current and play new
            pygame.mixer.music.stop()
            self.thread_running = False
            self.stopped_position = 0.0 # Reset stopped position when changing song
            self.play_music()

    def volume_adjust(self, value):
        """Adjust volume level"""
        volume = float(value)
        pygame.mixer.music.set_volume(volume)

        # Update mute state if volume > 0
        if volume > 0:
            self.previous_volume = volume
            self.muted = False
            self.volume_button.configure(text="VOL", text_color=COLOR_WHITE)  # Reset to white and "VOL"
        else:
            self.muted = True
            self.volume_button.configure(text="MUTED", text_color=COLOR_DEEP_RED)  # Deep Red for mute and "MUTED"

    def toggle_mute(self):
        """Toggle mute/unmute"""
        if self.muted:
            # Unmute
            pygame.mixer.music.set_volume(self.previous_volume)
            self.volume_slider.set(self.previous_volume)
            self.muted = False
            self.volume_button.configure(text="VOL", text_color=COLOR_WHITE)  # Reset to white and "VOL"
        else:
            # Mute
            self.previous_volume = pygame.mixer.music.get_volume()
            pygame.mixer.music.set_volume(0)
            self.volume_slider.set(0)
            self.muted = True
            self.volume_button.configure(text="MUTED", text_color=COLOR_DEEP_RED)  # Deep Red for mute and "MUTED"

    def toggle_shuffle(self):
        """Toggle shuffle mode"""
        if self.shuffle_state:
            self.shuffle_state = False
            self.shuffle_button.configure(text_color=COLOR_WHITE)  # Reset to white
            self.status_var.set("SHUFFLE OFF")
        else:
            self.shuffle_state = True
            self.shuffle_button.configure(text_color=COLOR_DEEP_RED)  # Deep Red when active
            self.status_var.set("SHUFFLE ON")

    def toggle_loop(self): # <- Renamed toggle_repeat to toggle_loop
        """Toggle loop mode (none, all, one)""" # <- Renamed repeat mode to loop mode
        # Cycle through loop states
        self.loop_state = (self.loop_state + 1) % 3 # <- Renamed repeat_state to loop_state

        # Update UI
        if self.loop_state == 0: # <- Renamed repeat_state to loop_state
            # No loop
            self.loop_button.configure(text_color=COLOR_WHITE, text="LOOP")  # Reset to white # <- Renamed repeat_button to loop_button, text to LOOP
            self.status_var.set("LOOP OFF") # <- Changed status to LOOP OFF
        elif self.loop_state == 1: # <- Renamed repeat_state to loop_state
            # Loop all
            self.loop_button.configure(text_color=COLOR_DEEP_RED, text="LOOP ALL")  # Deep Red when active # <- Renamed repeat_button to loop_button, text to LOOP ALL
            self.status_var.set("LOOP ALL") # <- Changed status to LOOP ALL
        else:
            # Loop one
            self.loop_button.configure(text_color=COLOR_DEEP_RED, text="LOOP ONE")  # Deep Red when active # <- Renamed repeat_button to loop_button, text to LOOP ONE
            self.status_var.set("LOOP ONE") # <- Changed status to LOOP ONE

    def slider_start_scroll(self, event):
        """Called when slider scrolling starts"""
        self.slider_active = True

    def slider_stop_scroll(self, event):
        """Called when slider scrolling stops"""
        self.slider_active = False

    def slide_song(self, value):
        """Handle song position slider change."""
        if not self.slider_active:  # Ignore programmatic slider updates
            return

        # Convert to float
        position = float(value)
        self.song_time = position # Update song_time immediately

        # Calculate position ratio for waveform
        position_ratio = position / self.song_length
        self.draw_waveform_position_indicator(position_ratio) # Draw position indicator immediately

        # Update time labels immediately
        mins, secs = divmod(int(position), 60)
        self.current_time_label.configure(text=f"{mins:02d}:{secs:02d}")

        if self.playing_state:
            # Stop the music to prevent overlap, then play from new position
            pygame.mixer.music.stop()
            try:
                pygame.mixer.music.play(0, position) # Play from the selected position (seconds)
                self.start_update_thread() # Restart thread after slide
            except pygame.error as e:
                print(f"Pygame error on seek: {e}")
                self.status_var.set("ERROR SEEKING TRACK")
                self.stop() # Stop playback in case of error
            if self.paused: # if paused when sliding, keep paused
                pygame.mixer.music.pause()


    def update_song_position(self):
        """Update song slider position and time labels"""
        if self.slider_active: # Do not update from thread if slider is being used
            return

        if self.playing_state and not self.paused and self.song_length > 0:
            self.song_time = pygame.mixer.music.get_pos() / 1000.0  # Get current position in seconds, use float division
            # Ensure song_time is not greater than song_length (for edge cases)
            self.song_time = min(self.song_time, self.song_length)

            # Update slider position, use set without trigger to avoid loop
            self.song_slider.set(self.song_time)

            # Update time labels
            mins, secs = divmod(int(self.song_time), 60)
            self.time_elapsed = f"{mins:02d}:{secs:02d}"
            self.current_time_label.configure(text=self.time_elapsed)

            # Calculate position ratio for waveform
            if self.song_length > 0:
                position_ratio = self.song_time / self.song_length
                self.draw_waveform_position_indicator(position_ratio) # Call draw_waveform_position_indicator here to update position
            else:
                self.draw_waveform_position_indicator(0) # Default to 0 if song_length is not available


    def start_update_thread(self):
        """Start a thread to update the song position periodically"""
        if not self.thread_running: # Prevent starting multiple threads
            self.thread_running = True
            if self.update_thread is None or not self.update_thread.is_alive():
                self.update_thread = threading.Thread(target=self.update_time)
                self.update_thread.daemon = True  # Allow main thread to exit without waiting
                self.update_thread.start()

    def update_time(self):
        """Function to be run in a separate thread to update time and check song end"""
        while self.thread_running and self.playing_state and not self.paused:
            self.update_song_position()
            self.check_music_end()
            time.sleep(0.1)  # Update every 100ms
        self.thread_running = False # Reset thread_running when loop finishes (after stop/pause)


    def check_music_end(self):
        """Check if the music has ended and handle next steps"""
        if self.playing_state and not pygame.mixer.music.get_busy():
            self.playing_state = False # Set playing state to false as song ended
            if self.loop_state == 2:  # Loop one # <- Renamed repeat_state to loop_state
                self.play_music()  # Replay current song
            elif self.loop_state == 1:  # Loop all # <- Renamed repeat_state to loop_state
                self.next_song()  # Play next song in playlist, loops back if needed
            elif self.shuffle_state:
                self.play_random_song()
            else:
                if self.current_song_index < len(self.songs_list) - 1:
                    self.next_song()  # Play next song in order
                else:
                    self.stop() # Stop after playlist ends if no loop and no shuffle


    def play_random_song(self):
        """Play a random song from the playlist"""
        if len(self.songs_list) > 1:
            next_index = random.choice([i for i in range(len(self.songs_list)) if i != self.current_song_index]) # Avoid playing current song again immediately
            self.current_song_index = next_index
        elif len(self.songs_list) == 1:
            pass # Only one song, just stop after it finishes if not looping
        else:
            return # Playlist empty, nothing to play
        pygame.mixer.music.stop()
        self.thread_running = False
        self.stopped_position = 0.0 # Reset stopped position when changing song
        self.play_music()


    def on_closing(self):
        """Handle window closing event"""
        self.thread_running = False  # Stop update thread
        pygame.mixer.music.stop() # Stop music
        self.root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    player = CyberpunkMusicPlayer(root)
    root.mainloop()