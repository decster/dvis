import random
import sys
from canvas import Canvas
from clip import Clip
from colors import Set3
import numpy as np

head_size = 64
page_size = 4096
subpage_padding = 16


def npad(x, p):
    return (x + p - 1) // p


def pad(x, p):
    return npad(x, p) * p


def subpage_pack_size(nitem, item_size):
    return npad(nitem, subpage_padding) + npad(item_size * nitem, subpage_padding)


page_head_pack = npad(head_size, subpage_padding)


class HT:
    def __init__(self, memory_size, item_size):
        subpage_size = (page_size - head_size) // subpage_padding
        slot_per_subpage = subpage_size // (item_size + 1)
        self.slot_per_page = slot_per_subpage * subpage_padding
        self.pack_per_page = page_size // subpage_padding
        self.item_size = item_size
        self.npage = memory_size // page_size
        self.pages = [0] * self.npage
        self.subpages = [[0] * 16 for i in range(self.npage)]
        self.subpage_packs = [[0] * 16 for i in range(self.npage)]
        self.orig_assigns = [[(pid, i) for i in range(16)] for pid in range(self.npage)]
        self.assigns = self.orig_assigns
        self.nele = 0
        self.moved_item = None

    def put(self, v):
        subid = v & 0xfff
        pid = (v >> 12) % self.npage
        subpid = subid >> 8
        self.pages[pid] += 1
        self.subpages[pid][subpid] += 1
        self.subpage_packs[pid][subpid] = subpage_pack_size(self.subpages[pid][subpid], self.item_size)
        self.nele+=1

    def reassign_overflows(self):
        limit = (page_size - head_size) // subpage_padding

        def candidates(sizes):
            s = sum(sizes)
            if s <= limit:
                return None
            N = len(sizes)
            r = s - limit
            candi1 = [(e, i) for i,e in enumerate(sizes) if e >= r]
            if len(candi1) > 0:
                return [min(candi1)]
            candi2 = None
            for i in range(N):
                for j in range(i+1, N):
                    v = sizes[i]+sizes[j]
                    if v == r:
                        return [(sizes[i], i), (sizes[j], j)]
                    elif v > r and (candi2 is None or (v, i, j) < candi2):
                        candi2 = (v, i, j)
            if candi2:
                return [(sizes[candi2[1]], candi2[1]), (sizes[candi2[2]], candi2[2])]
            candi3 = None
            for i in range(N):
                for j in range(i+1, N):
                    for k in range(j + 1, N):
                        v = sizes[i]+sizes[j]+sizes[k]
                        if v == r:
                            return [(sizes[i], i), (sizes[j], j), (sizes[k], k)]
                        elif v > r and (candi3 is None or (v, i, j, k) < candi3):
                            candi3 = (v, i, j, k)
            if candi3:
                return [(sizes[candi2[1]], candi2[1]), (sizes[candi2[2]], candi2[2]), (sizes[candi2[3]], candi2[3])]
            raise Exception(f"no suitable candi: {sizes} sum:{s}-limit:{limit}={r}")

        cds = []
        holes = []
        pages = self.subpage_packs
        for pid,p in enumerate(pages):
            cs = candidates(p)
            s = sum(p)
            if cs:  # larger than limit
                for c in cs:
                    cds.append((c[0], pid, c[1]))  # cnt, pid, subpid
                # if len(cs) == 2:
                #     print(f"2 candi: {p} sum:{sum(p)}-limit:{limit}={sum(p)-limit} {cs[0][0]} {cs[1][0]}")
            elif limit - s > 0:
                holes.append((limit - s, pid)) # hole_cnt, pid
        reassigns = []
        #print('candidates: ' + ' '.join(f'{e[1]}:{e[0]}' for e in cds))
        #print(f'holes: {holes}')
        while len(cds) > 0:
            cds.sort()
            holes.sort()
            c = cds[-1]
            if len(holes) == 0 or c[0] > holes[-1][0]:
                raise Exception('assign failed, no holes or hole not large enough')
            hole, hi = min((hole, hi) for hi, hole in enumerate(holes) if hole[0] >= c[0])
            reassigns.append(((c[1],c[2]), holes[hi][1], c[0]))
            #print(f'assign {reassigns[-1]} candis:{cds[-5:]} holes:{holes[-5:]}')
            new_hole = holes[hi][0] - c[0]
            if new_hole > 0:
                holes[hi] = (new_hole, holes[hi][1])
            else:
                del holes[hi]
            cds.pop()
        #print(f'reassigns: {reassigns}')
        self.moved_item = 0
        assigns = [[(pid, i) for i in range(16)] for pid in range(len(pages))]
        for src, dest, cnt in reassigns:
            assigns[dest].append(src)
            assigns[src[0]].remove(src)
            self.moved_item += cnt
        self.orig_assigns = self.assigns
        self.assigns = assigns

    def get_subpage_poses(self):
        pages = self.subpage_packs;
        # [[(dest_pid, cpos, len)]]
        poses = [[(0,0,0)]*16 for i in range(len(pages))]
        for dpid in range(len(self.subpage_packs)):
            cpos = page_head_pack
            for spid, ssubpid in self.assigns[dpid]:
                l = pages[spid][ssubpid]
                poses[spid][ssubpid] = (dpid, cpos, l)
                cpos += l
        return poses

    def space_ratio(self):
        return self.nele * self.item_size / (self.npage * page_size)

    def stats(self):
        page_packs = [sum(e) for e in self.subpage_packs]
        pmin = min(page_packs)
        pmax = max(page_packs)
        pavg = sum(page_packs) / len(page_packs)
        ret = f'size: {self.nele} #page:{self.npage} #pack/page:{self.pack_per_page} (min:{pmin} max:{pmax} avg:{pavg:.1f}) space_ratio:{self.space_ratio():.3f}'
        if self.moved_item and self.moved_item > 0:
            ret += f' move: {self.moved_item}/{self.nele} {self.moved_item/self.nele:.4f}'
        return ret

    def render(self, canvas=None):
        page_h = 4
        pack_w = 5
        if canvas is None:
            canvas = Canvas(1500, self.npage * page_h + 20)
            canvas.translate(10, 10)
        poses = self.get_subpage_poses()
        for pid in range(self.npage):
            canvas.box(0, page_h * pid, page_head_pack*pack_w, page_h, '777', 0)
            for subpid in range(16):
                dpid, cpos, l = poses[pid][subpid]
                if l == 0:
                    continue
                if dpid == pid:
                    canvas.box(cpos*pack_w, dpid*page_h, l*pack_w, page_h, Set3[subpid], 0)
                else:
                    canvas.box(cpos*pack_w, dpid*page_h, l*pack_w, page_h, Set3[subpid], 1)
        canvas.box(0, 0, pack_w * self.pack_per_page, page_h*self.npage,  '0000')
        return canvas


class PHDBClip(Clip):
    def __init__(self, item_size, memory_size, ratio, seed=0, path='phdb.mp4'):
        random.seed(seed)
        self.N = int(memory_size * ratio / item_size)
        self.ht = HT(memory_size, item_size)
        self.caption_height = 30
        self.H = self.ht.npage * 4 + self.caption_height + 10
        self.W = 1500
        super(PHDBClip, self).__init__(self.W, self.H, path, 4)

    def render(self):
        self.canvas.clear()
        self.canvas.translate(10, self.caption_height)
        self.ht.render(self.canvas)
        self.canvas.reset_translate()
        self.canvas.text(10, 20, self.ht.stats(), 18, align='left')

    def run(self):
        self.step()
        self.wait(1)
        progress = 0
        for i in range(self.N):
            v = random.randint(0, 0xffffffff)
            self.ht.put(v)
            p = int(i / self.N * 40)
            if p > progress:
                progress = p
                self.step()
        self.wait(1)
        self.ht.reassign_overflows()
        self.step()
        self.wait(2)
        self.finish()


if __name__ == "__main__":
    path = None
    if len(sys.argv) > 1:
        path = sys.argv[1]
    PHDBClip(20, 1024*1024, 0.87, path=path).run()
