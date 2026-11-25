"""python ikaros/render.py [s01,s02 | all] [--jobs 4] [--preview 0,20,40]  ->  ikaros/out/shots/<id>.mp4 (or a contact sheet)
python ikaros/render.py --assemble  ->  ikaros/dist/ikaros.mp4 with out/score.wav"""
import sys, os, importlib, subprocess, argparse, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from multiprocessing import Pool
import numpy as np, cv2
import film

OUT = os.path.join(HERE, 'out', 'shots'); DRAWINGS = 2 * film.BAR // film.ON


def work(a):
    sid, d = a; return importlib.import_module('shots.' + sid).draw(d)


def render(sid, jobs):
    m = importlib.import_module('shots.' + sid); m.page() if hasattr(m, 'page') else None
    os.makedirs(OUT, exist_ok=True); out = os.path.join(OUT, sid + '.mp4'); t = time.time()
    ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1920x1080', '-r', '12', '-i', '-',
                           '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', '-r', '12', out], stdin=subprocess.PIPE)
    with Pool(jobs) as p:
        for im in p.imap(work, [(sid, d) for d in range(DRAWINGS)]): ff.stdin.write(np.ascontiguousarray(im).tobytes())
    ff.stdin.close(); ff.wait(); print(sid, '%.0fs' % (time.time() - t), flush=True)


def preview(sid, ds, jobs):
    m = importlib.import_module('shots.' + sid); m.page() if hasattr(m, 'page') else None
    with Pool(jobs) as p: ims = p.map(work, [(sid, d) for d in ds])
    small = [cv2.resize(cv2.cvtColor(im, cv2.COLOR_RGB2BGR), (640, 360), interpolation=cv2.INTER_AREA) for im in ims]
    for im, d in zip(small, ds): cv2.putText(im, '%s d%02d' % (sid, d), (8, 22), 0, .6, (20, 20, 20), 2)
    while len(small) % 3: small.append(np.full_like(small[0], 255))
    sheet = np.vstack([np.hstack(small[i:i + 3]) for i in range(0, len(small), 3)])
    p = os.path.join(HERE, 'out', 'preview_%s.jpg' % sid); cv2.imwrite(p, sheet, [cv2.IMWRITE_JPEG_QUALITY, 88]); print(p)
    big = os.path.join(HERE, 'out', 'preview_%s_d%02d.png' % (sid, ds[len(ds) // 2])); cv2.imwrite(big, cv2.cvtColor(ims[len(ds) // 2], cv2.COLOR_RGB2BGR))


def assemble():
    lst = os.path.join(OUT, 'list.txt'); open(lst, 'w').write(''.join("file '%s'\n" % os.path.join(OUT, s + '.mp4') for s, _, _ in film.SHOTS))
    os.makedirs(os.path.join(HERE, 'dist'), exist_ok=True); out = os.path.join(HERE, 'dist', 'ikaros.mp4')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-i', os.path.join(HERE, 'out', 'score.wav'),
                    '-map', '0:v', '-map', '1:a', '-vf', 'fps=24,format=yuv420p', '-c:v', 'libx264', '-preset', 'slow', '-crf', '20',
                    '-c:a', 'aac', '-b:a', '256k', '-t', str(film.N / film.FPS), '-movflags', '+faststart', out], check=True)
    print(out, '%.1f MB' % (os.path.getsize(out) / 1e6))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('shots', nargs='?', default='all'); ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--preview'); ap.add_argument('--assemble', action='store_true'); a = ap.parse_args()
    if a.assemble: assemble(); sys.exit()
    ids = [s for s, _, _ in film.SHOTS] if a.shots == 'all' else a.shots.split(',')
    for s in ids:
        if a.preview: preview(s, [int(x) for x in a.preview.split(',')], a.jobs)
        else: render(s, a.jobs)
