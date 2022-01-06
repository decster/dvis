from canvas import Canvas
from moviepy.video.io.ffmpeg_writer import FFMPEG_VideoWriter


class Clip:
    def __init__(self, w, h, filename, fps):
        self.canvas = Canvas(w, h)
        self.writer = FFMPEG_VideoWriter(filename, (w,h), fps=fps)        
    
    def step(self):
        self.render()
        frame = self.canvas.get_npimage()
        self.writer.write_frame(frame)
        
    def finish(self):
        self.writer.close()

    def render(self):
        self.canvas.clear()


