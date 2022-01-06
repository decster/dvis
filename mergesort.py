import random
from clip import Clip


class MergeSortClip(Clip):
    def __init__(self, N, path):
        self.bw = 40
        super(MergeSortClip, self).__init__(N*self.bw+40, 60, path, 4)
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


if __name__ == "__main__":
    MergeSortClip(20, 'mergesort.mp4').run()
