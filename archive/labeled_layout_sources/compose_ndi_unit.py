"""Compose the native Blender core close-up with Chinese captions."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent
im=Image.new('RGB',(900,780),'white');unit=Image.open(R/'renders/NDI_Four_Ring_Core_Raw.png').convert('RGBA');im.paste(unit,(70,80),unit)
d=ImageDraw.Draw(im);font=ImageFont.truetype(str(R/'assets/NDIUnitSansSC-Bold.otf'),32);small=ImageFont.truetype(str(R/'assets/NDIUnitSansSC-Regular.otf'),21)
for y,t,f,col in [(25,'NDI 上下端连接示意',font,'#061A4A'),(690,'对应参考图上下 N–R 方向',small,'#061A4A'),(732,'按要求绘制的概念连接，非完整聚合物结构',small,'#737781')]:d.text(((900-d.textlength(t,font=f))/2,y),t,font=f,fill=col)
im.save(R/'renders/NDI_Four_Ring_Core_Preview.png')
