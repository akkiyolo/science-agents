import wave
import math
import struct

def generate_bgm():
    filepath = "d:/LearnAgents/science-agents-ui/public/assets/bgm.wav"
    
    # Audio parameters
    sample_rate = 44100
    duration = 8.0 # seconds
    
    # C major arpeggio frequencies (C4, E4, G4, C5)
    notes = [261.63, 329.63, 392.00, 523.25]
    
    obj = wave.open(filepath, 'w')
    obj.setnchannels(1) # mono
    obj.setsampwidth(2)
    obj.setframerate(sample_rate)
    
    for i in range(int(sample_rate * duration)):
        t = float(i) / sample_rate
        # Change note every 0.25 seconds
        note_idx = int((t * 4) % len(notes))
        freq = notes[note_idx]
        
        # Add some bass (C2 = 65.41 Hz)
        bass_freq = 65.41 if int(t) % 2 == 0 else 98.00 # C2 or G2
        
        # Generate square/sine waves
        melody = math.sin(2.0 * math.pi * freq * t)
        bass = math.sin(2.0 * math.pi * bass_freq * t)
        
        # Envelope to make it plucky
        env = math.exp(-3.0 * (t % 0.25))
        
        sample = (melody * env * 0.5 + bass * 0.5) * 32767.0 * 0.2
        
        # Clip
        if sample > 32767: sample = 32767
        if sample < -32768: sample = -32768
        
        obj.writeframesraw(struct.pack('<h', int(sample)))
        
    obj.close()
    print("Generated bgm.wav")

if __name__ == "__main__":
    generate_bgm()
