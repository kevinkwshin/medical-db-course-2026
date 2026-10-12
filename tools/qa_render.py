"""usage: python3 qa_render.py deck.pptx outname first last [pages_csv]  -> render/<outname>/slide-NNN.png + render/<outname>_sheet_N.png"""
import os, sys, subprocess, shutil, glob
from PIL import Image, ImageDraw
pptx, name, first, last = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
pick = [int(p) for p in sys.argv[5].split(',')] if len(sys.argv) > 5 else None
HERE = os.path.dirname(os.path.abspath(__file__))
CONT = os.path.expanduser("~/Library/Containers/com.microsoft.Powerpoint/Data/tmp")
src = os.path.join(CONT, name + ".pptx"); pdf = os.path.join(CONT, name + ".pdf")
shutil.copy(pptx, src)
if os.path.exists(pdf): os.remove(pdf)
script = f'''tell application "Microsoft PowerPoint"
	open POSIX file "{src}"
	set pres to active presentation
	save pres in (POSIX file "{pdf}") as save as PDF
	delay 3
	close pres saving no
end tell'''
subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
assert os.path.exists(pdf), "PDF export failed"
out = os.path.join(HERE, "render", name)
shutil.rmtree(out, ignore_errors=True)
r = subprocess.run(["osascript", "-l", "JavaScript", os.path.join(HERE, "pdf2png.js"), pdf, out, "1.2", str(first), str(last)], capture_output=True, text=True)
print(r.stdout.strip(), r.stderr.strip()[-300:])
files = sorted(glob.glob(os.path.join(out, "slide-*.png")))
if pick: files = [f for f in files if int(f[-7:-4]) in pick]
def sheet(fs, path, cols=3):
    ims = [Image.open(f) for f in fs]; w, h = ims[0].size; tw, th = int(w * .5), int(h * .5)
    rows = (len(ims) + cols - 1) // cols
    S = Image.new("RGB", (cols * tw + (cols + 1) * 10, rows * (th + 30) + 10), "white"); d = ImageDraw.Draw(S)
    for i, (f, im) in enumerate(zip(fs, ims)):
        r_, c = divmod(i, cols); x = 10 + c * (tw + 10); y = 10 + r_ * (th + 30)
        S.paste(im.resize((tw, th)), (x, y)); d.text((x, y + th + 5), os.path.basename(f), fill="black")
    S.save(path)
for k in range(0, len(files), 9):
    sheet(files[k:k + 9], os.path.join(HERE, "render", f"{name}_sheet_{k // 9 + 1}.png"))
print(len(files), "pages ->", (len(files) + 8) // 9, "sheets")
