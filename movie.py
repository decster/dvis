import json
import moviepy.editor as mpy
from dvis import Surface


class History(list):
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


class Movie():
    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.surface = Surface(w, h)
        self.idx = 0

    def render(self, idx):
        self.surface.draw_axis()

    def make_frame(self, t):
        self.surface.clear()
        self.render(self.idx)
        self.idx += 1
        return self.surface.get_npimage()

    def save(self, fname, fps=24):
        self.idx = 0
        duration = len(self.history) / fps
        clip = mpy.VideoClip(make_frame=self.make_frame, duration=duration)
        if fname.endswith('.gif'):
            clip.write_gif(fname, fps=fps)
        else:
            clip.write_videofile(fname, fps=fps)

from dvis import TextBoxHList, WithName
import random

def gen_merge_sort(sz):
    data = list(range(sz))
    random.shuffle(data)
    history = []
    def dump():
        history.append({'data': data.copy()})
    def merge(arr, start, mid, end):
        start2 = mid + 1;
        if arr[mid] <= arr[start2]:
            return
        while start <= mid and start2 <= end:
            # If element 1 is in right place
            if arr[start] <= arr[start2]:
                start += 1
            else:
                value = arr[start2]
                index = start2
                # Shift all the elements between element 1
                # element 2, right by 1.
                while index != start:
                    arr[index] = arr[index - 1]
                    index -= 1
                arr[start] = value
                start += 1;
                mid += 1;
                start2 += 1;

    def mergeSort(arr, l, r):
        if l < r:
            m = l + (r - l) // 2
            # Sort first and second halves
            mergeSort(arr, l, m)
            mergeSort(arr, m + 1, r)
            merge(arr, l, m, r)
            dump()
    mergeSort(data, 0, len(data)-1)
    return history


class SortMovie(Movie):
    def __init__(self):
        super(SortMovie, self).__init__(400, 200)
        self.history = SortMovie.gen_data(10)

    def render(self,idx):
        if idx >= len(self.history):
            data = self.history[-1]
        else:
            data = self.history[idx]
        self.surface


if __name__ == '__main__':
    m = Movie(320, 240, [{} for i in range(24)])
    m.save('test.gif')
