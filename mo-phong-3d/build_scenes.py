"""Blender 4.5 background renderer. No external models, add-ons or GUI required.

Usage: blender -b --python mo-phong-3d/build_scenes.py -- [exercise ...]
Geometry is an educational layout, not dimensioned CAD or an electrical/RF solver.
"""
import bpy, math, json, re, sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'mo-phong-3d'
FONT = None
for candidate in ['C:/Windows/Fonts/arial.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
    if Path(candidate).exists():
        FONT = bpy.data.fonts.load(candidate)
        break

COLORS = {'pcb':(.015,.35,.36,1),'green':(.02,.43,.2,1),'blue':(.025,.36,.75,1),
 'black':(.035,.05,.075,1),'silver':(.63,.7,.76,1),'gold':(.95,.62,.14,1),
 'white':(.9,.94,.97,1),'ink':(.04,.10,.17,1),'red':(.92,.08,.12,1),
 'cyan':(.02,.67,.9,1),'orange':(1,.39,.035,1),'purple':(.55,.13,.85,1),
 'floor':(.78,.84,.89,1),'screen':(.015,.065,.105,1)}
M={}
PATHS=[]

def mat(name):
    if name not in M:
        m=bpy.data.materials.new(name);m.diffuse_color=COLORS[name];M[name]=m
    return M[name]

def cube(name, p, size, color, bevel=.06):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=name;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat(color))
    if bevel:
        mod=o.modifiers.new('Rounded edges','BEVEL');mod.width=bevel;mod.segments=2
        o.modifiers.new('Normals','WEIGHTED_NORMAL')
    return o

def cyl(name,p,r,depth,color):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=depth,location=p)
    o=bpy.context.object;o.name=name;o.data.materials.append(mat(color));return o

def sphere(name,p,r,color):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=r,location=p)
    o=bpy.context.object;o.name=name;o.data.materials.append(mat(color));return o

def text(s,p,size=.27,color='ink',align='CENTER'):
    c=bpy.data.curves.new(s,'FONT');c.body=s;c.size=size;c.align_x=align;c.align_y='CENTER'
    if FONT:c.font=FONT
    o=bpy.data.objects.new(s,c);bpy.context.collection.objects.link(o);o.location=p;c.materials.append(mat(color));return o

def line(name,points,color='cyan',width=.045):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=width;c.bevel_resolution=3
    sp=c.splines.new('POLY');sp.points.add(len(points)-1)
    for v,p in zip(sp.points,points):v.co=(*p,1)
    o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);c.materials.append(mat(color));return o

def arrow(a,b,label='',color='cyan',yoff=0):
    a=Vector(a);b=Vector(b);line(label,[a,b],color,.055)
    PATHS.append([tuple(a),tuple(b)])
    d=(b-a).normalized();side=Vector((-d.y,d.x,0))
    line('arrow', [b-d*.32+side*.16,b,b-d*.32-side*.16],color,.055)
    if label:text(label,tuple((a+b)*.5+Vector((0,.35+yoff,.12))),.25,color)
    return a,b

def pin(name,p,color='gold'):
    cube('pin '+name,p,(.13,.13,.18),color,.015)
    return p

def board(x,y,name='UNO',kind='uno'):
    w,h=(3.8,3.2) if kind=='uno' else (2.5,3.2)
    cube(name+' PCB',(x,y,.35),(w,h,.15),'pcb' if kind=='uno' else 'black')
    cube('USB socket',(x-w/2+.15,y+.75,.58),(.65,.7,.42),'silver')
    cube('MCU',(x+.35,y,.52),(1.25,.65,.18),'black')
    if kind!='uno':
        cube('RF shield',(x+.12,y+.3,.58),(1.5,1.3,.2),'silver')
        for i in range(6):line('antenna',[(x-.65+i*.23,y+1.02,.68),(x-.65+i*.23,y+1.37,.68)],'gold',.025)
    else:
        for i in range(14):cube('MCU pin',(x-.25+i*.09,y-.45,.48),(.04,.15,.07),'silver',0)
        cyl('power jack',(x-1.3,y-.8,.55),.26,.35,'black')
    for side in [-1,1]:
        cube('header',(x,y+side*(h/2-.2),.5),(w-.5,.22,.25),'black')
        for i in range(12):pin(str(i),(x-(w-.7)/2+i*(w-.7)/11,y+side*(h/2-.2),.66))
    sphere('Power LED',(x-.85,y-.45,.6),.10,'red')
    text(name,(x,y-.95,.69),.25,'white')
    text('USB',(x-w/2+.18,y+1.25,.23),.18)
    return {'L':(x-w/2+.4,y-1.4,.72),'R':(x+w/2-.4,y+1.4,.72),'C':(x,y,.75)}

