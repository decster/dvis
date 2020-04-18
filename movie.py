import json
import moviepy.editor as mpy
from dvis import Surface


class History(list):
    def __init__(self, *args, **kwargs):
        super(History, self).__init__(*args, **kwargs)

    def load(self, fin):
        if isinstance(fin, str):
            fin = open(fin, 'r')
        while True:
            l = fin.readline()
            if not l:
                break
            self.append(json.loads(l))
        fin.close()

    def save(self, fout):
        if isinstance(fout, str):
            fout = open(fout, 'w')
        for l in self:
            json.dump(l, fout)
            fout.write('\n')
        fout.close()


class Movie(object):
    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.surface = Surface(w, h)
        self.idx = 0

    def nframe(self):
        raise Exception('not implemented')

    def render(self, idx):
        self.surface.draw_axis()

    def make_frame(self, t):
        self.surface.clear()
        self.render(self.idx)
        self.idx += 1
        return self.surface.get_npimage()

    def save(self, fname, fps=24):
        self.idx = 0
        duration = self.nframe() / fps
        clip = mpy.VideoClip(make_frame=self.make_frame, duration=duration)
        if fname.endswith('.gif'):
            clip.write_gif(fname, fps=fps)
        else:
            clip.write_videofile(fname, fps=fps)


class MovieWithHistory(Movie):
    def __init__(self, w, h, history, endstop=4):
        super(MovieWithHistory, self).__init__(w,  h)
        self.history = history
        self.endstop = endstop

    def nframe(self):
        return len(self.history) + self.endstop

    def save(self, fname, fps=24, json=False):
        if json:
            self.history.save(fname+".json")
        super(MovieWithHistory, self).save(fname, fps=fps)
