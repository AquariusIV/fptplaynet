__author__ = 'traitravinh'
import urllib, urllib2, re, os, sys, StringIO
import xbmc
import xbmcaddon,xbmcplugin,xbmcgui
from bs4 import BeautifulSoup
import SimpleDownloader as downloader


downloader = downloader.SimpleDownloader()
mysettings = xbmcaddon.Addon(id='plugin.video.nhaccuatui')
home = mysettings.getAddonInfo('path')
searchHistory = xbmc.translatePath(os.path.join(home,'history.txt'))
downloadpath = mysettings.getSetting('download_path')
searchlink ='http://www.nhaccuatui.com/tim-kiem?q='
home_link = 'http://www.nhaccuatui.com/'
logo='http://stc.nct.nixcdn.com/static_v8/images/share/logo-nct.jpg'
pl=xbmc.PlayList(xbmc.PLAYLIST_MUSIC)

def Home():
    addDir('Search',searchlink,1,logo,'')
    addDir('Downloaded Audio',downloadpath,8,logo,'')
    addDir('Downloaded Video',downloadpath,8,logo,'')

def SearchFirst(url):
    try:
        hist = open(searchHistory)
        addDir('Search',searchlink,2,logo,'')
        for text in hist:
            addDir(text,searchlink+text.replace(' ','+'),2,logo,'')
    except:pass

def Search(url):
    try:
        if url.find('+')!=-1:
            url = url.rstrip()
        else:
            keyb = xbmc.Keyboard('', 'Enter search text')
            keyb.doModal()
            if (keyb.isConfirmed()):
                    searchText = urllib.quote_plus(keyb.getText())
            url = "http://www.nhaccuatui.com/tim-kiem?q="+ searchText.replace(' ','+').rstrip()
            if searchText!='':
                with open(searchHistory,'a') as file:
                    file.write('\n'+searchText.replace('+',' '))

        index_search(url)
    except: pass



def index_search(url):
    try:
        link = urllib2.urlopen(url).read()
        soup = BeautifulSoup(link.decode('utf-8'))
        search_control_select = soup('ul',{'class':'search_control_select'})
        li_soup = BeautifulSoup(str(search_control_select[0]))('a')
        for i in range(1,4):
            a_soup = BeautifulSoup(str(li_soup[i]))
            alink = a_soup('a')[0]['href']
            atitle = a_soup('a')[0]['title'].encode('utf-8')
            acount=a_soup('span')[0].contents[0]
            title = atitle + str(acount)
            addDir(title,alink,4,logo,atitle)
    except:pass

def search_return(url,cname):
    try:
        image = logo
        key = ''
        subkey =''
        if cname.find('B')!=-1:
            key='list_song'
            subkey = 'name_song'
        elif cname.find('P')!=-1:
            key = 'list_album'
            subkey = 'box_absolute'
        elif cname.find('V')!=-1:
            key = 'list_video'
            subkey = 'img'

        link = urllib2.urlopen(url).read()
        soup = BeautifulSoup(link.decode('utf-8'))
        lists = soup('li',{'class':key})
        for l in lists:
            asoup = BeautifulSoup(str(l))
            alink = asoup('a',{'class':subkey})[0]['href']
            try:
                aimage = asoup('img')[0]['src']
                image = aimage
            except:pass
            atitle = asoup('a',{'class':subkey})[0]['title'].encode('utf-8')

            addDir(atitle,alink,5,image,cname)

        box_pageview = soup('div',{'class':'box_pageview'})
        pages = BeautifulSoup(str(box_pageview[0])).findAll('a')
        for p in pages:
            psoup = BeautifulSoup(str(p))
            plink = psoup('a')[0]['href']
            ptitle = psoup('a')[0].contents[0]

            addDir(ptitle.encode('utf-8'),plink,4,logo,cname)
    except:pass

def explore(url):
    try:
        xml_link = getXML(url)
        filelinks =[]
        filetitles =[]
        filelinks= getMediaLink(xml_link)
        filetitles = getMediaTitle(xml_link)
        filelinkslenght = len(filelinks)

        for i in range(0,filelinkslenght):
            addLink(filetitles[i],filelinks[i],6,iconimage,cname)
            i+=1
    except:pass

