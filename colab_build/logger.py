class DownloadLogger:
    def debug(self, msg):
        pass
    
    def warning(self, msg):
        if any(x in msg.lower() for x in ["ffmpeg not found", "falling back", "failed"]):
            print(f"Warning: {msg}")
    
    def error(self, msg):
        print(f"Error: {msg}")
    
    def write(self, msg):
        if msg and msg.strip():
            print(msg.strip())