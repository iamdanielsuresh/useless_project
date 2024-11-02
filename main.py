import sounddevice as sd
import numpy as np
import pycaw.pycaw as pycaw
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math

def get_current_system_volume():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    return volume

def set_system_volume(volume_level):
    # Ensure volume level is between 0 and 1
    volume_level = max(0.0, min(1.0, volume_level))
    volume = get_current_system_volume()
    volume.SetMasterVolumeLevelScalar(volume_level, None)

def calculate_volume_from_intensity(intensity):
    # Convert intensity to volume level (0-1)
    # You might need to adjust these values based on your microphone
    min_intensity = 0
    max_intensity = 100
    normalized = (intensity - min_intensity) / (max_intensity - min_intensity)
    return min(max(normalized, 0), 1)

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    
    # Calculate volume intensity from microphone input
    volume_norm = np.linalg.norm(indata) * 10
    
    # Convert to decibels
    if volume_norm > 0:
        intensity = 20 * math.log10(volume_norm)
    else:
        intensity = 0
        
    # Set system volume based on intensity
    new_volume = calculate_volume_from_intensity(intensity)
    set_system_volume(new_volume)
    
    # Print current intensity and volume level
    print(f"Intensity: {intensity:.2f} dB, Volume: {new_volume:.2%}")

def main():
    try:
        # Set up audio stream
        with sd.InputStream(callback=audio_callback,
                          channels=1,
                          samplerate=44100,
                          blocksize=int(44100 * 0.1)):  # 100ms blocks
            print("Yell to control the volume! (Press Ctrl+C to stop)")
            while True:
                sd.sleep(1000)
    except KeyboardInterrupt:
        print("\nStopping volume control...")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()