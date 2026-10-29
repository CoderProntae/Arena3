REAKTOR / TEK PAKET — YEDI ONAYLI 3B MODEL + YENI KOPRU
========================================================
Bu GLB dosyalari kullanicinin onayladigi modellerin Studio icin Y-yukari
koordinatina DONUSTURULMUS kopyalaridir; sekilleri/olcekleri degistirilmedi.

1. Eski ntfy.sh koprusunu terminalde Ctrl+C ile durdur. Bu ZIP'i YENI bir
   klasore ac. Roblox Studio'yu ilgili yer ile Edit modunda ac ve yedek al.
2. O klasorde PowerShell: python .\Roblox_Studio_MCP_Kalici_Kopru.py
   cryptography eksikse bir kez: python -m pip install cryptography
   Bu terminali acik birak. Bu sohbetten "Kopru ONLINE" haberini ver.
3. Studio File > Import (veya Ctrl+M): models klasorundeki YEDI .glb'yi
   tek seferde sec. Importer'da hepsinin Scale Unit = Studs oldugunu
   kontrol et, Import Only As Model secili kalsin, sonra Import de.
   Roblox'a yukleme secenegi paylasim/kalicilik kararin; bundan haber ver.
   Studio'da gorunene kadar aktarildi veya dogru gorunuyor varsaymiyoruz.
4. Dosyalar Workspace'e gelince bana haber ver. Sunucu tarafli hatch/piston/
   yekpare yayici animasyonlarini, koordinat/olcek hizalamasini ve durum VFX'ini
   Studio'da bizzat inceleyip kuracagim; fiziki tiklama testi yapmayacagim.

Windows istemcisi sadece Studio'nun resmi yerel mcp.bat surecini baslatir,
disariya yalniz giden HTTPS baglantisi acar; yazma/Play/Luau icin konsolda
HER ISLEMDE ayri YES gerekir. Yeni saglayici ntfy.envs.net ucretsiz bir
ucuncu taraf posta kutusudur: kota/erisim garantisi yoktur; AES/Fernet ile
icerik uctan uca sifrelenir fakat iletisim zamani/boyutu gorulebilir.
Roblox hesap sifresi veya API anahtari istemez. Gizli JSON'u paylasma.
Kaynak modeller model_exports/ altinda DEGISMEDEN kaldi.