def getXML(url):
    try:
        link = urllib2.urlopen(url).read()
        soup = BeautifulSoup(link.decode('utf-8'))
        flash_playing = soup('div',{'class':'box_playing'})
        file = re.compile('file=(.+?)" /').findall(str(flash_playing[0]))[0]
        return file
    except:pass

def getMediaLink(url):
    try:
        link = urllib2.urlopen(url).read()
        newlink = ''.join(link.splitlines()).replace('\t','').replace('\n','')
        match = re.compile('<location>(.+?)</location>').findall(newlink)
        finallink=[]
        for content in match:
            finallink.append(content.replace('<![CDATA[','').replace(']]>','').replace(' ',''))
        return finallink
    except:pass

def getMediaTitle(url):
    try:
        link = urllib2.urlopen(url).read()
        newlink = ''.join(link.splitlines()).replace('\t','').replace('\n','')
        match = re.compile('<title>(.+?)</title>').findall(newlink)
        finaltitle=[]
        for content in match:
            finaltitle.append(content.replace('<![CDATA[','').replace(']]>',''))

        return finaltitle
    except:pass

def Play(url):
    try:
        listitem = xbmcgui.ListItem(name,iconImage='DefaultVideo.png',thumbnailImage=iconimage)
        listitem.setPath(url)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
    except:pass

def download(url):
    try:
        filename = re.compile('[a-zA-Z0-9-_]+\.\w+$').findall(url)[0]
        type = re.compile('\.\w+$').findall(url)[0]
        title_num = re.compile('(?:-|_|\+)\w*\.\w+$').findall(filename)[0]
        title = str(filename).replace(title_num,'')
        filename = title+type
        params = {"url": url, "download_path": downloadpath, "Title": title}

        if os.path.isfile(downloadpath+filename):
            dialog = xbmcgui.Dialog()
            if dialog.yesno('Download message','File exists! re-download?'):
                downloader.download(filename, params)
        else:
            downloader.download(filename, params)
    except:pass

def delete(url):
    try:
        dialog = xbmcgui.Dialog()
        if dialog.yesno('Delete','Delete File?'):
            os.remove(url)
    except:pass

def list_downloaded(url):
    try:
        if str(name).find('Audio')!=-1:
            filetype = '.mp3'
        elif str(name).find('Video')!=-1:
            filetype = '.mp4'
        loadfiles = [a for a in os.listdir(url) if a.endswith(filetype)]
        for a in loadfiles:
            addLink(a,url+a,6,logo,'')
    except:pass

def addDir(name,url,mode,iconimage,cname):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&cname="+urllib.quote_plus(cname)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage=logo, thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

def addLink(name,url,mode,iconimage,cname):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&cname="+urllib.quote_plus(cname)
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name})
        liz.setProperty('mimetype', 'video/x-msvideo')
        contextmenuitems = []
        if url.find('http://')!=-1:
            contextmenuitems.append(('Download','XBMC.Container.Update(%s?url=%s&mode=7)'%('plugin://plugin.video.nhaccuatui',urllib.quote_plus(url))))
            liz.addContextMenuItems(contextmenuitems,replaceItems=False)
        else:
            contextmenuitems.append(('Delete','XBMC.Container.Update(%s?url=%s&mode=9)'%('plugin://plugin.video.nhaccuatui',urllib.quote_plus(url))))
            liz.addContextMenuItems(contextmenuitems,replaceItems=False)
        pl.add(u,liz)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz, isFolder=False)
        return ok

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]

        return param

params=get_params()
url=None
name=None
mode=None
iconimage=None
cname=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        iconimage=urllib.unquote_plus(params["iconimage"])
except:
        pass
try:
        cname=urllib.unquote_plus(params["cname"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

sysarg=str(sys.argv[1])
if mode==None or url==None or len(url)<1:
    Home()
elif mode==1:
    SearchFirst(url)
elif mode==2:
    Search(url)
elif mode==3:
    index_search(url)
elif mode==4:
    search_return(url,cname)
elif mode==5:
    explore(url)
elif mode==6:
    Play(url)
elif mode==7:
    download(url)
elif mode==8:
    list_downloaded(url)
elif mode==9:
    delete(url)
xbmcplugin.endOfDirectory(int(sysarg))
