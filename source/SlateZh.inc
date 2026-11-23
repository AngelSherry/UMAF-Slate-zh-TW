/* Generated subset and display-only translation table. No firmware variables. */
#include "SlateZhGlyphs.h"
#include "SlateZhTable.h"
STATIC BOOLEAN EnglishView;
BOOLEAN SlateZh(VOID){return Active && !EnglishView;}
VOID SlateSwitchView(VOID){EnglishView=!EnglishView;}
STATIC CONST CHAR16 *LookupZh(CONST CHAR16 *s){
  UINTN a=0,b=sizeof(ZhTable)/sizeof(ZhTable[0]);INTN k;
  while(a<b){UINTN m=a+(b-a)/2;k=StrCmp(s,ZhTable[m].En);if(k==0)return ZhTable[m].Tw;if(k<0)b=m;else a=m+1;}
  return NULL;
}
CHAR16 *SlateText(CHAR16 *owned){
  CONST CHAR16 *z;CHAR16 *copy;
  if(!owned || !SlateZh() || !(z=LookupZh(owned)))return owned;
  copy=AllocateCopyPool(StrSize(z),z);
  if(!copy)return owned;
  FreePool(owned);return copy;
}
STATIC CONST UINT8 *ZhMask(CHAR16 c){
  STATIC CHAR16 last;STATIC UINT8 mask[54*54];UINTN a=0,b=sizeof(ZhCodes)/sizeof(ZhCodes[0]),i,j,n,p;UINT8 tag;
  if(c<128)return NULL;
  if(last==c)return mask;
  while(a<b){UINTN m=a+(b-a)/2;if(ZhCodes[m]<c)a=m+1;else b=m;}
  if(a==sizeof(ZhCodes)/sizeof(ZhCodes[0]) || ZhCodes[a]!=c)return NULL;
  p=ZhOff[a];i=0;
  while(i<sizeof(mask)){tag=ZhRle[p++];if(tag>=128){n=tag-127;for(j=0;j<n;j++)mask[i++]=ZhRle[p];p++;}
    else{n=tag+1;CopyMem(mask+i,ZhRle+p,n);p+=n;i+=n;}}
  last=c;return mask;
}
