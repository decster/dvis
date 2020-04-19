import random
import sys
from dvis import TextBoxHList, WithName, RGB
from movie import MovieWithHistory, History


def gen_merge_sort(sz):
    data = list(range(sz))
    random.shuffle(data)
    history = History()
    def dump(**kwargs):
        history.append({'data': data.copy(), **kwargs})
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
    return history


class MergeSortMovie(MovieWithHistory):
    def __init__(self, N=16):
        self.bw = 40
        super(MergeSortMovie, self).__init__(N*self.bw+40, 60, gen_merge_sort(N))

    def render(self,idx):
        if idx >= len(self.history):
            data = self.history[-1]
        else:
            data = self.history[idx]
        array = data['data']
        hl = TextBoxHList(array, 24, self.bw)
        for idx in range(data['s'], data['p1']):
            hl[idx].b.fill = RGB(0xffaaaa)
        for idx in range(data['p1'], data['p2']):
            hl[idx].b.fill = RGB(0xaaffaa)
        for idx in range(data['p2'], data['e'] + 1):
            hl[idx].b.fill = RGB(0xaaaaff)
        root = WithName('merge sort', 24, hl)
        self.surface.translate(self.surface.width/2, self.surface.height-16)
        self.surface.draw(root)


def gen_quick_sort(sz):
    data = list(range(sz))
    random.shuffle(data)
    history = History()
    def dump(**kwargs):
        history.append({'data': data.copy(), **kwargs})
    def sub_partition(array, start, end):
        pivot = array[start]
        i = start + 1
        j = start + 1
        dump(s=start, e=end, i=i, j=j)
        while j <= end:
            if array[j] <= pivot:
                dump(s=start, e=end, i=i, j=j, w=j)
                array[j], array[i] = array[i], array[j]
                i += 1
            j += 1
            dump(s=start, e=end, i=i, j=j)
        array[start], array[i - 1] = array[i - 1], array[start]
        dump(s=start, e=end, swap=i-1)
        return i - 1
    def quicksort(array, start=0, end=None):
        if end - start < 1:
            return
        i = sub_partition(array, start, end)
        # print array, i, idx_pivot
        quicksort(array, start, i - 1)
        quicksort(array, i + 1, end)
    quicksort(data, 0, len(data)-1)
    dump(end=True)
    return history


class QuickSortMovie(MovieWithHistory):
    def __init__(self, N=16):
        self.bw = 40
        super(QuickSortMovie, self).__init__(N*self.bw+40, 60, gen_quick_sort(N))

    def render(self,idx):
        if idx >= len(self.history):
            data = self.history[-1]
        else:
            data = self.history[idx]
        array = data['data']
        hl = TextBoxHList(array, 24, self.bw)
        if 'end' in data:
            pass
        elif 'swap' in data:
            for idx in range(data['s'], data['swap']):
                hl[idx].b.fill = RGB(0xffaaaa)
            hl[data['swap']].b.fill = RGB(0xaaffaa)
            for idx in range(data['swap'], data['e']+1):
                hl[idx].b.fill = RGB(0xaaaaff)
        else:
            hl[data['s']].b.fill = RGB(0xaaffaa)
            for idx in range(data['s']+1, data['i']):
                hl[idx].b.fill = RGB(0xffaaaa)
            for idx in range(data['i'], data['j']):
                hl[idx].b.fill = RGB(0xaaaaff)
            for idx in range(data['j'], data['e'] + 1):
                hl[idx].b.fill = RGB(0xaaffff)
            if 'w' in data:
                hl[data['w']].b.fill = RGB(0xff2222)
        root = WithName('quick sort', 24, hl)
        self.surface.translate(self.surface.width/2, self.surface.height-16)
        self.surface.draw(root)


if __name__ == '__main__':
    N = 20
    if len(sys.argv) > 1:
        N = int(sys.argv[1])
    m = MergeSortMovie(N)
    m.save('mergesort.mp4', fps=2, json=True)
    m = QuickSortMovie(N)
    m.save('quicksort.mp4', fps=2, json=True)
