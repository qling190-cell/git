import pathlib,json,re
from pypdf import PdfReader
from PIL import Image,ImageDraw
root=pathlib.Path(__file__).parent;pdf=PdfReader(root/'太古仙尊每日助手源码分析报告.pdf')
pages=[];fonts=set();images=[]
for i,page in enumerate(pdf.pages,1):
    text=page.extract_text() or '';rows=[s.strip() for s in text.splitlines() if s.strip()]
    pages.append({'page':i,'characters':len(text),'first':rows[:4],'last':rows[-3:]})
    resources=page.get('/Resources',{})
    if hasattr(resources,'get_object'):resources=resources.get_object()
    for _,f in resources.get('/Font',{}).items():fonts.add(str(f.get_object().get('/BaseFont')))
    for name,obj in resources.get('/XObject',{}).items():
        obj=obj.get_object()
        if obj.get('/Subtype')=='/Image':images.append({'page':i,'width':obj.get('/Width'),'height':obj.get('/Height')})
qa=root/'审计资料/页面校验';files=sorted(qa.glob('page-*.png'),key=lambda p:int(re.search(r'(\d+)\.png$',p.name)[1]))
for start in range(0,len(files),8):
    chunk=files[start:start+8];im=Image.new('RGB',(4*306,2*420),'#cccccc');d=ImageDraw.Draw(im)
    for j,path in enumerate(chunk):
        p=Image.open(path);p.thumbnail((300,395));x=(j%4)*306+3;y=(j//4)*420+3;im.paste(p,(x,y));d.text((x,y+397),path.stem,fill='black')
    im.save(qa/f'sheet-{start//8+1}.jpg')
result={'pages':pages,'fonts':sorted(fonts),'image_xobjects':images,'rendered_page_count':len(files)}
(root/'审计资料/layout_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('PAGES',len(pages),'RENDERED',len(files),'FONTS',sorted(fonts),'IMAGES',images)
for row in pages:print(row['page'],row['characters'],' / '.join(row['first'][:2]))
