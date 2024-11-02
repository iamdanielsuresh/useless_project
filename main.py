import sounddevice as sd
import numpy as np
import math
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib as plt
import threading
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import queue
import time
import json
import os
import platform
import subprocess
from pygame import mixer
import logging


# Set up logging
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('volume_control.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('VolumeControl')

logger = setup_logging()


class Config:
    def __init__(self):
        self.config_file = "volume_control_config.json"
        self.defaults = {
            "sensitivity": 1.0,
            "max_history": 100,
            "update_interval": 100,
            "audio_feedback": True,
            "visualization_mode": "Line Graph",
            "calibration": {
                "min": 0,
                "max": 100
            }
        }
        self.settings = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                return {**self.defaults, **json.load(f)}
        except FileNotFoundError:
            return self.defaults

    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

class VolumeFilter:
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.volume_history = []

    def smooth_volume(self, new_volume):
        self.volume_history.append(new_volume)
        if len(self.volume_history) > self.window_size:
            self.volume_history.pop(0)
        return sum(self.volume_history) / len(self.volume_history)

    
                

class VolumeController:
    """Cross-platform volume control implementation"""
    def __init__(self):
        self.system = platform.system()
        try:
            if self.system == "Windows":
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self.volume = cast(interface, POINTER(IAudioEndpointVolume))
            logger.info(f"Volume controller initialized for {self.system}")
        except Exception as e:
            logger.error(f"Failed to initialize volume controller: {e}")
            raise

    def set_volume(self, volume_level):
        """Set system volume (0.0 to 1.0)"""
        try:
            volume_level = max(0.0, min(1.0, volume_level))
            
            if self.system == "Windows":
                self.volume.SetMasterVolumeLevelScalar(volume_level, None)
            elif self.system == "Darwin":  # macOS
                volume_level_percent = int(volume_level * 100)
                os.system(f"osascript -e 'set volume output volume {volume_level_percent}'")
            elif self.system == "Linux":
                volume_level_percent = int(volume_level * 100)
                os.system(f"amixer -D pulse sset Master {volume_level_percent}%")
            logger.debug(f"Volume set to {volume_level}")
        except Exception as e:
            logger.error(f"Failed to set volume: {e}")
            raise

    def get_volume(self):
        """Get current system volume (0.0 to 1.0)"""
        try:
            if self.system == "Windows":
                return self.volume.GetMasterVolumeLevelScalar()
            elif self.system == "Darwin":  # macOS
                cmd = "osascript -e 'output volume of (get volume settings)'"
                result = subprocess.check_output(cmd, shell=True).strip()
                return float(result) / 100.0
            elif self.system == "Linux":
                cmd = "amixer -D pulse sget Master | grep 'Left:' | awk -F'[][]' '{ print $2 }'"
                result = subprocess.check_output(cmd, shell=True).strip()
                return float(result.decode('utf-8').replace('%', '')) / 100.0
        except Exception as e:
            logger.error(f"Failed to get volume: {e}")
            return 0.0


class VolumeControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Volume Controller")
        self.root.geometry("1000x800")
        
        # Initialize configuration
        self.config = Config()
        
        # Initialize volume controller
        try:
            self.volume_controller = VolumeController()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize volume controller: {str(e)}")
            self.root.destroy()
            return
            
        # Initialize pygame mixer for audio feedback
        try:
            mixer.init()
        except Exception as e:
            logger.warning(f"Failed to initialize audio feedback: {e}")
        
        # Initialize volume filter
        self.volume_filter = VolumeFilter()
        
        # Variables
        self.is_monitoring = False
        self.is_calibrating = False
        self.sensitivity = tk.DoubleVar(value=self.config.settings["sensitivity"])
        self.current_volume = tk.DoubleVar(value=self.volume_controller.get_volume())
        self.current_intensity = tk.DoubleVar(value=0.0)
        self.visualization_mode = tk.StringVar(value=self.config.settings["visualization_mode"])
        self.audio_feedback = tk.BooleanVar(value=self.config.settings["audio_feedback"])
        self.data_queue = queue.Queue()
        
        # Performance optimization variables
        self.update_interval = self.config.settings["update_interval"]
        self.last_plot_update = 0
        self.plot_update_interval = 250  # ms
        
        # Calibration variables
        self.calibration_samples = []
        self.calibration_min = self.config.settings["calibration"]["min"]
        self.calibration_max = self.config.settings["calibration"]["max"]
        
        # History for plotting
        self.intensity_history = []
        self.volume_history = []
        self.max_history = self.config.settings["max_history"]
        
        # Create GUI
        self._create_gui()
        self._setup_plot()
        self._setup_shortcuts()
        
        # Start update loop
        self.root.after(self.update_interval, self._update_gui)
        
        logger.info("Application initialized successfully")

    def _setup_shortcuts(self):
        self.root.bind('<space>', lambda e: self._toggle_monitoring())
        self.root.bind('<c>', lambda e: self._start_calibration())
        self.root.bind('<Escape>', lambda e: self.root.quit())
        self.root.bind('<Up>', lambda e: self._adjust_sensitivity(0.1))
        self.root.bind('<Down>', lambda e: self._adjust_sensitivity(-0.1))

    def _adjust_sensitivity(self, delta):
        new_value = self.sensitivity.get() + delta
        self.sensitivity.set(max(0.1, min(2.0, new_value)))
        self.config.settings["sensitivity"] = self.sensitivity.get()
        self.config.save_config()

    def _start_monitoring(self):
        def audio_callback(indata, frames, time, status):
            try:
                if status:
                    logger.warning(f"Audio callback status: {status}")
                
                if not self.is_monitoring:
                    raise sd.CallbackStop()
                
                volume_norm = np.linalg.norm(indata) * 10
                intensity = 20 * math.log10(volume_norm) if volume_norm > 0 else 0
                new_volume = self._calculate_volume_from_intensity(intensity)
                
                # Apply smoothing filter
                smoothed_volume = self.volume_filter.smooth_volume(new_volume)
                
                try:
                    self.volume_controller.set_volume(smoothed_volume)
                except Exception as e:
                    logger.error(f"Failed to set volume: {e}")
                    self._handle_volume_control_error()
                
                self.data_queue.put((intensity, smoothed_volume))
            except Exception as e:
                logger.error(f"Audio callback error: {e}")
                self._attempt_stream_recovery()

        try:
            self.stream = sd.InputStream(
                callback=audio_callback,
                channels=1,
                samplerate=44100,
                blocksize=int(44100 * 0.1)
            )
            self.stream.start()
            logger.info("Audio monitoring started")
        except Exception as e:
            logger.error(f"Failed to start audio stream: {e}")
            self.is_monitoring = False
            self.toggle_button.configure(text="Start Monitoring")
            messagebox.showerror("Error", f"Failed to start audio monitoring: {str(e)}")

    def _attempt_stream_recovery(self):
        """Attempt to recover from stream errors"""
        try:
            if hasattr(self, 'stream'):
                self.stream.stop()
            time.sleep(1)
            self._start_monitoring()
            logger.info("Stream recovery successful")
        except Exception as e:
            logger.error(f"Stream recovery failed: {e}")
            self.is_monitoring = False
            self.root.after(0, self._update_monitoring_state)

    def _handle_volume_control_error(self):
        """Handle volume control errors"""
        try:
            self.volume_controller = VolumeController()
            logger.info("Volume controller reinitialized")
        except Exception as e:
            logger.error(f"Failed to reinitialize volume controller: {e}")
            self.is_monitoring = False
            self.root.after(0, self._update_monitoring_state)
        

    def _create_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Control frame
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
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
        sensitivity_frame = ttk.LabelFrame(main_frame, text="Sensitivity", padding="10")
        sensitivity_frame.pack(fill=tk.X, padx=5, pady=5)
        
        sensitivity_slider = ttk.Scale(sensitivity_frame, from_=0.1, to=2.0,
                                     orient=tk.HORIZONTAL, variable=self.sensitivity)
        sensitivity_slider.pack(fill=tk.X, padx=5)
        
        # Metrics frame
        metrics_frame = ttk.LabelFrame(main_frame, text="Current Metrics", padding="10")
        metrics_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Volume indicator
        volume_frame = ttk.Frame(metrics_frame)
        volume_frame.pack(fill=tk.X, pady=2)
        ttk.Label(volume_frame, text="Volume:").pack(side=tk.LEFT, padx=5)
        self.volume_bar = ttk.Progressbar(volume_frame, length=200, mode='determinate')
        self.volume_bar.pack(side=tk.LEFT, padx=5)
        
        # Intensity indicator
        intensity_frame = ttk.Frame(metrics_frame)
        intensity_frame.pack(fill=tk.X, pady=2)
        ttk.Label(intensity_frame, text="Intensity (dB):").pack(side=tk.LEFT, padx=5)
        self.intensity_bar = ttk.Progressbar(intensity_frame, length=200, mode='determinate')
        self.intensity_bar.pack(side=tk.LEFT, padx=5)
        
        # Visualization frame
        viz_frame = ttk.LabelFrame(main_frame, text="Visualization", padding="10")
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Visualization mode selector
        viz_modes = ["Line Graph", "Bar Graph", "Meter"]
        viz_selector = ttk.OptionMenu(viz_frame, self.visualization_mode, 
                                    self.visualization_mode.get(), *viz_modes,
                                    command=self._change_visualization)
        viz_selector.pack(side=tk.TOP, padx=5, pady=5)
        
        # Plot frame
        self.plot_frame = ttk.Frame(viz_frame)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)

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
            
            # Set system volume
            self.volume_controller.set_volume(new_volume)
            
            # Update data
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
            messagebox.showerror("Error", f"Failed to start audio monitoring: {str(e)}")

    def _calculate_volume_from_intensity(self, intensity):
        if self.is_calibrating:
            self.calibration_samples.append(intensity)
            return self.current_volume.get()
        
        min_intensity = self.calibration_min if self.calibration_min != 0 else 0
        max_intensity = self.calibration_max if self.calibration_max != 100 else 100
        
        normalized = (intensity - min_intensity) / (max_intensity - min_intensity)
        normalized *= self.sensitivity.get()
        return min(max(normalized, 0), 1)

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

    def _setup_plot(self):
        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
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

    def _change_visualization(self, mode):
        self._setup_plot()  # Reset plot for new visualization mode

    def _update_plot(self):
        mode = self.visualization_mode.get()
        
        if mode == "Line Graph":
            if len(self.intensity_history) > self.max_history:
                self.intensity_history = self.intensity_history[-self.max_history:]
                self.volume_history = self.volume_history[-self.max_history:]
                
            x = range(len(self.intensity_history))
            self.intensity_line.set_data(x, self.intensity_history)
            self.volume_line.set_data(x, [v * 100 for v in self.volume_history])
            self.ax.set_xlim(0, max(self.max_history, len(x)))
        
        elif mode == "Bar Graph":
            self.ax.clear()
            self.ax.bar(['Intensity', 'Volume'], 
                       [self.current_intensity.get(), self.current_volume.get() * 100],
                       color=['blue', 'red'])
            self.ax.set_ylim(0, 100)
        
        elif mode == "Meter":
            self.ax.clear()
            intensity = self.current_intensity.get()
            volume = self.current_volume.get() * 100
            
            # Create VU meter style visualization
            self.ax.add_patch(plt.Rectangle((0, 0), intensity, 0.3, color='blue', alpha=0.6))
            self.ax.add_patch(plt.Rectangle((0, 0.7), volume, 0.3, color='red', alpha=0.6))
            
            self.ax.set_xlim(0, 100)
            self.ax.set_ylim(0, 1)
            self.ax.set_xticks(range(0, 101, 10))
            self.ax.set_yticks([0.15, 0.85])
            self.ax.set_yticklabels(['Intensity', 'Volume'])
        
        self.canvas.draw()

    def _update_gui(self):
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
        
        self.root.after(100, self._update_gui)

    def _save_current_state(self):
        """Save current state before closing"""
        self.config.settings.update({
            "sensitivity": self.sensitivity.get(),
            "visualization_mode": self.visualization_mode.get(),
            "audio_feedback": self.audio_feedback.get(),
            "calibration": {
                "min": self.calibration_min,
                "max": self.calibration_max
            }
        })
        self.config.save_config()
        logger.info("Application state saved")

    def __del__(self):
        """Cleanup on destruction"""
        self._save_current_state()
        if hasattr(self, 'stream'):
            self.stream.stop()
        logger.info("Application shutdown complete")

def main():
    try:
        root = tk.Tk()
        app = VolumeControlApp(root)
        root.mainloop()
    except Exception as e:
        logger.critical(f"Application crashed: {e}")
        raise

if __name__ == "__main__":
    main()