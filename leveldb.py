import random
import sys
import json
from clip import Clip
from colors import Set3


class LevelDBClip(Clip):
    def __init__(self, data, path):
        super(LevelDBClip, self).__init__(1280, 800, path, 24)
        self.data = [json.loads(e[4:]) for e in open(data).readlines()]
        n = len(self.data)
        print(f'total step: {n}')
        self.state = (None, None, None) # levels, delete, add
        self.stepi = 0

    def render(self):
        self.canvas.clear()
        heights = [100, 120, 180, 280]
        ys = [sum(heights[:i])+i*10 for i in range(len(heights))]
        self.canvas.translate(70, 40)
        TW = self.canvas.width - 80
        DW = 120000
        scale = DW / TW # 100
        dels, adds = set(), set()
        if self.state[1]:
            dels = set(e[1] for e in self.state[1])
        if self.state[2]:
            adds = set(e[1] for e in self.state[2])
        for i in range(4):
            fs = self.state[0][i]
            total_size = sum(e['size'] for e in fs) // 1024
            self.canvas.text(-35, ys[i]+heights[i]//2, f'L{i}', 24, align='center')
            self.canvas.text(-35, ys[i]+heights[i]//2+24, f'{total_size//1024}M', 18, align='center')
            for idx,f in enumerate(fs):
                fid = f['id']
                color = Set3[0]
                if fid in dels:
                    color = Set3[1]
                elif fid in adds:
                    color = Set3[2]
                size = f['size']
                s, e = f['start'] // scale, f['end'] // scale
                w = max(1, e - s)
                h = max(8, size // (w * 1800))
                if i == 0:
                    #print(f'level:{i} s:{s} e:{e} w:{w} h:{h}')
                    th = h + len(fs)*8
                    self.canvas.box(s, ys[i]+heights[i]//2-th//2+idx*8, w, h, color=color)
                else:
                    self.canvas.box(s, ys[i]+heights[i]//2-h//2, w, h, color=color)

    def on_step_back(self):
        if self.stepi >= 2:
            self.stepi -= 2

    def stepn(self):
        if self.stepi < 100 and self.writer:
            for i in range((100-self.stepi)//15):
                self.step()
        else:
            self.step()

    def run(self):
        self.stepi = 0
        while True:
            i = self.stepi
            e = self.data[i]
            if isinstance(e, list):
                # levels
                self.state = (e, None, None)
                self.stepn()
            else:
                # compaction
                self.state = (self.data[i-1], e['delete'], None)
                self.stepn()
                self.state = (self.data[i+1], None, e['add'])
                self.stepn()
            if self.writer:
                self.stepi += max(1, self.stepi//100)
            else:
                self.stepi += 1
            if self.stepi >= len(self.data):
                break
        self.stepi = len(self.data) - 1
        self.wait(1)
        print(f'total frame: {self.nframe} {self.nframe/self.fps:.1f}s')


if __name__ == "__main__":
    path = None
    if len(sys.argv) > 1:
        path = sys.argv[1]
    LevelDBClip('leveldb.log', path).run()