def module(x,y,kind,label=None):
    label=label or kind
    cube(kind+' PCB',(x,y,.32),(2.5,2.3,.14),'green' if kind not in ['MAX7219','LCD1602'] else 'blue')
    ports={}
    if kind=='DS1307':
        cyl('CR2032 holder',(x+.35,y+.1,.52),.67,.25,'black')
        cyl('CR2032 coin cell',(x+.35,y+.1,.68),.57,.08,'silver')
        text('+',(x+.35,y+.1,.74),.37)
        cube('DS1307 IC',(x-.7,y-.35,.5),(.48,.8,.16),'black')
    elif kind=='DHT11':
        cube('Blue vented DHT11',(x,y,.85),(1.45,1.55,.95),'blue')
        for i in range(6):cube('vent',(x-.5+i*.2,y,1.34),(.08,1.1,.015),'screen',.01)
    elif kind=='HC-05' or kind=='CC2531':
        cube('Radio shield',(x,y-.22,.53),(1.5,1.15,.18),'silver')
        for i in range(6):line('PCB antenna',[(x-.65+i*.25,y+.55,.43),(x-.65+i*.25,y+.95,.43)],'gold',.035)
        if kind=='CC2531':cube('USB-A',(x,y-1.3,.45),(1,.75,.28),'silver')
        else:cube('KEY button',(x+.85,y-.8,.55),(.3,.3,.18),'black')
    elif kind=='LCD1602':
        cube('LCD bezel',(x,y,.52),(4.4,1.65,.25),'black')
        cube('LCD panel',(x,y,.67),(3.9,1.18,.04),'green')
        text('07:30:00  AL ON\n     MINH HOA',(x,y,.71),.25,'ink')
    elif kind=='PIR':
        sphere('Fresnel dome',(x,y,.6),.72,'white')
    elif kind=='MAX7219':
        cube('8x8 matrix',(x,y,.55),(2.1,2.1,.3),'black')
        for row in range(8):
            for col in range(8):
                cyl('LED',(x-.87+col*.25,y-.87+row*.25,.72),.07,.04,'red' if col in [1,6] or row==4 else 'screen')
    else:
        cube('IC',(x,y,.52),(1.3,.9,.18),'black')
    text(label,(x,y-1.5,.23),.30)
    for i,n in enumerate(['VCC','GND','DATA','CLK']):
        p=(x-1.03+i*.68,y-1,.55);ports[n]=pin(n,p)
    return ports

def laptop(x,y,label='PC',screen='Terminal / Wireshark'):
    cube('Laptop base',(x,y,.25),(3.4,2.2,.2),'silver')
    cube('Keyboard',(x,y-.15,.38),(2.9,1.1,.03),'black')
    for i in range(8):line('key row',[(x-1.3+i*.36,y-.65,.41),(x-1.3+i*.36,y+.35,.41)],'silver',.018)
    cube('Display backing',(x,y+1,.95),(3.4,.2,1.9),'black')
    # Display laid out toward the camera: text on an inclined plane.
    o=cube('Display',(x,y+.83,1),(3.1,.04,1.55),'screen');
    t=text(screen,(x,y+.79,1.05),.23,'cyan');t.rotation_euler=(math.pi/2,0,0)
    text(label,(x,y-1.5,.22),.32)
    return (x,y,.7)

