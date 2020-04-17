import moviepy.editor as mpy
from dvis import *

N = 20
W, H = 200, 700
T = 40
FPS = 15
duration = 4

fontsize = 30
eles = [e*13433 % 100 for e in range(N)]
ts = TextBoxVList(eles, fontsize, 100)
root = WithName('Demo', fontsize, ts, 2)

def makeFrame(t):
    i = int(t/duration * T)
    ts.children[(i+N-1)%N].b.fill = RGB(0xffffff)
    ts.children[i%N].b.fill = RGB(0xff7777)
    s = Surface(W, H)
    s.clear()
    s.translate(100, 60)
    s.draw(root)
    return s.get_npimage()


clip = mpy.VideoClip(make_frame=makeFrame, duration=duration)
# clip.write_gif("demo_{}x{}.gif".format(W, H), fps=FPS, program="ImageMagick", opt="OptimizePlus", fuzz=10)
clip.write_videofile("movie.mp4", fps=FPS)
