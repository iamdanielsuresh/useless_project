import sounddevice as sd
import numpy as np
import pycaw.pycaw as pycaw
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math
import tkinter as tk
from tkinter import ttk
import threading
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import queue
import time

class VolumeControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Volume Controller")
        self.root.geometry("800x600")
        
        # Variables
        self.is_monitoring = False
        self.sensitivity = tk.DoubleVar(value=1.0)
        self.current_volume = tk.DoubleVar(value=0.0)
        self.current_intensity = tk.DoubleVar(value=0.0)
        self.data_queue = queue.Queue()
        
        # History for plotting
        self.intensity_history = []
        self.volume_history = []
        self.max_history = 100
        
        self._create_gui()
        self._setup_plot()
        
        # Start update loop
        self.root.after(100, self._update_gui)

    def _create_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Control frame
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Start/Stop button
        self.toggle_button = ttk.Button(control_frame, text="Start Monitoring",
                                      command=self._toggle_monitoring)
        self.toggle_button.grid(row=0, column=0, padx=5)
        
        # Sensitivity slider
        ttk.Label(control_frame, text="Sensitivity:").grid(row=0, column=1, padx=5)
        sensitivity_slider = ttk.Scale(control_frame, from_=0.1, to=2.0,
                                     orient=tk.HORIZONTAL, variable=self.sensitivity)
        sensitivity_slider.grid(row=0, column=2, padx=5, sticky=(tk.W, tk.E))
        
        # Metrics frame
        metrics_frame = ttk.LabelFrame(main_frame, text="Current Metrics", padding="10")
        metrics_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Volume indicator
        ttk.Label(metrics_frame, text="Volume:").grid(row=0, column=0, padx=5)
        self.volume_bar = ttk.Progressbar(metrics_frame, length=200, mode='determinate')
        self.volume_bar.grid(row=0, column=1, padx=5)
        
        # Intensity indicator
        ttk.Label(metrics_frame, text="Intensity (dB):").grid(row=1, column=0, padx=5)
        self.intensity_bar = ttk.Progressbar(metrics_frame, length=200, mode='determinate')
        self.intensity_bar.grid(row=1, column=1, padx=5)
        
        # Plot frame
        self.plot_frame = ttk.Frame(main_frame)
        self.plot_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        control_frame.columnconfigure(2, weight=1)

    def _setup_plot(self):
        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initial plot setup
        self.intensity_line, = self.ax.plot([], [], label='Intensity', color='blue')
        self.volume_line, = self.ax.plot([], [], label='Volume', color='red')
        self.ax.set_ylim(-10, 100)
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Level')
        self.ax.legend()
        self.ax.grid(True)

    def _update_plot(self):
        if len(self.intensity_history) > self.max_history:
            self.intensity_history = self.intensity_history[-self.max_history:]
            self.volume_history = self.volume_history[-self.max_history:]
            
        x = range(len(self.intensity_history))
        self.intensity_line.set_data(x, self.intensity_history)
        self.volume_line.set_data(x, [v * 100 for v in self.volume_history])
        
        self.ax.set_xlim(0, max(self.max_history, len(x)))
        self.canvas.draw()

    def _toggle_monitoring(self):
        if not self.is_monitoring:
            self.is_monitoring = True
            self.toggle_button.configure(text="Stop Monitoring")
            self._start_monitoring()
        else:
            self.is_monitoring = False
            self.toggle_button.configure(text="Start Monitoring")

    def _start_monitoring(self):
        def audio_callback(indata, frames, time, status):
            if status:
                print(status)
            
            if not self.is_monitoring:
                raise sd.CallbackStop()
            
            volume_norm = np.linalg.norm(indata) * 10
            intensity = 20 * math.log10(volume_norm) if volume_norm > 0 else 0
            new_volume = self._calculate_volume_from_intensity(intensity)
            self._set_system_volume(new_volume)
            
            self.data_queue.put((intensity, new_volume))

        try:
            self.stream = sd.InputStream(
                callback=audio_callback,
                channels=1,
                samplerate=44100,
                blocksize=int(44100 * 0.1)
            )
            self.stream.start()
        except Exception as e:
            print(f"Error starting audio stream: {str(e)}")
            self.is_monitoring = False
            self.toggle_button.configure(text="Start Monitoring")

    def _calculate_volume_from_intensity(self, intensity):
        min_intensity = 0
        max_intensity = 100
        normalized = (intensity - min_intensity) / (max_intensity - min_intensity)
        normalized *= self.sensitivity.get()  # Apply sensitivity multiplier
        return min(max(normalized, 0), 1)

    def _set_system_volume(self, volume_level):
        volume_level = max(0.0, min(1.0, volume_level))
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(volume_level, None)

    def _update_gui(self):
        # Process any new data
        try:
            while True:
                intensity, volume = self.data_queue.get_nowait()
                self.current_intensity.set(intensity)
                self.current_volume.set(volume)
                
                self.intensity_history.append(intensity)
                self.volume_history.append(volume)
                
                # Update progress bars
                self.volume_bar['value'] = volume * 100
                self.intensity_bar['value'] = min(100, intensity)
                
                self._update_plot()
                
        except queue.Empty:
            pass
        
        # Schedule next update
        self.root.after(100, self._update_gui)

def main():
    root = tk.Tk()
    app = VolumeControlApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
