"""Author scoped display help; never use a shared blank/help token as a standalone key."""
import json
from pathlib import Path
P=Path(__file__).resolve().parent
def make():
 a=json.loads((P/'en-index.json').read_text()); pairs=json.loads((P/'help-pairs.json').read_text()); notes={}
 def put(i,text):
  assert i not in notes and 0<text.count('。')<=2 and text.endswith('。'), (i,text)
  notes[i]=text
 for line in (P/'help-notes.txt').read_text().splitlines():
  if line and not line.startswith('#'):
   ix,text=line.split(' ',1);put(int(ix),text)
 for i,mode in [(447,'一般'),(451,'兩倍頻率'),(455,'四倍頻率')]:
  put(i,f'記憶體以{mode}模式重新整理後，至少等幾個時脈週期才能再下命令；可填 0x3C～0x3DE。')
 for i,n in [(407,'開列間隔 tRC'),(419,'四次開列的時窗 tFAW'),(429,'寫入後的恢復時間 tWR'),(433,'重複開列限制 tRCpage'),(437,'同區組的讀取間隔'),(441,'同區組的寫入間隔'),(445,'一般重新整理的等待時間 tRFC1'),(449,'兩倍頻率重新整理的等待時間 tRFC2'),(453,'四倍頻率重新整理的等待時間 tRFC4')]:
  put(i,f'選「手動」可自行設定{n}；選「自動」則由韌體決定。')
 for i,signal in [(511,'位址與命令'),(513,'晶片選擇與終端電阻控制'),(514,'時脈啟用')]:
  put(i,f'調整記憶體取樣前，{signal}訊號須提前多久穩定下來。填入時序設定碼 0x00～0x3F。')
 for i,signal in [(517,'時脈'),(524,'位址與命令'),(525,'晶片選擇與終端電阻控制'),(526,'時脈啟用')]:
  put(i,f'設定記憶體{signal}訊號的驅動阻抗。選項以歐姆（Ω）表示，阻抗越低，驅動越強。')
 for i,which in [(529,'一般運作時'),(538,'寫入時'),(541,'未被選取時')]:
  put(i,f'設定記憶體晶片{which}的終端電阻，用來抑制訊號反射。RZQ/2 代表參考電阻的一半。')
 for i,thing in [(464,'由讀轉寫'),(466,'由寫轉讀'),(468,'在同一晶片選擇訊號下連續寫入'),(470,'在同一條記憶體模組上連續寫入'),(472,'在不同記憶體模組間接續寫入'),(474,'在同一晶片選擇訊號下連續讀取'),(476,'在同一條記憶體模組上連續讀取'),(478,'在不同記憶體模組間接續讀取')]:
  put(i,f'{thing}時，兩次操作至少要間隔幾個記憶體時脈週期。')
 for i,n in [(1022,'低'),(1024,'中'),(1026,'高')]:
  put(i,f'設定風扇曲線的{n}溫點，單位為 °C。這個溫度對應「{n}溫 PWM」的風扇輸出。')
  put(i+8,f'設定風扇曲線在{n}溫點的輸出，用 PWM 占空比表示（0～100%）。數字是驅動訊號的比例，不是轉速。')
 for i,device in [(1047,'APU')]:
  put(i,'機身溫控需要降低功耗時，此值是 APU 持續功耗可降到的下限。單位為毫瓦，1000 mW 等於 1 W。')
 for i in range(1052,1058):
  put(i,f'這是機身表面溫度追蹤模型的校準參數 M{i-1051}，供主機板調校使用。韌體未列出換算方式。')
 for i in range(1058,1067):
  part=('APU','獨顯','HS2 熱點')[(i-1058)%3];k=(i-1058)//3
  put(i,[f'調整機身溫度模型中與{part}對應的 C 係數；這是校準值。',f'調整機身溫度模型中與{part}對應的 Alpha 係數；這是校準值。',f'設定機身溫控針對{part}使用的表面溫度上限；韌體未標示數值刻度。'][k])
 for i,part in [(1067,'估算誤差'),(1068,'誤差變化率')]:
  put(i,f'設定機身溫度模型修正{part}時採用的係數。這是校準值，不是溫度讀數。')
 for i,part in [(889,'干擾端的高 32 條資料線'),(891,'干擾端的低 32 條資料線'),(893,'干擾端的 ECC 資料線'),(898,'目標端的高 32 條資料線'),(900,'目標端的低 32 條資料線')]:
  put(i,f'以位元遮罩選取記憶體測試{part}；每個位元對應一條線。')
 for i,part in [(913,'讀取電壓'),(915,'讀取時序'),(917,'寫入電壓'),(919,'寫入時序')]:
  put(i,f'測量記憶體眼圖時，每次將{part}調整 1、2 或 4 格。步距越小，取樣點越密。')
 for i,p in [(1533,'負責初始化 AMD 平台的 AGESA'),(1534,'AMD 安全處理器的開機載入程式'),(1535,'AMD 安全處理器的作業系統'),(1536,'AMD 開機載入程式（ABL）'),(1537,'AMD 平台設定資料（APCB）'),(1538,'AMD 平台開機資料（APOB）'),(1539,'CPU 微碼修補程式'),(1540,'管理電源與時脈的 SMU 韌體'),(1541,'管理高速 I/O 的 DXIO 韌體'),(1542,'MP2 協同處理器韌體'),(1543,'遠端鍵盤、螢幕與滑鼠控制引擎（KVM）'),(1544,'顯示卡韌體（VBIOS）'),(1545,'UEFI 顯示驅動程式（GOP）'),(1546,'嵌入式控制器（EC）韌體'),(1547,'USB 供電協定（PD）第 1 區的韌體'),(1548,'USB 供電協定（PD）第 2 區的韌體'),(1550,'TI USB 供電控制器韌體')]:
  put(i,f'這是{p}的版本號碼，供核對目前韌體版本。')
 for i,n in [(2587,'A1'),(2588,'A2'),(2589,'B1'),(2590,'B2')]:
  put(i,f'顯示韌體在 {n} 記憶體插槽偵測到的模組資訊。')
 for i,n in [(1254,'最高效能'),(1256,'效能優先'),(1258,'續航優先'),(1260,'最高效能'),(1262,'效能優先'),(1264,'續航優先'),(1266,'節電')]:
  p='接上變壓器' if i<1260 else '使用電池'
  put(i,f'{p}時，將「{n}」模式的功耗上限設為指定比例。填 0～100，單位是百分比。')
 used=set();rules={}
 for row in pairs:
  s,h=row['prompt'],row['help'];clean=s.strip()
  if clean not in a:continue
  i=a.index(clean)
  if i not in notes:continue
  used.add(i);key=(s,h);v=notes[i]
  assert rules.get(key,v)==v
  rules[key]=v
 assert used==set(notes),set(notes)-used
 return rules
