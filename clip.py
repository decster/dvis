import random
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



class MergeSortClip(Clip):
    def __init__(self, N):
        self.bw = 40
        super(MergeSortClip, self).__init__(N*self.bw+40, 60, 'mergesort.mp4', 4)
        self.data = list(range(N))
        self.pos = (0,0,0,0)

    def render(self):
        self.canvas.clear()
        def box_color(i, text):
            if i < self.pos[0]:
                return 0xffffff
            elif i < self.pos[1]:
                return 0xffaaaa
            elif i < self.pos[2]:
                return 0xaaffaa
            elif i < self.pos[3]:
                return 0xaaaaff
        bbox = self.canvas.text_box_list(20, 30, self.bw, 24, self.data, 'h', box_color=box_color)
        self.canvas.text_align_to(bbox, 'merge sort')

    def run(self):
        data = self.data
        random.shuffle(data)
        def dump(s, p1, p2, e):
            self.pos = (s, p1, p2, e)
            self.step()
        def merge(arr, start, mid, end):
            os = start
            start2 = mid + 1
            dump(s=os, p1=start, p2=start2, e=end)
            if arr[mid] <= arr[start2]:
                dump(s=os, p1=end+1, p2=end+1, e=end)
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
                    start += 1
                    mid += 1
                    start2 += 1
                dump(s=os, p1=start, p2=start2, e=end)
            dump(s=os, p1=end+1, p2=end+1, e=end)
        def mergeSort(arr, l, r):
            m = l + (r - l) // 2
            # Sort first and second halves
            if l < m:
                mergeSort(arr, l, m)
            if m+1 < r:
                mergeSort(arr, m + 1, r)
            merge(arr, l, m, r)
        mergeSort(data, 0, len(data)-1)
        for i in range(10):
            self.step()
        self.finish()


class QuickSortClip(Clip):
    def __init__(self, N):
        self.bw = 40
        super(QuickSortClip, self).__init__(N*self.bw+40, 80, 'quicksort.mp4', 4)
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
    MergeSortClip(20).run()
    QuickSortClip(20).run()
    