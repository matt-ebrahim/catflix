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
    """Generate a more realistic buzzing sound for the bug"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Create multiple frequency components for a more complex sound
    base_freq = 200  # Base frequency
    freq_variation = 50 * np.sin(2 * np.pi * 2 * t)  # Varying frequency
    harmonics = [
        0.5 * np.sin(2 * np.pi * (base_freq + freq_variation) * t),  # Main tone
        0.3 * np.sin(2 * np.pi * (base_freq * 1.5 + freq_variation) * t),  # First harmonic
        0.2 * np.sin(2 * np.pi * (base_freq * 2 + freq_variation) * t),  # Second harmonic
    ]
    
    # Combine all components
    signal = sum(harmonics)
    
    # Add some noise for texture
    noise = 0.1 * np.random.randn(len(t))
    signal += noise
    
    # Add amplitude modulation for wing beat effect
    wing_beat = 0.3 * np.sin(2 * np.pi * 100 * t)  # 100 Hz wing beat
    signal *= (1 + wing_beat)
    
    # Normalize
    signal = signal / np.max(np.abs(signal))
    
    # Convert to 16-bit PCM
    signal = (signal * 32767).astype(np.int16)
    return signal, sample_rate

def create_natural_background():
    """Create a natural-looking background with texture"""
    # Create base background (light green for grass-like appearance)
    background = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8)
    background[:, :, 0] = 200  # Red channel
    background[:, :, 1] = 230  # Green channel
    background[:, :, 2] = 180  # Blue channel
    
    # Add some texture
    noise = np.random.randint(0, 30, (HEIGHT, WIDTH, 3), dtype=np.uint8)
    background = np.clip(background - noise, 0, 255).astype(np.uint8)
    
    # Add some darker spots for variety
    for _ in range(50):
        x = random.randint(0, WIDTH-1)
        y = random.randint(0, HEIGHT-1)
        size = random.randint(5, 15)
        background[max(0, y-size):min(HEIGHT, y+size), 
                  max(0, x-size):min(WIDTH, x+size)] = background[max(0, y-size):min(HEIGHT, y+size), 
                                                                 max(0, x-size):min(WIDTH, x+size)] * 0.8
    
    return background

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
    frame = background.copy()  # Use the natural background
    
    if idx < len(path):
        x, y = path[idx]
        # Convert coordinates to integers
        x, y = int(x), int(y)
        
        # Draw a more detailed bug
        # Body (dark brown)
        frame[y-2:y+2, x-2:x+2] = [40, 20, 10]
        
        # Wings (semi-transparent)
        wing_color = np.array([100, 100, 100, 128], dtype=np.uint8)
        # Left wing
        frame[y-3:y+3, x-4:x] = np.clip(frame[y-3:y+3, x-4:x] * 0.7, 0, 255)
        # Right wing
        frame[y-3:y+3, x:x+4] = np.clip(frame[y-3:y+3, x:x+4] * 0.7, 0, 255)
        
        # Add a small shadow under the bug
        shadow = np.zeros((4, 4, 3), dtype=np.uint8)
        shadow[:, :] = [20, 20, 20]
        frame[y+2:y+6, x-2:x+2] = np.clip(frame[y+2:y+6, x-2:x+2] * 0.8, 0, 255)
    
    return frame

def main():
    global path, background
    path = make_path(DURATION)
    background = create_natural_background()
    
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
    final_clip.write_videofile("bug_animation.mp4", fps=FPS, codec='libx264', audio_codec='aac', threads=4)
    
    # Clean up temporary audio file
    os.remove(temp_audio_file)

if __name__ == "__main__":
    main() 