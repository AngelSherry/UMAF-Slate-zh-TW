import re,json,collections,sys
from pathlib import Path
P=Path(__file__).resolve().parent
load=lambda p:json.loads((P/p).read_text())
a=load('en-index.json'); idx={x:i for i,x in enumerate(a)}; engine=load('engine-draft.json')
def compact(s):return re.sub(r'\s+',' ',s).strip()
rev={}
for l in (P/'review.txt').read_text().splitlines():
 if not l or l.startswith('#'):continue
 k,v=l.split(' ',1);rev[a[int(k)]]=v
gl={k.casefold():v for k,v in (l.split('|') for l in (P/'glossary.txt').read_text().splitlines() if l)}
pat=re.compile(r'(?<![A-Za-z])(?:'+'|'.join(map(re.escape,sorted(gl,key=len,reverse=True)))+r')(?![A-Za-z])',re.I)
def lex(s):return pat.sub(lambda m:gl[m[0].lower()],s)
def polish(s):
 s=s.replace('▁',' ').replace('配置','設定').replace('引數','參數').replace('韌體程式','韌體').replace('客車','匯流排').replace('公交車','匯流排').replace('總線','匯流排').replace('韌體軟體','韌體').replace('霹靂','Thunderbolt').replace('熱備件','熱備援磁碟').replace('熱餘件','熱備援磁碟').replace('驅動器','磁碟機').replace('渠道','通道').replace('晶片集','晶片組').replace('車道','通道').replace('巷道','通道').replace('地址','位址').replace('時鐘','時脈').replace('圖象','影像').replace('頻寬寬度','頻寬').replace('國家4','P-state 4').replace('銀行','Bank').replace('重置','重設').replace('復位','重設').replace('計算機','電腦').replace('固件','韌體').replace('啟動順序','開機順序').replace('禁用','停用').replace('使能','啟用').replace('插口','插座').replace('軟盤','磁片').replace('攝像頭','攝影機').replace('埠口','連接埠').replace('預設情況下','預設').replace('允許您','可').replace('允許使用者','可').replace('您可以','可').replace('該裝置','此裝置')
 for k,v in {'羣': '群', '寄存器': '暫存器', '物理磁碟': '實體磁碟', '物理裝置': '實體裝置', '字節': '位元組', '安全啟動': '安全開機', '通訊埠': '連接埠', '協議': '協定', '政策': '原則', '接口': '介面', '証書': '憑證', '證書': '憑證', 'PCR 值庫': 'PCR 暫存器組', 'PCR 數據庫': 'PCR 暫存器組', 'PCR 銀行': 'PCR 暫存器組', 'PCR 存儲庫': 'PCR 暫存器組', '未找到': '找不到', '運行時': '執行階段', '閃存': '快閃記憶體', '數據': '資料', '中央處理器': 'CPU', '質量儲存': '大量儲存', '緩存': '快取', '硬件': '硬體', '軟件': '軟體', '此選項允許您': '可', '如果啟用此選項，': '啟用後，', '上電': '通電', '熱插拔槽位': '熱插拔插槽', '默認': '預設', '安全啟用': '安全啟用', '該選項': '此選項', '設置': '設定', '優化': '最佳化', '信息': '資訊', '千兆噸/秒': 'GT/s'}.items():s=s.replace(k,v)
 s=re.sub(r'\s+(?=[，。；：）])','',s)
 s=re.sub(r'(?<=[\u3000-\u9fff]) +(?=[\u3000-\u9fff])','',s)
 return re.sub(' +',' ',s).strip()