def server(x,y,label='Server'):
    cube(label,(x,y,1.1),(2.2,1.7,1.9),'black')
    for i in range(4):
        cube('Rack tray',(x,y-.87,.5+i*.4),(1.85,.05,.28),'silver')
        sphere('Activity LED',(x+.7,y-.94,.5+i*.4),.055,'green')
    text(label,(x,y-1.55,.25),.34)
    return (x,y,1)

def router(x,y,label='Router / AP'):
    cube(label,(x,y,.6),(2.7,1.7,.65),'white')
    for xx in [-.95,.95]:cyl('Wi-Fi antenna',(x+xx,y+.55,1.35),.065,1.3,'black')
    for i in range(4):sphere('link',(x-.65+i*.4,y-.87,.65),.065,'green')
    text(label,(x,y-1.4,.23),.30)
    return (x,y,.9)

def lamp(x,y,label='LED / lamp',on=True):
    cyl('lamp base',(x,y,.3),.6,.35,'silver')
    cyl('lamp stem',(x,y,.78),.12,.7,'black')
    sphere('lamp',(x,y,1.4),.62,'gold' if on else 'white')
    text(label,(x,y-1.25,.23),.28)
    return (x,y,1)

def wire(a,b,label,color='cyan',route=0):
    a=Vector(a);b=Vector(b);h=.95+abs(route)*.18
    points=[a,Vector((a.x,a.y-.5-route*.15,h)),Vector((b.x,b.y-.5-route*.15,h)),b]
    line(label,points,color,.035)
    PATHS.append([tuple(p) for p in points])
    text(label,tuple((points[1]+points[2])*.5+Vector((0,-.15,.1))),.22,color)

def rail(a,b,label,color):
    wire(a,b,label,color,3 if color=='red' else 4)

