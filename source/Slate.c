/* SPDX-License-Identifier: BSD-2-Clause
 * Local graphical canvas for DisplayEngine, not a system console driver.
 * Does not change EFI protocols, display mode, variables, forms or input.
 */
#include "Slate.h"
#include <Protocol/GraphicsOutput.h>
#include <Protocol/HiiFont.h>
#include <Library/BaseMemoryLib.h>
#include <Library/BaseLib.h>
#include <Library/MemoryAllocationLib.h>
#include <Library/UefiBootServicesTableLib.h>
#include "SlateAtlas.h"
#include "SlateBrand.h"
typedef EFI_GRAPHICS_OUTPUT_BLT_PIXEL PX;
typedef EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL SLATE_OUT;
typedef EFI_GRAPHICS_OUTPUT_PROTOCOL GOP;
STATIC GOP *G;
STATIC EFI_HII_FONT_PROTOCOL *Font;
STATIC PX *Strip;
STATIC UINTN W,H,Cw,Ch,Cols,Rows,Left,Top;
STATIC BOOLEAN Active;
#include "SlateZh.inc"
STATIC EFI_SIMPLE_TEXT_OUTPUT_MODE Mode = {1,0,7,0,0,FALSE};
STATIC UINT32 CONST Ink[16]={0xdce8f2,0x9cc3ce,0x91e6bb,0x86d8d0,0xff9c90,0xe3afe4,0xffce86,0xc6d6e2,
  0x93a3b3,0xb2d6ed,0xa1efc5,0xa2e6e0,0xff9d94,0xe9b7e9,0xffda85,0xf3f9ff};
