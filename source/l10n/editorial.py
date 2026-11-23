"""Taiwan UI copy pass; invoked on display strings only. Never edit lookup keys."""
import re,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
# Numeric IDs name this exact frozen English inventory, not offsets into newer firmware.
if hashlib.sha256((P/'en-index.json').read_bytes()).hexdigest()!='07d638ff17ff19e08f14202d8d57ef76e235eddd5618f8298150cf544e8e7fbd':
 raise ValueError('English index differs; rebind and review copy edits before building')
roles=json.loads((P/'roles.json').read_text())
manual={int(s.split(' ',1)[0]):s.split(' ',1)[1] for s in (P/'copyedits.txt').read_text().splitlines() if s}
if len(manual)!=len((P/'copyedits.txt').read_text().splitlines()):raise ValueError('Duplicate or empty copy edit')
terms={
'選擇 a ':'選擇','一般幫助':'操作說明','幫助區域':'說明欄','滾動':'捲動','恢復預設值':'還原預設值','拋棄':'捨棄','退出':'離開','運行時':'執行時','目前對任何設定選項所做的變更':'尚未儲存的設定','設定設定':'設定','電源節省':'省電','未裝置':'未安裝','超時時間':'逾時','超時':'逾時','平臺':'平台','端口乘法器':'連接埠倍增器','端口':'連接埠','設備':'裝置','門控':'閘控','卡讀卡器':'讀卡機','智能卡':'智慧卡','藍芽':'藍牙','指紋識別':'指紋辨識','鼠標':'滑鼠','客戶端':'用戶端','以太網':'乙太網路','控制台':'主控台','串行':'序列','調試':'除錯','支持':'支援','字串以冒號分隔':'各組數值以冒號分隔','本地':'本機','當前':'目前','位寬':'位元寬度','優先級':'優先順序','生產環境':'正式環境','生產平台':'正式平台','補丁':'修補','電源適配器':'電源變壓器','適配器':'介面卡','熱備盤':'熱備援磁碟','全球熱備':'全域熱備','熱備磁碟':'熱備援磁碟','熱備實體磁碟':'熱備援磁碟','專屬熱備':'專用熱備','RAID 級別':'RAID 等級','作為全球':'作為全域','硬體流控':'硬體流量控制','實力乙太網路':'Realtek 乙太網路','域名':'網域名稱','附屬字串':'尾碼','黏貼':'貼上','低速度':'低速','黙認':'預設','PCIE':'PCIe','PCI-E':'PCIe',' DEBUG ':' 除錯 ','串列通用輸入/輸出':'序列通用輸出入','推薦':'建議','支援支援':'支援','設定參數設定':'設定參數','主機控制器正確報告自身':'主機控制器回報就緒','廣頻調製':'展頻調變','存儲':'儲存','舊的 PCI 裝置':'傳統 PCI 裝置','恢復使用者預設值':'還原使用者預設值','系統 CONFIG':'系統設定','韌體的啟動區塊區域':'韌體的啟動區塊','韌體的主區塊區域':'韌體的主區塊','簽名無效':'簽章無效','ROM 影像':'ROM 映像','更新影像':'更新映像','新影像':'新映像','完整影像':'完整映像','選擇影像檔':'選擇映像檔','驗證影像':'驗證映像','快閃記憶體影像':'韌體映像','NvRam':'NVRAM','NvRAM':'NVRAM','Nvme':'NVMe','Legacy':'傳統','Mebx':'MEBx','獨立GPU':'獨顯','FW 版本':'韌體版本','FW 模式':'韌體模式','選項檔路徑':'項目檔案路徑','的檔路徑':'的檔案路徑','RAID 水平':'RAID 等級','先前值':'上次設定值','一般幫助':'操作說明','裝置(s)':'裝置','磁碟(s)':'磁碟','陣列(s)':'陣列','按下 ENTER':'按 Enter','按下 ESC':'按 Esc','按 ESC':'按 Esc','按 <Enter> 來':'按 Enter ','按 <F2>':'按 F2','按下 ESC':'按 Esc','空閒容量':'可用容量','頻寬寬度':'頻寬','產生器器':'產生器','COMPUTER INC.':'COMPUTER INC.'}
han=r'[\u3400-\u9fff]'
def edit(i,en,y):
 role=roles.get(en,[])
 if i in manual:return manual[i]
 if i in (183,184,185,186,187,189,190):return {183:'PC ANSI',184:'VT100',185:'VT100+',186:'VT-UTF8',187:'TTY 終端機',189:'XTerm R6',190:'VT400'}[i]
 if 2510<=i<=2517:return f'裝置 {i-2510} 的 ASPM 模式'
 if 2518<=i<=2525:return f'裝置 {i-2518} 的熱插拔模式'
 if 2587<=i<=2590:return en.replace('_',' ').rstrip(':')+'：'
 if 2011<=i<=2013:return en.replace('_',' ')
 if 1385<=i<=1393:return y.replace('位於','使用').replace('通訊匯流排','匯流排')
 if i in (1353,1355):return '前置攝影機 '+str((i-1353)//2)+' 供電'
 if i in (1354,1356):return '控制前置攝影機 '+str((i-1354)//2)+' 的供電。'
 if 1001<=i<=1011 and i!=1007:
  w,n=re.findall(r'\d+',en);return f'{w} W '+('POR ' if i<=1006 else '')+f'設定 {n}（'+('商用／消費' if '/' in en or ' and ' in en else '商用' if 'COMMERCIAL' in en else '消費')+'型）'
 if 1052<=i<=1066:
  s=en.split('_')
  if len(s)==2:return 'STT 係數 '+s[-1]
  return ('STT '+s[-1]+' 機身溫度上限' if 'TEMPERATURE' in s else 'STT '+s[-1]+' 的 '+('α' if s[1]=='ALPHA' else 'C')+' 係數')
 if 1314<=i<=1327 and i%2==0:return '時脈請求 '+re.search(r'REQ(\d)',en)[1]+' 電源管理'
 if i in (1117,1120):return 'SATA 埠 '+en[-1]+' 積極休眠'
 if i in (1184,1186,1188):return 'UART '+en.split()[1]+' 傳統模式'
 if i in (1315,1317,1319,1321,1323,1325,1327):
  where=['M.2 無線網卡插槽 J92','板上網路晶片 U55','M.2 行動網卡插槽 J90','Thunderbolt 接頭 CON1','DT x4 插槽 J79','M.2 SSD 插槽 J19','MXM x8 插槽 J10'][(i-1315)//2]
  return '決定'+where+'是否使用時脈請求訊號（CLK_REQ'+re.search(r'REQ(\d)', en, re.I)[1]+'#）。'
 if i in (1023,1025,1027,1029,1037):return '設定'+{1023:'低溫點',1025:'中溫點',1027:'高溫點',1029:'臨界溫度',1037:'溫度遲滯範圍'}[i]+'，單位 °C。'
 if 1415<=i<=1434:return re.search(r'([+-]\d+(?:\.\d+)?)',en)[1]+' mV'
 if 1438<=i<=1457:
  n,m=re.findall(r'[+-]\d+(?:\.\d+)?',en);return f'ANPEC {n}／TI {m} mV'
 if i in (1461,1462):return '常供電 '+re.search(r'\+\d+',en)[0]+' mV'
 if 1556<=i<=1569:
  n,v,u=re.fullmatch(r'(\d+)bit \((\d+)(GB|TB)\)',en,re.I).groups();return f'{n} 位元（{v} {u}）'
 if 1750<=i<=1753:return f'DIMM {i-1750}：未安裝'
 if 1781<=i<=1788:return f'SATA 埠 {i-1781} 作為 eSATA'
 if 1789<=i<=1796:return f'SATA 埠 {i-1789} 供電'
 if i in (2139,2141,2143):
  v={2139:'軟碟機',2141:'硬碟',2143:'光碟機'}[i];return f'預先建立虛擬{v}，供稍後插入 USB {v}時使用。「自動」只在尚未接上 USB {v}時建立。'
 if i in (1676,1677,1678,2616,2617,2618):
  return '從可用的檔案系統尋找並啟動 '+re.search(r'Shell(?:x64|IA64)?\.efi',en,re.I)[0]+'。'
 if 3231<=i<=3243:y=y.replace('供應','佈建')
 if re.fullmatch(r'\d+(\.\d+)?(?:MHz|kHz|Hz|mV|W|ms|us|s|KB|MB|GB| Gbs| ASIDs)',en,re.I):
  num,unit=re.fullmatch(r'(\d+(?:\.\d+)?)\s*([A-Za-z]+)',en).groups(); return num+' '+{'mhz':'MHz','khz':'kHz','hz':'Hz','gbs':'Gb/s','us':'µs','asids':'個 ASID'}.get(unit.lower(),unit)
 if not re.search(han,y):return y
 for k,v in terms.items():y=y.replace(k,v)
 y=y.replace('Dimm','DIMM').replace('Uart ','UART ').replace('OpROM','Option ROM').replace('OPROM','Option ROM').replace('OS 下','作業系統中')
 y=re.sub(r'啟用\s*(?:[/／]|或)\s*停用\s*|停用或啟用\s*','控制',y)
 y=y.replace('控制鎖定傳統資源','選擇是否鎖定傳統資源').replace('無線可管理性','無線管理').replace('設定或變更 DASH ','設定 DASH ').replace('簽名清單','簽章清單').replace('驅動 BBS','光碟機 BBS')
 y=re.sub(r'若已鎖定，(.+?)將被停用。',r'鎖定後會停用\1。',y);y=re.sub(r'若已上鎖，(.+?)將被關閉。',r'鎖定後會停用\1。',y)
 y=re.sub(r'啟用 (XHCI\d|UART \d)$',r'\1 開關',y)
 y=y.replace('電源啟用','供電').replace('與板載','與板上').replace('板載','板上')
 y=re.sub(r'(?<=\d)(MHz|kHz|Hz|mV|GB|MB|TB|KB|W|A)\b',r' \1',y)
 y=re.sub('('+han+r')\s*:\s*',r'\1：',y);y=re.sub(r'\s+:\s*(?='+han+')','：',y)
 y=re.sub(r'(?<='+han+r')(?=[A-Za-z0-9])|(?<=[A-Za-z0-9])(?='+han+')',' ',y)
 y=re.sub(r' +([，。：；）])',r'\1',y)
 y=y.replace('...','…');y=re.sub(r'[！!]{2,}','！',y)
 if '。' not in y[-1:] and y.endswith('.') and i not in (2865,2866,3015,3016):y=y[:-1]+('。' if role==['help'] or len(y)>23 else '')
 if role==['help'] and not re.search(r'[。，：；！？…）\]!?]$',y) and re.search(han,y):y+='。'
 if set(role)<=set(['label','value','title']) and role and y.endswith('。') and len(y)<30:y=y[:-1]
 return y
def variant(raw,y):
 k=raw.strip()
 if roles.get(k)==['value']:return y
 return raw[:len(raw)-len(raw.lstrip())]+y+raw[len(raw.rstrip()):]