def circuit(ex):
    if ex=='2.3':
        return circuit('3.1')
    if ex=='2.2':
        a=board(-4,0,'Arduino UNO')
        laptop(5,1,'PC / USB','Serial: 9600 / 115200')
        cube('D2 pushbutton',(.4,-1,.5),(1,1,.55),'black')
        wire(a['R'],(.2,-.6,.8),'D2 -> nut nhan','cyan')
        wire((.6,-1.3,.8),a['L'],'Nut -> GND','black',1)
        text('INPUT_PULLUP',(1,-2.5,.3),.38)
        text('Giu >3 s: CONFIG | Chon 9600 / 115200',(0,3.5,.3),.34)
        return 'Mot nut D2 xuong GND | Nhan = LOW | LED D13 | Doi baud Serial Monitor theo firmware'
    if ex.startswith('2.'):
        a=board(-5,0,'NodeMCU ESP8266','esp');b=board(4,0,'Arduino UNO')
        wire(a['R'],b['R'],'D1 TX -> D10 RX','cyan',0)
        wire(b['L'],a['L'],'D9 TX -> 1k/2k -> D2 RX','orange',1)
        cube('1k resistor',(-.7,-2,.8),(.85,.2,.22),'gold')
        cube('2k resistor',(.7,-2,.8),(.85,.2,.22),'gold')
        rail((-5,-1.5,.65),(4,-1.5,.65),'GND chung','black')
        return 'UART 9600 8N1 | Noi cheo TX/RX | Khong dua 5V vao GPIO ESP'
    if ex.startswith('3.'):
        a=board(-5,0,'Arduino UNO')
        if ex=='3.3':
            modules=[module(-.8+i*2.6,1,'MAX7219',f'MAX7219 #{i+1}') for i in range(4)]
            wire(a['R'],modules[0]['DATA'],'D11 MOSI -> DIN','cyan')
            for i in range(3):arrow((.25+i*2.6,1.6,1),(1.25+i*2.6,1.6,1),'DOUT','orange')
            line('CLK bus',[(-5,3,.85),(8,3,.85)],'purple')
            line('LOAD bus',[(-5,3.7,.85),(8,3.7,.85)],'orange')
            for i,m in enumerate(modules):
                line('CLK',[(i*2.6-.8,3,.85),m['CLK']],'purple',.03)
                line('LOAD',[(i*2.6-.4,3.7,.85),(i*2.6-.4,2.1,.8)],'orange',.03)
            text('D13 SCK -> CLK chung',(.5,3.35,.9),.27,'purple')
            text('D10 -> CS / LOAD chung',(.5,4.1,.9),.27,'orange')
            cube('5V external PSU',(4,-2.6,.4),(3,1,.55),'black')
            text('5V ngoai + GND chung',(4,-3.5,.23),.29)
            for m in modules:
                wire((3,-2.6,.8),m['VCC'],'','red',4)
                wire((5,-2.6,.8),m['GND'],'','black',5)
            return 'SPI mode 0 | 1 MHz | 4 x 16 bit = 64 xung / hang | Khong noi DOUT ve MISO'
        rtc=module(1,1.3,'DS1307')
        wire(a['R'],rtc['DATA'],'A4 SDA -> SDA','cyan')
        wire(a['L'],rtc['CLK'],'A5 SCL -> SCL','orange',1)
        rail((-4,-1.4,.7),rtc['GND'],'GND','black')
        rail((-3.5,-1.4,.7),rtc['VCC'],'5V','red')
        if ex=='3.2':
            lcd=module(6,1.3,'LCD1602')
            wire(rtc['DATA'],lcd['DATA'],'SDA chung','cyan',2)
            wire(rtc['CLK'],lcd['CLK'],'SCL chung','orange',3)
            for i,n in enumerate(['MODE D4','UP D5','DOWN D6','SET D7']):
                cube(n,(i*1.5,-2.6,.45),(.6,.6,.4),'black');text(n,(i*1.5,-3.2,.25),.22)
                wire((-3.5+i*.25,-1.4,.7),(i*1.5,-2.6,.7),'','purple',i+1)
            cyl('Piezo D9',(7,-2.4,.55),.6,.5,'black');text('Piezo D9',(7,-3.4,.23),.24)
            sphere('LED D8',(5.5,-2.4,.6),.22,'red');text('D8',(5.5,-3.1,.23),.23)
            return 'I2C chung A4/A5 | Nut INPUT_PULLUP xuong GND | Dia chi LCD: do truoc khi sua code'
        return 'RTC DS1307: SDA=A4, SCL=A5 | CR2032 giu gio khi mat nguon chinh'
    if ex.startswith('5.'):
        if ex=='5.2':
            laptop(-6,0,'Proteus / COMPIM','Virtual COM A')
            laptop(6,0,'PC terminal / Web','Virtual COM B')
            arrow((-4,1,1),(4,1,1),'COM A <-> com0com <-> COM B','cyan')
            text('Mo phong cong noi tiep tren cung PC',(0,-2,.3),.4)
            return 'COM ao chi truyen byte stream | Khong mo phong Bluetooth RF / pairing / song vo tuyen'
        a=board(-5,0,'Arduino UNO');hc=module(.3,1,'HC-05')
        soft=ex=='5.1'
        wire(hc['DATA'],a['R'],'HC TXD -> '+('D10 RX' if soft else 'D0 RX'),'cyan')
        wire(a['L'],hc['CLK'],('D11 TX' if soft else 'D1 TX')+' -> 1k/2k -> HC RXD','orange',1)
        rail((-5,-1.5,.7),hc['GND'],'GND chung','black')
        cube('1k / 2k divider',(-1.5,-2,.6),(1.4,.4,.25),'gold')
        laptop(6,1,'PC / Bluetooth SPP','AT / Web / Serial')
        arrow((1.8,2.4,1.1),(4.5,2.4,1.1),'Bluetooth SPP','purple')
        if ex=='5.4':
            d=module(3.5,-2.4,'DHT11');wire(a['R'],d['DATA'],'D2 -> DATA','green',2)
            text('JSON moi 2 s',(7,-3,.23),.26)
        if ex=='5.2':text('COM ao chi gia lap byte stream, khong gia lap song RF',(.1,4.2,.25),.3)
        return 'HC-05 RXD / KEY logic 3.3V | AT: 38400 | Data: 9600 | VCC theo dung breakout'
    if ex in ['8.3','8.4']:
        a=board(-5,0,'Wemos D1 mini','esp');d=module(.2,0,'DHT11')
        wire(a['R'],d['DATA'],'D2 / GPIO4 -> DATA','cyan')
        rail(a['L'],d['VCC'],'3.3V','red');rail((-5,-1.6,.7),d['GND'],'GND','black')
        text('Pull-up DATA len 3.3V',(.1,2,.25),.29)
        server(6,1,'Home Assistant')
        arrow((-3.2,3,1),(5,3,1),'Wi-Fi / Native API 6053','purple')
        lamp(6,-2.7,'LED D4 active LOW')
        return 'DHT11 -> HA: 10 s | Tren 30 C / 10 s: ON | Duoi 28 C / 10 s: OFF | 28-30: giu trang thai'

