"""Use the skill renderer with the PDF exported by native Microsoft Word.

The bundled renderer requires LibreOffice, absent on this Windows host.
Only conversion is replaced; OOXML preparation and PDF-to-PNG rasterization
remain the skill's render_docx.py implementation.
"""
import pathlib,runpy,sys
root=pathlib.Path(__file__).parent
script=pathlib.Path('C:/Users/21413/.codex/plugins/cache/openai-primary-runtime/documents/26.1025.11240/skills/documents/render_docx.py')
ns=runpy.run_path(str(script),run_name='document_render_adapter')
pdf=root/'太古仙尊每日助手源码分析报告.pdf'
ns['rasterize'].__globals__['convert_to_pdf']=lambda *args,**kwargs:(str(pdf),'Converted by native Microsoft Word 16.0; LibreOffice unavailable')
sys.argv=[str(script),str(root/'太古仙尊每日助手源码分析报告.docx'),'--output_dir',str(root/'审计资料/页面校验'),'--dpi','110']
ns['main']()
