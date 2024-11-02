import sounddevice as sd
import numpy as np
import pycaw.pycaw as pycaw
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import queue
import time
import json
import os
from pygame import mixer
import colorsys

class VolumeControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Voice Volume Controller")
        self.root.geometry("1000x800")
        
        # Initialize pygame mixer for audio feedback
        mixer.init()
        
        # Variables
        self.is_monitoring = False
        self.is_calibrating = False
        self.sensitivity = tk.DoubleVar(value=1.0)
        self.current_volume = tk.DoubleVar(value=0.0)
        self.current_intensity = tk.DoubleVar(value=0.0)
        self.visualization_mode = tk.StringVar(value="Line Graph")
        self.audio_feedback = tk.BooleanVar(value=True)
        self.data_queue = queue.Queue()
        
        # Calibration variables
        self.calibration_samples = []
        self.calibration_min = 0
        self.calibration_max = 100
        
        # History for plotting
        self.intensity_history = []
        self.volume_history = []
        self.max_history = 100
        
        # Load presets
        self.presets = self.load_presets()
        
        self._create_gui()
        self._setup_plot()
        
        # Start update loop
        self.root.after(100, self._update_gui)

    def _create_gui(self):
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Main control tab
        main_tab = ttk.Frame(self.notebook)
        self.notebook.add(main_tab, text="Main Controls")
        
        # Presets tab
        presets_tab = ttk.Frame(self.notebook)
        self.notebook.add(presets_tab, text="Presets")
        
        # Settings tab
        settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(settings_tab, text="Settings")
        
        # Setup each tab
        self._setup_main_tab(main_tab)
        self._setup_presets_tab(presets_tab)
        self._setup_settings_tab(settings_tab)

    def _setup_main_tab(self, parent):
        # Control frame
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="10")
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Start/Stop button
        self.toggle_button = ttk.Button(control_frame, text="Start Monitoring",
                                      command=self._toggle_monitoring)
        self.toggle_button.pack(side=tk.LEFT, padx=5)
        
        # Calibration button
        self.calibrate_button = ttk.Button(control_frame, text="Calibrate",
                                         command=self._start_calibration)
        self.calibrate_button.pack(side=tk.LEFT, padx=5)
        
        # Sensitivity control
        sensitivity_frame = ttk.LabelFrame(parent, text="Sensitivity", padding="10")
        sensitivity_frame.pack(fill=tk.X, padx=5, pady=5)
        
        sensitivity_slider = ttk.Scale(sensitivity_frame, from_=0.1, to=2.0,
                                     orient=tk.HORIZONTAL, variable=self.sensitivity)
        sensitivity_slider.pack(fill=tk.X, padx=5)
        
        # Metrics frame
        metrics_frame = ttk.LabelFrame(parent, text="Current Metrics", padding="10")
        metrics_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Volume indicator
        ttk.Label(metrics_frame, text="Volume:").pack(side=tk.LEFT, padx=5)
        self.volume_bar = ttk.Progressbar(metrics_frame, length=200, mode='determinate')
        self.volume_bar.pack(side=tk.LEFT, padx=5)
        
        # Intensity indicator
        ttk.Label(metrics_frame, text="Intensity (dB):").pack(side=tk.LEFT, padx=5)
        self.intensity_bar = ttk.Progressbar(metrics_frame, length=200, mode='determinate')
        self.intensity_bar.pack(side=tk.LEFT, padx=5)
        
        # Visualization frame
        viz_frame = ttk.LabelFrame(parent, text="Visualization", padding="10")
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Visualization mode selector
        viz_modes = ["Line Graph", "Bar Graph", "Spectrum", "Circular"]
        viz_selector = ttk.OptionMenu(viz_frame, self.visualization_mode, 
                                    self.visualization_mode.get(), *viz_modes,
                                    command=self._change_visualization)
        viz_selector.pack(side=tk.TOP, padx=5, pady=5)
        
        # Plot frame
        self.plot_frame = ttk.Frame(viz_frame)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)

    def _setup_presets_tab(self, parent):
        # Presets list
        presets_frame = ttk.LabelFrame(parent, text="Volume Presets", padding="10")
        presets_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Preset controls
        controls_frame = ttk.Frame(presets_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # New preset entry
        self.preset_name = tk.StringVar()
        preset_entry = ttk.Entry(controls_frame, textvariable=self.preset_name)
        preset_entry.pack(side=tk.LEFT, padx=5)
        
        # Save preset button
        save_btn = ttk.Button(controls_frame, text="Save Current Settings",
                             command=self._save_preset)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # Presets listbox
        self.presets_list = tk.Listbox(presets_frame, height=10)
        self.presets_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._update_presets_list()
        
        # Load and Delete buttons
        btn_frame = ttk.Frame(presets_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        load_btn = ttk.Button(btn_frame, text="Load Selected",
                             command=self._load_preset)
        load_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = ttk.Button(btn_frame, text="Delete Selected",
                               command=self._delete_preset)
        delete_btn.pack(side=tk.LEFT, padx=5)

    def _setup_settings_tab(self, parent):
        settings_frame = ttk.LabelFrame(parent, text="Application Settings", padding="10")
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Audio feedback toggle
        feedback_check = ttk.Checkbutton(settings_frame, text="Enable Audio Feedback",
                                       variable=self.audio_feedback)
        feedback_check.pack(anchor=tk.W, padx=5, pady=5)
        
        # History length control
        history_frame = ttk.Frame(settings_frame)
        history_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(history_frame, text="History Length:").pack(side=tk.LEFT)
        history_scale = ttk.Scale(history_frame, from_=50, to=500,
                                orient=tk.HORIZONTAL,
                                command=lambda v: self._set_history_length(int(float(v))))
        history_scale.set(self.max_history)
        history_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    def _setup_plot(self):
        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize different visualization types
        self._setup_line_plot()

    def _setup_line_plot(self):
        self.ax.clear()
        self.intensity_line, = self.ax.plot([], [], label='Intensity', color='blue')
        self.volume_line, = self.ax.plot([], [], label='Volume', color='red')
        self.ax.set_ylim(-10, 100)
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Level')
        self.ax.legend()
        self.ax.grid(True)

    def _setup_bar_plot(self):
        self.ax.clear()
        self.ax.set_ylim(0, 100)
        self.ax.set_xlabel('Metric')
        self.ax.set_ylabel('Level')

    def _setup_spectrum_plot(self):
        self.ax.clear()
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, 100)
        self.ax.set_xlabel('Frequency')
        self.ax.set_ylabel('Magnitude')

    def _setup_circular_plot(self):
        self.ax.clear()
        self.ax.set_aspect('equal')
        self.ax.set_xlim(-1.2, 1.2)
        self.ax.set_ylim(-1.2, 1.2)

    def _change_visualization(self, mode):
        if mode == "Line Graph":
            self._setup_line_plot()
        elif mode == "Bar Graph":
            self._setup_bar_plot()
        elif mode == "Spectrum":
            self._setup_spectrum_plot()
        else:  # Circular
            self._setup_circular_plot()

    def _update_plot(self):
        mode = self.visualization_mode.get()
        
        if mode == "Line Graph":
            self._update_line_plot()
        elif mode == "Bar Graph":
            self._update_bar_plot()
        elif mode == "Spectrum":
            self._update_spectrum_plot()
        else:  # Circular
            self._update_circular_plot()
        
        self.canvas.draw()

    def _update_line_plot(self):
        if len(self.intensity_history) > self.max_history:
            self.intensity_history = self.intensity_history[-self.max_history:]
            self.volume_history = self.volume_history[-self.max_history:]
            
        x = range(len(self.intensity_history))
        self.intensity_line.set_data(x, self.intensity_history)
        self.volume_line.set_data(x, [v * 100 for v in self.volume_history])
        self.ax.set_xlim(0, max(self.max_history, len(x)))

    def _update_bar_plot(self):
        self.ax.clear()
        self.ax.bar(['Intensity', 'Volume'], 
                   [self.current_intensity.get(), self.current_volume.get() * 100],
                   color=['blue', 'red'])
        self.ax.set_ylim(0, 100)

    def _update_spectrum_plot(self):
        self.ax.clear()
        # Create a simple spectrum-like visualization
        x = np.linspace(0, 100, 100)
        intensity = self.current_intensity.get()
        volume = self.current_volume.get() * 100
        y = intensity * np.exp(-x/20) + volume * np.exp(-x/30)
        self.ax.fill_between(x, y, alpha=0.5)
        self.ax.set_ylim(0, 100)

    def _update_circular_plot(self):
        self.ax.clear()
        self.ax.set_aspect('equal')
        
        # Create circular visualization
        intensity = self.current_intensity.get() / 100
        volume = self.current_volume.get()
        
        # Draw intensity circle
        intensity_circle = plt.Circle((0, 0), intensity, 
                                    color='blue', alpha=0.3)
        self.ax.add_artist(intensity_circle)
        
        # Draw volume circle
        volume_circle = plt.Circle((0, 0), volume, 
                                 color='red', alpha=0.3)
        self.ax.add_artist(volume_circle)
        
        self.ax.set_xlim(-1.2, 1.2)
        self.ax.set_ylim(-1.2, 1.2)

    def _start_calibration(self):
        if not self.is_calibrating:
            self.is_calibrating = True
            self.calibration_samples = []
            self.calibrate_button.configure(text="Stop Calibration")
            messagebox.showinfo("Calibration Started", 
                              "Please make sounds at various volumes for calibration.\n"
                              "Click 'Stop Calibration' when done.")
        else:
            self._finish_calibration()

    def _finish_calibration(self):
        self.is_calibrating = False
        self.calibrate_button.configure(text="Calibrate")
        
        if len(self.calibration_samples) > 0:
            self.calibration_min = min(self.calibration_samples)
            self.calibration_max = max(self.calibration_samples)
            messagebox.showinfo("Calibration Complete",
                              f"Calibration range: {self.calibration_min:.1f} - "
                              f"{self.calibration_max:.1f} dB")

    def _calculate_volume_from_intensity(self, intensity):
        if self.is_calibrating:
            self.calibration_samples.append(intensity)
            return self.current_volume.get()
            
        # Use calibration values if available
        min_intensity = self.calibration_min if self.calibration_min != 0 else 0
        max_intensity = self.calibration_max if self.calibration_max != 100 else 100
        
        normalized = (intensity - min_intensity) / (max_intensity - min_intensity)
        normalized *= self.sensitivity.get()
        return min(max(normalized, 0), 1)

    def load_presets(self):
        try:
            with open('volume_presets.json', 'r')