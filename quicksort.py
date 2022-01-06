import random
from clip import Clip


class QuickSortClip(Clip):
    def __init__(self, N, path):
        self.bw = 40
        super(QuickSortClip, self).__init__(N*self.bw+40, 80, path, 4)
        self.data = list(range(N))

    def render(self):
        self.canvas.clear()
        lpad = 20
        bbox = self.canvas.text_box_list(lpad, 30, self.bw, 24, self.data, 'h', box_color=self.color)
        if self.ij[0] == self.ij[1]:
            self.canvas.text(lpad+(self.ij[0]+0.5)*self.bw, 70, 'ij', 20)
        else:
            self.canvas.text(lpad+(self.ij[0]+0.5)*self.bw, 70, 'i', 20)
            self.canvas.text(lpad+(self.ij[1]+0.5)*self.bw, 70, 'j', 20)
#         for m in self.ij:
#             self.canvas.line((lpad+(m+0.5)*self.bw, 60), (lpad+(m+0.5)*self.bw, 70))
        self.canvas.text_align_to(bbox, 'quick sort')

    def run(self):
        data = self.data
        random.shuffle(data)
        self.color = [0xffffff] * len(data)
        color = self.color
        i = 0
        j = 0

        def dump():
            self.ij = (i,j)
            self.step()

        def sub_partition(array, start, end):
            pivot = array[start]
            nonlocal i,j
            i = start + 1
            j = start + 1
            color[start] = 0xff7777
            for idx in range(i,end+1):
                color[idx] = 0x00ffff
            dump()
            while j <= end:
                if array[j] <= pivot:
                    color[j] = 0xffaaaa
                    dump()
                    array[j], array[i] = array[i], array[j]
                    color[j] = 0x7777ff
                    color[i] = 0x77ff77
                    i += 1
                else:
                    color[j] = 0x7777ff
                j += 1
                dump()
            color[i-1] = 0xff7777
            dump()
            array[start], array[i - 1] = array[i - 1], array[start]
            for idx in range(start, end+1):
                color[idx] = 0xffffff
            dump()
            return i - 1

        def quicksort(array, start=0, end=None):
            if end - start < 1:
                return
            i = sub_partition(array, start, end)
            # print array, i, idx_pivot
            quicksort(array, start, i - 1)
            quicksort(array, i + 1, end)
        quicksort(data, 0, len(data)-1)
        for i in range(10):
            self.step()
        self.finish()


if __name__ == "__main__":
    QuickSortClip(20, 'quicksort.mp4').run()
