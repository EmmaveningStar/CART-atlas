"""Import public research data; never infer approval status."""
import datetime as dt, hashlib, json, pathlib, re, sys, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET
DATA=pathlib.Path(__file__).resolve().parents[1]/'dist/data'
def load(name,default):
    try:return json.loads((DATA/(name+'.json')).read_text())
    except FileNotFoundError:return default
def save(name,value):
    path=DATA/(name+'.json');tmp=path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');tmp.replace(path)
def get(url):
    for attempt in range(3):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'CARTAtlas/1.0 (public research index)'})
            with urllib.request.urlopen(req,timeout=30) as r:return r.read()
        except Exception:
            if attempt==2:raise
            time.sleep(2**attempt)
def normalize(study):
    p=study['protocolSection'];i=p['identificationModule'];s=p['statusModule']
    return dict(id=i['nctId'],title=i.get('briefTitle',''),interventions=[x['name'] for x in p.get('armsInterventionsModule',{}).get('interventions',[])],conditions=p.get('conditionsModule',{}).get('conditions',[]),phase=' / '.join(p.get('designModule',{}).get('phases',[])) or '未提供',status=s.get('overallStatus','UNKNOWN'),updated=s.get('lastUpdatePostDateStruct',{}).get('date',''),source='https://clinicaltrials.gov/study/'+i['nctId'],note='試驗登錄自動匯入；研究用途不代表已獲核准。')
def trials_fetch():
    items=[];token=None
    for page in range(100):
        params={'query.term':'("CAR-T" OR "CAR T" OR "chimeric antigen receptor T")','format':'json','pageSize':100,'sort':'LastUpdatePostDate:desc'}
        if token:params['pageToken']=token
        raw=json.loads(get('https://clinicaltrials.gov/api/v2/studies?'+urllib.parse.urlencode(params)))
        items.extend(normalize(x) for x in raw.get('studies',[]));token=raw.get('nextPageToken')
        if not token:break
    if token:raise RuntimeError('Pagination cap reached; preserving prior data')
    if not items:raise RuntimeError('Empty study response; preserving prior data')
    return items
def pubmed_fetch():
    base='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    q='("chimeric antigen receptor T"[Title/Abstract] OR "CAR-T"[Title/Abstract]) AND ("last 30 days"[EDAT])'
    r=json.loads(get(base+'esearch.fcgi?'+urllib.parse.urlencode(dict(db='pubmed',term=q,retmode='json',retmax=100,sort='pub date'))))
    ids=r['esearchresult']['idlist']
    if not ids:return []
    time.sleep(.4)
    root=ET.fromstring(get(base+'efetch.fcgi?'+urllib.parse.urlencode(dict(db='pubmed',id=','.join(ids),retmode='xml'))));out=[]
    for art in root.findall('.//PubmedArticle'):
        pmid=art.findtext('.//MedlineCitation/PMID');node=art.find('.//ArticleTitle')
        if not pmid or node is None:continue
        title=''.join(node.itertext())
        d=next((x for x in art.findall('.//PubMedPubDate') if x.attrib.get('PubStatus')=='pubmed'),None)
        date=f"{int(d.findtext('Year')):04}-{int(d.findtext('Month')):02}-{int(d.findtext('Day')):02}" if d is not None else dt.date.today().isoformat()
        out.append(dict(id='pmid-'+pmid,title=title,date=date,type='研究文獻',source='PubMed',url='https://pubmed.ncbi.nlm.nih.gov/'+pmid+'/',summary='近期收錄文獻；日期為 PubMed 收錄日期，原始發表日期請見來源。未自動判定臨床效益。',review='自動匯入・未審閱'))
    return out
class TextExtractor:
    @staticmethod
    def clean(raw):
        text=raw.decode('utf-8',errors='replace')
        main=re.search(r'<main\b[^>]*>(.*?)</main>',text,re.S|re.I)
        if main:text=main.group(1)
        text=re.sub(r'<(script|style)\b[^>]*>.*?</\1>','',text,flags=re.S|re.I)
        return re.sub(r'\s+',' ',re.sub('<[^>]+>',' ',text)).strip()
def run():
    now=dt.datetime.now(dt.timezone.utc).isoformat();today=now[:10]
    health=load('health',{});health['lastAttempt']=now;health['mode']='GitHub Actions 每日更新';health['sources']={}
    news={x['id']:x for x in load('news',[])};fail=[]
    news={k:v for k,v in news.items() if v.get('type')!='試驗更新'}
    health['sources']['研究摘要']={'status':'編輯整理・不自動匯入試驗清單'}
    try:
        items=pubmed_fetch();news.update({x['id']:x for x in items})
        health['sources']['PubMed']={'status':'成功','count':len(items),'checkedAt':now}
    except Exception as e:
        fail.append('PubMed');health['sources']['PubMed']={'status':'失敗・保留舊資料','error':str(e)}
    hashes=load('source-hashes',{});monitors=load('monitors',[]);errors=[]
    for monitor in monitors:
        url=monitor['url']
        try:
            text=TextExtractor.clean(get(url))
            if len(text)<100:raise RuntimeError('Unexpectedly short source page')
            digest=hashlib.sha256(text.encode()).hexdigest();prev=hashes.get(url)
            if prev and prev!=digest:
                key='source-'+hashlib.sha256((url+digest).encode()).hexdigest()[:24]
                news[key]=dict(id=key,title=monitor['name']+'：來源頁面有異動',date=today,type='來源異動',source=monitor['agency'],url=url,summary='頁面文字變更可能來自版面或非核准內容。待人工核對，不自動變更核准狀態。',review='待人工核對')
            hashes[url]=digest
        except Exception as e:errors.append({'name':monitor['name'],'error':str(e)})
    health['sources']['主管機關監測']={'status':'成功' if not errors else f'{len(errors)} 頁失敗・保留舊雜湊','count':len(monitors),'checkedAt':now,'errors':errors}
    if errors:fail.append('regulators')
    if not fail:health['lastSuccess']=now
    save('news',sorted(news.values(),key=lambda x:x['date'],reverse=True)[:600]);save('source-hashes',hashes);save('health',health)
    print(json.dumps({'failures':fail,'newsCount':len(news),'lastAttempt':now}))
    return bool(fail)
if __name__=='__main__':sys.exit(run())
