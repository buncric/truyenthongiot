"""Run with Blender: blender -b --python tools/check_blender.py.

Open every committed scene and verify its numbered timeline, packed font,
component geometry, camera and render files. Render three representative scenes
to the OS temporary directory to check that saved .blend files are usable.
"""
import bpy,json,re,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
rows=json.loads((ROOT/'mo-phong-3d/manifest.json').read_text(encoding='utf8'))
assert len(rows)==30
report=[]
out=Path(tempfile.mkdtemp(prefix='iot-blender-reopen-'))
for row in rows:
    p=ROOT/'mo-phong-3d'/row['blend']
    bpy.ops.wm.open_mainfile(filepath=str(p))
    scene=bpy.context.scene
    assert scene.camera and scene.render.engine=='BLENDER_WORKBENCH',row['id']
    assert len(scene.timeline_markers)==row['renders'],row['id']
    assert any(o.type=='MESH' for o in scene.objects),row['id']
    fonts=[o.data.font for o in scene.objects if o.type=='FONT']
    assert fonts and any(f.packed_file for f in fonts),row['id']
    for i in range(row['renders']):
        jpg=p.parent/f'buoc-{i+1:02}.jpg'
        assert jpg.is_file() and jpg.stat().st_size>10000,jpg
        scene.frame_set(1+i*30)
        visible=[o.data.body for o in scene.objects if o.type=='FONT' and not o.hide_render and o.data.body.startswith('Bước ')]
        assert len(visible)==1 and visible[0].startswith(f'Bước {i+1} •'),(row['id'],i,visible)
    if row['id'] in ['3.2','6.1','13.3']:
        scene.frame_set(1);scene.render.filepath=str(out/f"reopen-{row['id']}.jpg")
        bpy.ops.render.render(write_still=True)
    report.append({'id':row['id'],'timeline_steps':row['renders'],'objects':len(scene.objects),'packed_font':True,'result':'PASS'})
(out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('BLENDER_VERIFY_PASS',len(report),'scenes;',sum(r['timeline_steps'] for r in report),'frames;',str(out),flush=True)
