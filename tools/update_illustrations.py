"""Link reviewed Blender renders and source PDF crops into the exercise guides.

Run after build_scenes.py. Only source hashes and links are changed here;
this script does not alter photos, screenshots, PDFs, firmware or measurements.
"""
from pathlib import Path
import json,re

ROOT=Path(__file__).resolve().parents[1]
catalog=json.loads((ROOT/'docs/catalog.json').read_text(encoding='utf8'))
scenes=json.loads((ROOT/'mo-phong-3d/manifest.json').read_text(encoding='utf8'))
source=json.loads((ROOT/'docs/giao-dien-goc/manifest.json').read_text(encoding='utf8'))
byid={r['id']:r for r in scenes}

for row in catalog:
    p=ROOT/row['guide'];s=p.read_text(encoding='utf8');ex=row['id']
    if ex=='8.1':
        row['title']=s.splitlines()[0].lstrip('# ')
        row['steps']=len(re.findall(r'^### Bước ',s,re.M))
        continue
    if ex not in byid:raise ValueError('Missing scene '+ex)
    steps=re.findall(r'^### Bước (\d+)\. (.+)$',s,re.M)
    for n,_ in steps:
        render=ROOT/f'mo-phong-3d/{ex}/buoc-{int(n):02}.jpg'
        if not render.exists():raise ValueError('Missing render '+str(render))
    s=re.sub(r'!\[Bước ([^\]]+)\]\(images/[^)]+-buoc-(\d+)\.png\)',
       lambda m:f'![Bước {m[1]}](../mo-phong-3d/{ex}/buoc-{int(m[2]):02}.jpg)',s)
    # Stable markers permit refreshing the index without duplicating sections.
    s=re.sub(r'\n<!-- blender-intro -->.*?<!-- /blender-intro -->\n','\n',s,flags=re.S)
    intro=f'''
<!-- blender-intro -->
## Xem mô hình khi chưa có đủ linh kiện

[Tải cảnh Blender bài {ex}](../mo-phong-3d/{ex}/bai-{ex}.blend) · [Cách mở, xoay và xem timeline](../mo-phong-3d/README.md) · [Ảnh linh kiện trên mạng và nguồn](../docs/linh-kien/README.md).

Các hình theo bước dưới đây là **cảnh Blender 3D minh họa bố trí và tín hiệu**. Mốc trên timeline tương ứng số bước; vị trí hạt tín hiệu chỉ diễn họa hướng truyền. Phần nạp code/click menu làm theo chỉ dẫn bằng chữ và ảnh giao diện gốc bên dưới; hình 3D không giả làm màn hình phần mềm hay kết quả đo.

**Đọc cảnh:** xanh lơ/cam/tím là các đường tín hiệu có nhãn; dây đỏ là nguồn, dây đen là GND trong cảnh mạch điện. Với cảnh mạng, mũi tên chỉ luồng logic. Header được giản lược để dễ nhìn, nên dùng bảng nối dây trong bài để tìm chân thật.
<!-- /blender-intro -->
'''
    s=s.replace('## Thực hiện từng bước',intro+'\n## Thực hiện từng bước',1)
    s=s.replace('Các hình `images/*-buoc-*.png` là sơ đồ hướng dẫn biên soạn, không phải ảnh chụp kết quả chạy.',
       'Các hình Blender trong bài là minh họa tự dựng; ảnh giao diện từ PDF được ghi nguồn riêng. Chưa có ảnh phần cứng của người dùng cho bài này, nên chưa xác nhận kết quả thực nghiệm.')
    # Use only crops from the PDF/pages actually cited by this guide.
    s=re.sub(r'\n<!-- source-crops -->.*?<!-- /source-crops -->\n','\n',s,flags=re.S)
    match=re.search(r'Nguồn:.*?tai-lieu-goc/([^\)]+)\), trang (\d+)(?:-(\d+))?',s)
    if match:
        pdf,lo,hi=match.groups();lo=int(lo);hi=int(hi or lo)
        crops=[r for r in source if r['pdf']==pdf and lo<=r['page']<=hi]
        if crops:
            lines=['','<!-- source-crops -->','## Ảnh giao diện / mạch trong tài liệu gốc','',
                'Các ảnh sau lấy từ đúng các trang đề của bài. Khoanh vùng và mũi tên có sẵn trong nguồn; địa chỉ, COM, tên thiết bị và phiên bản là ví dụ. Áp dụng các hiệu chỉnh trong phần thao tác ở trên.','']
            for crop in crops:
                lines += [f"**Trang {crop['page']}, hình {crop['image']+1}** — [mở trang gốc](../tai-lieu-goc/trang/{Path(pdf).stem}/page-{crop['page']:02}.jpg).",'',
                          f"![Giao diện gốc trang {crop['page']}](../docs/giao-dien-goc/{crop['path']})",'']
            lines += ['<!-- /source-crops -->','']
            s+='\n'.join(lines)
    p.write_text(s,encoding='utf8')

