from canvas import Canvas
from moviepy.video.io.ffmpeg_writer import FFMPEG_VideoWriter
import cv2


class Clip:
    def __init__(self, w, h, filename, fps):
        self.fps = fps
        self.canvas = Canvas(w, h)
        if filename is None or filename == '':
            self.writer = None
        else:
            self.writer = FFMPEG_VideoWriter(filename, (w,h), fps=fps)
        self.last_frame = self.canvas.get_npimage()
    
    def step(self):
        self.render()
        frame = self.canvas.get_npimage()
        self.last_frame = frame
        if self.writer:
            self.writer.write_frame(frame)
        else:
            self._cv_show_wait()

    def wait(self, sec):
        if self.writer:
            nframe = int(self.fps * sec)
            for i in range(nframe):
                self.writer.write_frame(self.last_frame)
        else:
            self._cv_show_wait()

    def _cv_show_wait(self):
        cvt = cv2.cvtColor(self.last_frame, cv2.COLOR_BGR2RGB)
        cv2.imshow('preview', cvt)
        key = cv2.waitKey(0)
        if key == ord('q') or key == 27:  # Esc
            cv2.destroyAllWindows()
            raise Exception('preview stopped')

    def finish(self):
        if self.writer:
            self.writer.close()
        else:
            cv2.destroyAllWindows()

    def render(self):
        self.canvas.clear()


