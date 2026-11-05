import importlib.util,pathlib,tempfile,unittest
spec=importlib.util.spec_from_file_location('up',pathlib.Path(__file__).with_name('update_data.py'))
up=importlib.util.module_from_spec(spec);spec.loader.exec_module(up)
class Tests(unittest.TestCase):
    def test_source_failure_preserves_data_and_products(self):
        with tempfile.TemporaryDirectory() as d:
            prev=up.DATA;up.DATA=pathlib.Path(d)
            try:
                up.save('trials',[{'id':'old'}]);up.save('products',[{'name':'immutable'}]);up.save('news',[]);up.save('monitors',[])
                a,b=up.trials_fetch,up.pubmed_fetch
                def fail():raise RuntimeError('fixture unavailable')
                up.trials_fetch=fail;up.pubmed_fetch=fail
                try:self.assertTrue(up.run())
                finally:up.trials_fetch=a;up.pubmed_fetch=b
                self.assertEqual(up.load('trials',[]),[{'id':'old'}])
                self.assertEqual(up.load('products',[]),[{'name':'immutable'}])
                self.assertIsNone(up.load('health',{}).get('lastSuccess'))
            finally:up.DATA=prev
    def test_html_ignores_scripts(self):
        self.assertEqual(up.TextExtractor.clean(b'<main><script>noise</script><h1>Label</h1></main>'),'Label')
    def test_normalize(self):
        r=up.normalize({'protocolSection':{'identificationModule':{'nctId':'NCT12345678'},'statusModule':{'overallStatus':'COMPLETED'},'designModule':{'phases':['PHASE2']}}})
        self.assertEqual(r['status'],'COMPLETED')
if __name__=='__main__':unittest.main()