def network(ex):
    if ex.startswith('4.'):
        pc=laptop(-7,-1,'PC / Smartphone','IoT dashboard');ap=router(-2,1,'Home Gateway')
        pir=module(3,2,'PIR','Motion detector');l=lamp(7,-1,'Smart lamp')
        arrow(pc,ap,'LAN / Wi-Fi');arrow(ap,(3,2,1),'IoT registration')
        arrow((3,1,1),l,'Motion -> light ON','orange')
        if ex=='4.3':
            cube('Camera',(7,3,.8),(1.2,1,.9),'white');sphere('Lens',(7,2.4,.8),.26,'black')
            cyl('Siren',(3,-2,1),.6,1.2,'red');text('Siren + camera',(4,-3,.23),.3)
        return 'Packet Tracer: gateway, DHCP, IoT registration va dieu kien su kien | 3D minh hoa topology'
    if ex.startswith('6.'):
        server(-7,1,'HA / Zigbee2MQTT');co=module(-2,1,'CC2531','Coordinator USB')
        l=lamp(4,2,'Zigbee light');sn=module(1,-2,'CC2531','Sniffer USB rieng')
        laptop(7,-2,'PC capture','Wireshark / ZBOSS')
        arrow((-5.6,1,1),(-3.3,1,1),'USB','black')
        arrow((-1,1.8,1),(3,2,1),{'6.1':'MAC / NWK','6.2':'APS / ZCL ON-OFF','6.3':'Join / Transport Key'}[ex],'orange')
        arrow((3,1.3,1),(1,-.5,1),'Cung channel','purple')
        arrow((2.5,-2,1),(5.3,-2,1),'USB capture','cyan')
        if ex=='6.3':
            cube('Joining sensor',(6,3,.6),(1.2,.9,.4),'white')
            arrow((5,3,1),(-.5,2.7,1),'Association -> Device announce','green')
        return 'Coordinator va sniffer la 2 thiet bi | Cung channel (vi du 15) | Khong tu suy dien key tu payload ma hoa'
    if ex=='8.2':
        board(-7,1,'ESPHome ESP','esp');router(-1,1);server(6,1,'Home Assistant')
        laptop(0,-3,'PC capture','tcp.port == 6053')
        arrow((-5.5,1,1),(-2.8,1,1),'Wi-Fi','purple');arrow((.8,1,1),(4.5,1,1),'Native API 6053','cyan')
        return 'mDNS UDP5353 | HTTP TCP80 | Native API TCP6053 | PC phai thay duoc traffic can bat'
    if ex=='9.1':
        laptop(-6,0,'Windows host','VMware / VirtualBox')
        server(0,1,'Debian VM');laptop(6,0,'NetAnim','ns-3.43 / XML')
        arrow((-4,2,1),(-1.5,2,1),'SSH / shared folder')
        arrow((1.5,2,1),(4.5,2,1),'Build -> run -> XML','orange')
        text('ns-3.43 = version co dinh',(.1,-3,.25),.37)
        return 'Blender chi minh hoa moi truong | Ket qua mo phong mang phai lay tu ns-3 / FlowMonitor'
    if ex=='10.1':
        server(-8,1,'Remote Host');server(-3,1,'PGW / EPC')
        cyl('eNB pole',(2,1,1.6),.12,3,'silver')
        for dx in [-.4,.4]:cube('LTE antenna',(2+dx,1,2.6),(.3,.5,1.1),'white')
        text('eNodeB',(2,-.8,.25),.36)
        for i in range(3):
            cube('UE phone',(7+i*.25,-2+i*2,.55),(.8,1.35,.2),'black')
            arrow((2.5,1,1.7),(6.5+i*.25,-2+i*2,.7),'LTE' if i==1 else '', 'purple')
        text('UE: 1 / 5 / 10 nodes',(6,-3.6,.25),.31)
        arrow((-6.5,1,1),(-4.5,1,1),'P2P','cyan');arrow((-1.5,1,1),(.8,1,1),'EPC','orange')
        return 'UDP 128 byte / 100 ms | UE 7.0.0.0/8 | Khoang cach 20/100/500m | Hinh khong theo ti le vat ly'
    if ex.startswith('12.') or ex.startswith('14.'):
        board(-7,0,'ESP32 / ESP8266','esp');router(-2,1,'Wi-Fi AP')
        server(3,1,'Mosquitto broker');laptop(8,-1,'Home Assistant / PC','MQTT cmd / state')
        arrow((-5.3,1,1),(-3.6,1,1),'Wi-Fi','purple')
        arrow((-.5,1,1),(1.7,1,1),'TLS 8883' if ex=='14.1' else 'MQTT 1883','orange')
        arrow((4.5,1,1),(6.4,1,1),'subscribe','cyan')
        arrow((6,-2.8,.8),(-5,-2.8,.8),'cmd -> device | state -> subscriber','green')
        detail={'12.1':'Publish JSON sensor: simulated=true | Khong phai so do cam bien that',
        '12.2':'Topic cmd rieng state | Lenh den thiet bi -> phan hoi trang thai thuc',
        '12.3':'Retained state | Last Will offline | Reset -> online va state moi',
        '14.1':'So sanh plaintext 1883 voi TLS 8883 | Xac minh CA va hostname',
        '14.2':'Replay: cung ban tin | Anti-replay: HMAC + time +/-10s + sequence tang',
        '14.3':'Reconnect/backoff | Tai co gioi han | Quan sat kha nang phuc hoi'}[ex]
        if ex=='14.2':
            cube('Rejected replay',(1,-3.7,.5),(3.2,.8,.5),'red');text('REPLAY REJECT',(1,-3.7,.79),.27,'white')
        if ex=='14.1':
            cube('TLS padlock',(1.1,3.1,.7),(.9,.65,.7),'gold')
            line('lock shackle',[(.8,3.1,1),(.8,3.1,1.6),(1.4,3.1,1.6),(1.4,3.1,1)],'silver',.07)
            text('CA / hostname verification',(1,3.9,.3),.29)
        if ex in ['12.3','14.3']:
            text('OFFLINE -> reconnect -> ONLINE',(1,3.8,.3),.35,'red')
        return detail
    if ex.startswith('13.'):
        board(-7,0,'ESP / PC client','esp');server(7,1,'CoAP :5683')
        label={'13.1':'CON / NON + MID + token','13.2':'GET / Observe notifications','13.3':'Block2: 2KB / 128B = 16 blocks'}[ex]
        if ex=='13.1':
            server(0,1,'Drop proxy :5684')
            arrow((-5.2,1,1),(-1.6,1,1),label,'cyan')
            arrow((1.6,1,1),(5.5,1,1),'UDP5683','orange')
        else:
            arrow((-5.2,1,1),(5.5,1,1),label+' / UDP5683','cyan')
        arrow((5.5,-2,1),(-5.5,-2,1),'Response / ACK' if ex!='13.2' else 'Observe: server push, token giu nguyen','purple')
        if ex=='13.3':
            for i in range(16):cube(f'Block {i}',(-4.5+i*.6,-3.5,.4),(.48,.8,.4),'green' if i%2 else 'blue')
        return label+' | Day la minh hoa luong giao thuc, so do / pcap phai lay tu chuong trinh'
    return ''