STATIC UINT32 CONST Paper[8]={0x102029,0x263a4a,0x20443b,0x91ead3,0x503039,0x382f48,0x403c32,0x182b35};
STATIC PX Pixel(UINT32 n){PX p={(UINT8)n,(UINT8)(n>>8),(UINT8)(n>>16),0};return p;}
STATIC VOID Fill(UINTN x,UINTN y,UINTN w,UINTN h,UINT32 rgb){
  PX p=Pixel(rgb);if(w && h && x<W && y<H && w<=W-x && h<=H-y) G->Blt(G,&p,EfiBltVideoFill,0,0,x,y,w,h,0);
}
STATIC INTN IndexOf(CHAR16 c){
  UINTN a=0,b=sizeof(Code)/sizeof(Code[0]);while(a<b){UINTN m=a+(b-a)/2;if(Code[m]<c)a=m+1;else b=m;}
  return a<sizeof(Code)/sizeof(Code[0]) && Code[a]==c?(INTN)a:-1;
}
STATIC VOID Glyph(UINTN x,UINTN width,CHAR16 c,PX ramp[256]){
  UINTN i,j,v; INTN idx=IndexOf(c); EFI_IMAGE_OUTPUT *img=NULL;
  CONST UINT8 *zh=(SlateZh() && (idx<0 || width==2*Cw)) ? ZhMask(c) : NULL;
  if(zh){
    for(j=0;j<Ch;j++){UINTN fy=j*53*256/(Ch-1),y0=fy>>8,y1=y0<53?y0+1:y0,wy=fy&255;
      for(i=0;i<width;i++){
        if(width==54 && Ch==54)v=zh[j*54+i];
        else{UINTN fx=i*53*256/(width-1),x0=fx>>8,x1=x0<53?x0+1:x0,wx=fx&255;
          UINTN p=zh[y0*54+x0]*(256-wx)+zh[y0*54+x1]*wx,q=zh[y1*54+x0]*(256-wx)+zh[y1*54+x1]*wx;
          v=(p*(256-wy)+q*wy+32768)>>16;}
        Strip[j*W+x+i]=ramp[v];}}
    return;
  }
  if(idx<0 && Font){EFI_STATUS s=Font->GetGlyph(Font,c,NULL,&img,NULL);
    if(EFI_ERROR(s) || !img || !img->Image.Bitmap || !img->Width || !img->Height)idx=IndexOf('?');}
  if(idx<0 && !img)idx=IndexOf('?');
  for(j=0;j<Ch;j++){
    UINTN fy=j*(ATLAS_H-1)*256/(Ch-1), y0=fy>>8, y1=(y0+1<ATLAS_H)?y0+1:y0, wy=fy&255;
    for(i=0;i<width;i++){
      if(idx>=0){
        if(width==ATLAS_W && Ch==ATLAS_H){v=Atlas[idx][j*ATLAS_W+i];}
        else {
          UINTN fx=i*(ATLAS_W-1)*256/(width-1), x0=fx>>8, x1=(x0+1<ATLAS_W)?x0+1:x0, wx=fx&255;
          CONST UINT8 *a=Atlas[idx];
          UINTN p0=a[y0*ATLAS_W+x0]*(256-wx)+a[y0*ATLAS_W+x1]*wx;
          UINTN p1=a[y1*ATLAS_W+x0]*(256-wx)+a[y1*ATLAS_W+x1]*wx;
          v=(p0*(256-wy)+p1*wy+32768)>>16;
        }
      } else {PX p=img->Image.Bitmap[(j*img->Height/Ch)*img->Width+(i*img->Width/width)];v=(p.Red+p.Green+p.Blue)/3;}
      Strip[j*W+x+i]=ramp[v];}}
  if(img){if(img->Image.Bitmap)FreePool(img->Image.Bitmap);FreePool(img);}
}
STATIC VOID Ramp(PX r[16],UINT32 fg,UINT32 bg){
  PX a=Pixel(bg),b=Pixel(fg);UINTN k;for(k=0;k<16;k++){r[k].Red=(UINT8)((a.Red*(15-k)+b.Red*k)/15);
  r[k].Green=(UINT8)((a.Green*(15-k)+b.Green*k)/15);r[k].Blue=(UINT8)((a.Blue*(15-k)+b.Blue*k)/15);r[k].Reserved=0;}
}
STATIC VOID FontRamp(PX r[256],UINT32 fg,UINT32 bg){
  PX a=Pixel(bg),b=Pixel(fg);UINTN k;
  for(k=0;k<256;k++){
    r[k].Red=(UINT8)((a.Red*(255-k)+b.Red*k+127)/255);
    r[k].Green=(UINT8)((a.Green*(255-k)+b.Green*k+127)/255);
    r[k].Blue=(UINT8)((a.Blue*(255-k)+b.Blue*k+127)/255);
    r[k].Reserved=0;
  }
}
STATIC VOID Run(UINTN x,UINTN y,CHAR16 *s,UINTN n,UINTN cw,UINT32 fg,UINT32 bg){
  UINTN i,px=n*cw;PX r[256];BOOLEAN blank=TRUE;if(!px||x>W||y>H||px>W-x||Ch>H-y)return;
  for(i=0;i<n;i++){if(s[i]!=L' '){blank=FALSE;break;}}
  if(blank){Fill(x,y,px,Ch,bg);return;} FontRamp(r,fg,bg);
  for(i=0;i<n;i++)Glyph(i*cw,cw,s[i],r);
  G->Blt(G,Strip,EfiBltBufferToVideo,0,0,x,y,px,Ch,W*sizeof(PX));
}
STATIC VOID RoundBox(UINTN x,UINTN y,UINTN w,UINTN h,UINTN r,UINT32 color){
  UINTN i,j; if(!r||r*2>h||r*2>w){Fill(x,y,w,h,color);return;}
  Fill(x,y+r,w,h-2*r,color);
  for(i=0;i<r;i++){j=0;while(j<r && (r-j)*(r-j)+(r-i)*(r-i)>r*r)j++;
    Fill(x+j,y+i,w-2*j,1,color);Fill(x+j,y+h-1-i,w-2*j,1,color);}
}
STATIC VOID Chrome(VOID){
  CHAR16 badge[]=L"UMAF / SLATE";UINTN i,j,h=Ch*2/3,w=h*BRAND_W/BRAND_H,bx=Left+(Cols-14)*Cw;PX r[16];
  Fill(0,0,W,H,0x0c1920);
  RoundBox(Left-Cw/2,Top-Ch/6,Cols*Cw+Cw,Rows*Ch+Ch/3,Cw/2,0x182b35);
  RoundBox(Left,Ch/2,Ch,Ch,Ch/4,0x91ead3);
  Fill(Left+Ch/4,Ch/2+Ch/4,Ch/2,Ch/9,0x164438);
  Fill(Left+Ch/4,Ch/2+Ch/2,Ch/3,Ch/9,0x164438);
  if(SlateZh()){Run(Left+Ch+Ch/3,Ch/2,L"韌體設定",4,2*Cw,0xf3f9ff,0x0c1920);}else{
  Ramp(r,0xf3f9ff,0x0c1920);
  for(j=0;j<h;j++)for(i=0;i<w;i++)Strip[j*W+i]=r[Brand[j*BRAND_H/h*BRAND_W+i*BRAND_W/w]];
  G->Blt(G,Strip,EfiBltBufferToVideo,0,0,Left+Ch+Ch/3,Ch/2+(Ch-h)/2,w,h,W*sizeof(PX));
  }
  Run(bx-12*Cw,Ch/2,L"F2: EN/TW",9,Cw,0x9cc3ce,0x0c1920);
  RoundBox(bx,Ch/2,14*Cw,Ch,Ch/2,0x203c3d);Run(bx+Cw,Ch/2,badge,12,Cw,0x9ae9d8,0x203c3d);
  Fill(Left,Ch*7/4,Cols*Cw,2,0x334851);
}
STATIC PX Under[128];STATIC UINTN Ux,Uy;STATIC BOOLEAN Marked;
STATIC VOID HideCaret(VOID){
  if(Marked && G){G->Blt(G,Under,EfiBltBufferToVideo,0,0,Ux,Uy,Cw,2,Cw*sizeof(PX));}Marked=FALSE;
}
STATIC VOID ShowCaret(VOID){
  if(!Active||!Mode.CursorVisible||!G||2*Cw>128)return;
  Ux=Left+Cw*(UINTN)Mode.CursorColumn;Uy=Top+Ch*((UINTN)Mode.CursorRow+1)-3;
  if(!EFI_ERROR(G->Blt(G,Under,EfiBltVideoToBltBuffer,Ux,Uy,0,0,Cw,2,Cw*sizeof(PX)))){
    Marked=TRUE;Fill(Ux,Uy,Cw,2,0x91ead3);
  }
}
STATIC EFI_STATUS EFIAPI Clear(SLATE_OUT *t){HideCaret();Chrome();Mode.CursorColumn=0;Mode.CursorRow=0;ShowCaret();return EFI_SUCCESS;}
STATIC EFI_STATUS EFIAPI Reset(SLATE_OUT *t,BOOLEAN extended){return Clear(t);}
STATIC EFI_STATUS EFIAPI Test(SLATE_OUT *t,CHAR16 *s){return s?EFI_SUCCESS:EFI_INVALID_PARAMETER;}
STATIC EFI_STATUS EFIAPI Query(SLATE_OUT *t,UINTN m,UINTN *c,UINTN *r){if(m || !c || !r)return EFI_UNSUPPORTED;*c=Cols;*r=Rows;return EFI_SUCCESS;}
STATIC EFI_STATUS EFIAPI Set(SLATE_OUT *t,UINTN m){return m?EFI_UNSUPPORTED:Clear(t);}
STATIC EFI_STATUS EFIAPI Attr(SLATE_OUT *t,UINTN a){if(a>255)return EFI_UNSUPPORTED;Mode.Attribute=(INT32)a;return EFI_SUCCESS;}
STATIC EFI_STATUS EFIAPI Move(SLATE_OUT *t,UINTN x,UINTN y){if(x>=Cols||y>=Rows)return EFI_UNSUPPORTED;HideCaret();Mode.CursorColumn=(INT32)x;Mode.CursorRow=(INT32)y;ShowCaret();return EFI_SUCCESS;}
STATIC EFI_STATUS EFIAPI Cursor(SLATE_OUT *t,BOOLEAN b){HideCaret();Mode.CursorVisible=b;ShowCaret();return EFI_SUCCESS;}
STATIC VOID Eol(VOID){Mode.CursorColumn=0;if((UINTN)Mode.CursorRow+1<Rows)Mode.CursorRow++;}
STATIC EFI_STATUS EFIAPI Output(SLATE_OUT *t,CHAR16 *s){
  UINTN n,step,col,row,avail,bg,fg;BOOLEAN wide;if(!s)return EFI_INVALID_PARAMETER;HideCaret();wide=(Mode.Attribute&0x80)!=0;
  while(*s){
    if(*s==L'\r'){Mode.CursorColumn=0;++s;continue;}
    if(*s==L'\n'){if((UINTN)Mode.CursorRow+1<Rows)Mode.CursorRow++;++s;continue;}
    if(*s==L'\b'){if(Mode.CursorColumn>0)Mode.CursorColumn--;++s;continue;}
    if(*s==0xfff0 || *s==0xfff1){wide=(*s++==0xfff1);continue;}
    step=wide?2:1;col=(UINTN)Mode.CursorColumn;row=(UINTN)Mode.CursorRow;avail=(Cols-col)/step;
    if(!avail){Eol();continue;}
    for(n=0;n<avail && s[n] && s[n]!=L'\r'&&s[n]!=L'\n'&&s[n]!=L'\b'&&s[n]!=0xfff0&&s[n]!=0xfff1;n++){}
    bg=((UINTN)Mode.Attribute>>4)&7;fg=(UINTN)Mode.Attribute&15;
    Run(Left+col*Cw,Top+row*Ch,s,n,Cw*step,bg==3?0x0c302b:Ink[fg],Paper[bg]);
    Mode.CursorColumn+=(INT32)(n*step);s+=n;if((UINTN)Mode.CursorColumn>=Cols)Eol();
  }ShowCaret();return EFI_SUCCESS;
}
STATIC SLATE_OUT Terminal={Reset,Output,Test,Query,Set,Attr,Clear,Move,Cursor,&Mode};
SLATE_OUT *SlateOut(VOID){return Active?&Terminal:gST->ConOut;}
BOOLEAN SlateEnabled(VOID){return Active;}
VOID SlateDrop(VOID){Marked=FALSE;Active=FALSE;if(Strip){FreePool(Strip);Strip=NULL;}W=H=0;G=NULL;Font=NULL;}
VOID SlateBegin(BOOLEAN FullView){
  UINTN w,h,c,maxv;GOP *g=NULL;EFI_STATUS s;Marked=FALSE;Active=FALSE;if(!FullView)return;
  s=gBS->HandleProtocol(gST->ConsoleOutHandle,&gEfiGraphicsOutputProtocolGuid,(VOID**)&g);
  if(EFI_ERROR(s)||g==NULL){
    // If the platform does not attach GOP to ConOut, only accept an unambiguous single GOP.
    EFI_HANDLE *v=NULL;UINTN count=0;
    s=gBS->LocateHandleBuffer(ByProtocol,&gEfiGraphicsOutputProtocolGuid,NULL,&count,&v);
    if(!EFI_ERROR(s)&&count==1)s=gBS->HandleProtocol(v[0],&gEfiGraphicsOutputProtocolGuid,(VOID**)&g);else g=NULL;
    if(v)FreePool(v);
  }
  if(!g||!g->Mode||!g->Mode->Info)return;
  w=g->Mode->Info->HorizontalResolution;h=g->Mode->Info->VerticalResolution;
  if(w<800||h<560||w>8192||h>4320)return;
  c=w/94;maxv=h/52;if(c>maxv)c=maxv;if(c<8)c=8;if(c>46)c=46;
  if(w/c<84 || h/(2*c)<26)return;
  if(!Strip || G!=g || W!=w || H!=h){SlateDrop();G=g;W=w;H=h;Cw=c;Ch=2*c;
    Cols=w/c-4;Rows=h/Ch-3;Left=(w-Cols*Cw)/2;Top=2*Ch;
    if(Rows<23 || Cols<80){SlateDrop();return;}
    Strip=AllocateZeroPool(w*Ch*sizeof(PX));if(!Strip){SlateDrop();return;}
    gBS->LocateProtocol(&gEfiHiiFontProtocolGuid,NULL,(VOID**)&Font);
  }
  Active=TRUE;Mode.CursorColumn=Mode.CursorRow=0;Mode.CursorVisible=FALSE;Chrome();
}
