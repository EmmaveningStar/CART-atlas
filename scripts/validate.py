import json,pathlib
D=pathlib.Path(__file__).resolve().parents[1]/'dist/data'
def check():
    for n in ['products','trials','news','health','monitors']:
        x=json.loads((D/(n+'.json')).read_text())
        assert isinstance(x,dict if n=='health' else list),n
    for n,key in [('products','name'),('trials','id'),('news','id')]:
        rows=json.loads((D/(n+'.json')).read_text())
        assert len(rows)==len({r[key] for r in rows}),n
    for p in json.loads((D/'products.json').read_text()):
        assert p['verifiedAt'] and p['detail'] and set(p['regions'])=={'US','EU','JP','TW','CN','UK'}
        for v in p['regions'].values():
            assert v['status'] in ['已核准','附條件核准','待查證']
            assert v['source'].startswith('https://')
    print('Data validation passed')
if __name__=='__main__':check()
