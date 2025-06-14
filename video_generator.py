from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip
import numpy as np
import random
from scipy.io import wavfile
import os

# Canvas size
WIDTH, HEIGHT = 640, 480
DURATION = 10  # seconds
FPS = 24

def generate_bug_sound(duration, sample_rate=44100):
    """Generate a buzzing sound for the bug"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    # Create a buzzing sound using multiple sine waves
    frequency = 200 + 50 * np.sin(2 * np.pi * 2 * t)  # Varying frequency
    signal = 0.5 * np.sin(2 * np.pi * frequency * t)
    # Add some noise
    signal += 0.1 * np.random.randn(len(t))
    # Normalize
    signal = signal / np.max(np.abs(signal))
    # Convert to 16-bit PCM
    signal = (signal * 32767).astype(np.int16)
    return signal, sample_rate

def make_path(duration, fps=FPS):
    """Generate a more natural bug-like path"""
    num_frames = int(duration * fps)
    x, y = random.randint(100, 540), random.randint(100, 380)
    path = [(x, y)]
    
    # Add some randomness to make movement more natural
    velocity_x = random.uniform(-2, 2)
    velocity_y = random.uniform(-2, 2)
    
    for _ in range(num_frames - 1):
        # Update velocity with some randomness
        velocity_x += random.uniform(-0.5, 0.5)
        velocity_y += random.uniform(-0.5, 0.5)
        
        # Limit maximum velocity
        velocity_x = np.clip(velocity_x, -5, 5)
        velocity_y = np.clip(velocity_y, -5, 5)
        
        # Update position
        x = np.clip(x + velocity_x, 0, WIDTH)
        y = np.clip(y + velocity_y, 0, HEIGHT)
        
        path.append((x, y))
    return path

def make_frame(t):
    """Create a single frame of the animation"""
    idx = int(t * FPS)
    frame = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8) * 255
    
    if idx < len(path):
        x, y = path[idx]
        # Draw a more detailed bug (small black dot with wings)
        # Body
        frame[y-2:y+2, x-2:x+2] = [0, 0, 0]
        # Wings
        frame[y-3:y+3, x-4:x+4] = [50, 50, 50]
    
    return frame

def main():
    global path
    path = make_path(DURATION)
    
    # Create video clip
    clip = VideoClip(make_frame, duration=DURATION)
    
    # Generate and add bug sound
    bug_sound, sample_rate = generate_bug_sound(DURATION)
    temp_audio_file = "temp_bug_sound.wav"
    wavfile.write(temp_audio_file, sample_rate, bug_sound)
    
    # Add audio to video
    audio_clip = AudioFileClip(temp_audio_file)
    final_clip = clip.set_audio(audio_clip)
    
    # Write the final video
    final_clip.write_videofile("bug_animation.mp4", fps=FPS, codec='libx264', audio_codec='aac')
    
    # Clean up temporary audio file
    os.remove(temp_audio_file)

if __name__ == "__main__":
    main() 