import tkinter as tk
from tkinter import ttk
import sounddevice as sd
import numpy as np
import platform
from ctypes import cast, POINTER
import threading
import time

if platform.system() == 'Windows':
    from ctypes import windll
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
elif platform.system() == 'Darwin':  # macOS
    import osascript
else:  # Linux
    import alsaaudio

class VolumeControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Scream Volume Controller")
        self.root.geometry("400x300")
        
        # Initialize audio system based on OS
        self.setup_volume_control()
        
        # GUI elements
        self.frame = ttk.Frame(root, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.volume_label = ttk.Label(self.frame, text="Current Volume: 0%")
        self.volume_label.grid(row=0, column=0, pady=10)
        
        self.noise_label = ttk.Label(self.frame, text="Noise Level: 0 dB")
        self.noise_label.grid(row=1, column=0, pady=10)
        
        self.start_button = ttk.Button(self.frame, text="Start Listening", command=self.toggle_listening)
        self.start_button.grid(row=2, column=0, pady=20)
        
        self.is_listening = False
        self.stream = None
    
    def setup_volume_control(self):
        system = platform.system()
        if system == 'Windows':
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume_controller = cast(interface, POINTER(IAudioEndpointVolume))
        elif system == 'Darwin':
            self.volume_controller = None  # Will use osascript
        else:
            self.volume_controller = alsaaudio.Mixer()
    
    def get_current_volume(self):
        system = platform.system()
        if system == 'Windows':
            return int((self.volume_controller.GetMasterVolumeLevelScalar() * 100))
        elif system == 'Darwin':
            vol = osascript.osascript('get volume settings')[1]
            return int(vol.split(',')[0].split(':')[1])
        else:
            return self.volume_controller.getvolume()[0]
    
    def set_volume(self, volume):
        volume = max(0, min(100, volume))
        system = platform.system()
        if system == 'Windows':
            self.volume_controller.SetMasterVolumeLevelScalar(volume / 100, None)
        elif system == 'Darwin':
            osascript.osascript(f'set volume output volume {volume}')
        else:
            self.volume_controller.setvolume(int(volume))
        
        self.volume_label.config(text=f"Current Volume: {volume}%")
    
    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        volume_norm = np.linalg.norm(indata) * 10
        db = 20 * np.log10(volume_norm) if volume_norm > 0 else 0
        
        # Update noise level label
        self.root.after(0, self.noise_label.config, {"text": f"Noise Level: {db:.0f} dB"})
        
        # Adjust volume based on noise level
        if db > 60:  # Threshold for considering it a "scream"
            new_volume = int(min(100, db - 60))  # Scale db to volume
            self.root.after(0, self.set_volume, new_volume)
    
    def toggle_listening(self):
        if not self.is_listening:
            self.start_button.config(text="Stop Listening")
            self.is_listening = True
            
            # Start audio stream
            self.stream = sd.InputStream(callback=self.audio_callback)
            self.stream.start()
        else:
            self.start_button.config(text="Start Listening")
            self.is_listening = False
            if self.stream:
                self.stream.stop()
                self.stream.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = VolumeControlApp(root)
    root.mainloop()