invariant=re.compile(r'(?:(?:[\d .xA-Fa-f+-]+)(?:MB|GB|KB|MHz|MHz|mV|ms|us|s|%|W|A|Gbps|x|h)?|[A-Z][A-Z\d_+#.:/-]*|[a-zA-Z]+_[\w./]+|[\dA-Za-z]+==[\w/]+|T(?:rc|fa|rr|wr|rd|ck|cw|rp|rt|cl|ra|rf|wt|ck)[A-Za-z\d]*|[A-Za-z]+DrvStren|Rtt\w+|[A-Za-z]+Setup|RZQ/\d+)',re.I if False else 0)
def rule(x):
 if x in rev:return rev[x],'edited'
 s=compact(x)
 if re.fullmatch(r'(?:[+-]?\d+(?:\.\d+)?\s*(?:[kmg]hz|[kmgt]b|gbps|gbs|[mun]s|mv|v|ma|a|w|asids?)|VIRT\s+\d+\s+\d+|(?:\d+\.){3}\d+)',s,re.I):return x,'identifier'
 if re.fullmatch(r'[%0-9adlsxX:/. -]+',s) and '%' in s:return x,'identifier'
 if re.fullmatch(r'(?:VDDP|VDDG) voltage \([+-]?\d+mv\)',s,re.I):return re.sub(r' voltage \(([+-]?\d+)mv\)',r' 電壓（\1 mV）',s,flags=re.I),'terms'
 m=re.fullmatch(r'Physical Disk (\d+): XX: SATA, Size, Ready',s)
 if m:return '實體磁碟 '+m[1]+'：XX：SATA，容量，就緒','terms'
 m=re.fullmatch(r'(AC|DC) (Maximum Performance|Better Performance|Better Battery|Battery Saver) Limit',s)
 profiles={'Maximum Performance':'最高效能','Better Performance':'效能優先','Better Battery':'續航優先','Battery Saver':'節電'}
 if m:return m[1]+' '+profiles[m[2]]+'功耗上限','terms'
 m=re.fullmatch(r'Power limit adjustment percent for \[(.+?)\] on (AC|DC): 0 - 100',s)
 if m and m[1] in profiles:return m[2]+' 供電時「'+profiles[m[1]]+'」的功耗上限百分比，範圍 0～100。','terms'
 if s in ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'):
  return str(('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()).index(s)+1)+' 月','terms'
 if s in gl:return gl[s.lower()],'terms'
 if s.lower() in gl:return gl[s.lower()],'terms'
 for reg,rep in [(r'([0-9A-Fa-f]+h?) Clk',r'\1 週期'),(r'([\d.]+) ohm',r'\1 Ω'),(r'(\d+) CCDs?',r'\1 個 CCD'),(r'PState (\d+)',r'P-state \1'),(r'(\S+) Ctrl',r'\1 控制'),(r'Specify (T\w+)',r'設定 \1。'),(r'(?:ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN) (\(.+\))',r'\1 核心'),(r'(\S+) under I2C (\d+) Bus',r'I2C \2 匯流排：\1'),(r'(\d+) Hours?',r'\1 小時')]:
  m=re.fullmatch(reg,s,re.I)
  if m:return m.expand(rep),'terms'
 if invariant.fullmatch(s) or not re.search('[A-Za-z]{2}',s):return x,'identifier'
 if any(s.startswith(q) for q in ['PcdMsg','STT_','PcdCfg','http://','https://']):return x,'identifier'
 # Short compound labels with no unaccounted-for English words use a stable technical glossary.
 l=lex(s)
 rem=pat.sub(' ',s)
 words=re.findall('[A-Za-z]{2,}',rem)
 if len(s)<80 and l!=s and all(t.upper()==t or re.search('[a-z][A-Z]|[A-Z].*[A-Z]',t) or t in ('mV','MHz','MHz','ms','us','Clk','Gb','Gbps') for t in words):
  return polish(l),'terms'
 if re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{1,26}',s) and (not re.search('[aeiou]',s,re.I) or re.search('[a-z][A-Z]',s) or s.upper()==s):return s,'identifier'
 return polish(engine[str(idx[x])]),'local-mt'
from editorial import edit,variant
cat={};qa={};raws={x for p in load('inventory.json').values() for group in p for lang,v in group.items() if lang.startswith('en') for x in v.values() if x.strip()}
for raw in sorted(raws):
 x=raw.strip()
 y,method=rule(x)
 # Keep the exact control glyph / selector response groups checked by EDK II.
 if x in ['Y','N','D (d)','G (g)','C (c)','Y (y)','N (n)','O (o)','!','!!','?']:y=x;method='identifier'
 revised=edit(idx[x],x,y)
 if revised!=y:method='copyedited'
 y=revised
 cat[raw]=variant(raw,y)
 qa[x]=[y,method]
cat.update(load('extras.json'))
for i in range(1,16):
 for en,tw in [('Sign','方向'),('Magnitude','幅度')]:cat[f'Core {i} Curve Optimizer {en}']=f'核心 {i} 偏移'+('方向' if en=='Sign' else '量')
cat['Slate:GearDownHelp']='DDR4 以半速時脈取樣命令與位址，放寬訊號時序；資料傳輸率維持不變。'
(P/'catalog.json').write_text(json.dumps(cat,ensure_ascii=False,indent=1))
(P/'authoring-qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=1))
print(collections.Counter(v[1] for v in qa.values()))
