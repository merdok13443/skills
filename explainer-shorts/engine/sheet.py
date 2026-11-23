import sys, glob, os
from PIL import Image
d=sys.argv[1]
fs=sorted(glob.glob(os.path.join(d,'t*.png')),key=lambda f:float(os.path.basename(f)[1:-4]))
ims=[Image.open(f).convert('RGB').resize((360,640)) for f in fs]
cols=int(sys.argv[2]) if len(sys.argv)>2 else 4;rows=(len(ims)+cols-1)//cols
sheet=Image.new('RGB',(cols*360,rows*640),'white')
for i,im in enumerate(ims): sheet.paste(im,((i%cols)*360,(i//cols)*640))
sheet.save(os.path.join(d,'sheet.png'))