(ROOT/'docs/catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
lines=['# Mô hình Blender 3D cho các bài thực hành','',
       f'**{len(scenes)} cảnh `.blend`, {sum(r["renders"] for r in scenes)} hình theo bước**. Bài 8.1 dùng ảnh thao tác và ảnh mạch thật bạn cung cấp; các bài còn lại có mô hình để học khi chưa có đầy đủ linh kiện. [Nguồn ảnh linh kiện tham khảo](../docs/linh-kien/README.md) · [84 hình giao diện từ PDF](../docs/giao-dien-goc/README.md).','',
       '## Mở và sử dụng','',
       '1. Cài Blender 4.5 LTS từ [nguồn chính thức](https://www.blender.org/download/lts/). Mở liên kết `.blend` của bài trong bảng, chọn **Download raw file** trên GitHub và lưu file về máy.',
       '2. Trong Blender chọn **File → Open**, mở file vừa tải. Dùng bánh xe để zoom, giữ chuột giữa để xoay, Shift + chuột giữa để dịch cảnh. Nhấn **Numpad 0** xem camera; **Home** để lấy toàn cảnh.',
       '3. Chuyển viewport sang **Material Preview** hoặc **Solid → Color: Material** để thấy màu. Cảnh dùng Workbench nên **F12** render trực tiếp, không cần cài add-on hay tải model ngoài.',
       '4. Timeline có mốc mỗi 30 frame: bước 1 ở frame 1, bước 2 ở 31, bước 3 ở 61... Nhập frame theo bước hoặc nhấn Space xem hạt tín hiệu chạy theo đường đầu tiên trong cảnh. Hạt chỉ là diễn họa hướng truyền; màu/trạng thái thiết bị không được tính từ firmware.',
       '5. Đọc bảng chân trong hướng dẫn trước khi đấu mạch. Các header và kích thước 3D được giản lược; không dùng vị trí pin trên hình thay cho pinout thật.',
       '6. Với bài mạng, kết quả gói tin, latency và retransmission phải lấy từ Wireshark/NS-3/chương trình đi kèm. Blender thể hiện bố trí và luồng logic, không chạy mô hình điện, RF hay firmware.','',
       '## Danh mục','', '| Bài | Hướng dẫn | Cảnh chỉnh sửa được | Xem nhanh |','|---|---|---|---|']
for row in scenes:
    ex=row['id'];lines += [f'| {ex} | [Thao tác từng bước](../{row["guide"]}) | [Blender]({row["blend"]}) | [Hình bước 1]({ex}/buoc-01.jpg) |']
lines+=['','## Một số cảnh tiêu biểu','']
for ex in ['3.2','3.3','5.4','6.1','10.1','14.1']:
    lines += [f'### Bài {ex}','',f'![Mô hình 3D bài {ex}]({ex}/buoc-01.jpg)','']
lines += ['## Dựng lại từ mã nguồn','',
          'Toàn bộ hình học nằm trong [build_scenes.py](build_scenes.py); không nhập model của bên thứ ba. Các ảnh linh kiện chỉ dùng tham khảo nhận dạng, không được dán vào mô hình để giả ảnh thật. Font tiếng Việt được đóng gói trong file Blender.','',
          '```powershell',
          r'& "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" -b --python mo-phong-3d/build_scenes.py',
          '# Hoặc chỉ dựng một số bài:',
          r'& "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" -b --python mo-phong-3d/build_scenes.py -- 3.2 5.4',
          'python tools/update_illustrations.py','```','',
          'Chạy tại thư mục gốc repository, thay đường dẫn Blender theo máy. Nếu chỉ dựng vài bài, file manifest-part.json là báo cáo riêng; manifest.json của toàn bộ bộ bài vẫn được giữ. Hình render 1800×1200, JPEG chất lượng 90; mỗi bài giữ file `.blend` nén.','',
          'Bản dựng đã kiểm tra: Blender 4.5.14 LTS Windows x64; archive SHA256 `b9533d2397ac1984db4466fb23a7a4649391cca93f6e84209f9bcc60d071c8b9`. Blender portable được cài trong thư mục làm việc ngoài Git, không đưa bộ cài vào repository.']
(ROOT/'mo-phong-3d/README.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