def create(ex,guide):
    global M,FONT,PATHS
    # Hidden timeline labels cannot be selected through bpy.ops. Remove all
    # objects directly so a later exercise cannot inherit earlier step labels.
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj,do_unlink=True)
    M={};PATHS=[]
    for data in list(bpy.data.materials):
        if data.users==0:bpy.data.materials.remove(data)
    scene=bpy.context.scene;scene.timeline_markers.clear();scene.render.engine='BLENDER_WORKBENCH'
    scene.render.resolution_x=1800;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='JPEG';scene.render.image_settings.quality=90
    scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.45
    scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=False
    scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='WORLD'
    scene.display.shading.show_specular_highlight=True
    scene.display.shading.background_type='WORLD';scene.world.color=(.78,.84,.89)
    scene.view_settings.view_transform='Standard'
    cube('Workbench',(0,0,-.05),(24,15,.25),'floor')
    body=guide.read_text(encoding='utf8')
    title=body.splitlines()[0].lstrip('# ')
    text(title,(0,5.9,.17),.51)
    text('BLENDER 3D • MINH HỌA • KHÔNG PHẢI ẢNH CHẠY THẬT',(0,5.2,.17),.26,'blue')
    detail=circuit(ex) or network(ex)
    # Long technical lines split at separators to preserve readability.
    pieces=detail.split(' | ');mid=(len(pieces)+1)//2
    text(' | '.join(pieces[:mid]),(0,-4.9,.2),.32)
    text(' | '.join(pieces[mid:]),(0,-5.45,.2),.30)
    text('Vị trí header quy ước • Đấu theo bảng chân trong hướng dẫn • Không dùng hình thay sơ đồ điện',(0,-6.2,.17),.23)
    bpy.ops.object.camera_add(location=(0,-18,26))
    cam=bpy.context.object;cam.name='Camera overview'
    cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=25.5;scene.camera=cam
    steps=re.findall(r'^### Bước (\d+)\. (.+)$',body,re.M)
    scene.frame_start=1;scene.frame_end=max(60,30*len(steps))
    # A moving packet is an explicitly illustrative animation, not computed traffic.
    path=PATHS[0] if PATHS else [(-1,3.6,1),(1,3.6,1)]
    packet=sphere('Illustrative signal packet',path[0],.13,'orange')
    for index,point in enumerate(path):
        packet.location=point
        packet.keyframe_insert('location',frame=1+round(index*(scene.frame_end-1)/(len(path)-1)))
    for i,(num,step) in enumerate(steps):
        frame=1+i*30;scene.timeline_markers.new('Bước '+num+': '+step,frame=frame)
        obj=text('Bước '+num+' • '+step,(0,4.5,.18),.30,'blue')
        for at,hide in [(1,True),(frame,False),(frame+29,False),(frame+30,True)]:
            obj.hide_render=hide;obj.hide_viewport=hide
            obj.keyframe_insert('hide_render',frame=at);obj.keyframe_insert('hide_viewport',frame=at)
    for obj in scene.objects:
        if obj.animation_data and obj.animation_data.action:
            for fc in obj.animation_data.action.fcurves:
                for k in fc.keyframe_points:k.interpolation='CONSTANT' if fc.data_path.startswith('hide_') else 'LINEAR'
    folder=HERE/ex;folder.mkdir(exist_ok=True)
    for i,(num,step) in enumerate(steps):
        scene.frame_set(1+i*30)
        # Alternate slightly oblique and near overhead views without hiding labels.
        cam.location=(0,-18 if i%2==0 else -10,26 if i%2==0 else 30)
        cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(folder/f'buoc-{int(num):02}.jpg')
        bpy.ops.render.render(write_still=True)
    scene.frame_set(1)
    # Pack font for portable Vietnamese text, and save with the first step visible.
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/f'bai-{ex}.blend'),compress=True)
    return {'id':ex,'guide':str(guide.relative_to(ROOT)).replace('\\','/'),'blend':f'{ex}/bai-{ex}.blend','renders':len(steps),'detail':detail,'status':'illustration_not_hardware_result'}

if __name__=='__main__':
    selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    catalog=json.loads((ROOT/'docs/catalog.json').read_text(encoding='utf8'))
    result=[]
    for row in catalog:
        ex=row['id']
        if ex=='8.1' or (selected and ex not in selected):continue
        print('BUILD_LAB',ex,flush=True)
        result.append(create(ex,ROOT/row['guide']))
    target=HERE/('manifest-part.json' if selected else 'manifest.json')
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
