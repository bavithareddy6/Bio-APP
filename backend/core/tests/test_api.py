from django.test import TestCase, Client
from core.models import ProteinSequence, GeneExpression


class ApiTests(TestCase):
    def setUp(self):
        # Create two genes with expressions
        p1 = ProteinSequence.objects.create(gene_name='GeneA', sequence='AAA')
        p2 = ProteinSequence.objects.create(gene_name='GeneB', sequence='BBBB')
        GeneExpression.objects.create(protein=p1, sample1=1, sample2=2, sample3=3, sample4=4, sample5=0, sample6=6)
        GeneExpression.objects.create(protein=p2, sample1=6, sample2=5, sample3=4, sample4=3, sample5=2, sample6=1)
        self.client = Client()

    def test_sequences_post(self):
        resp = self.client.post('/api/sequences', data={'genes': ['GeneA', 'GeneX']}, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['count'], 1)
        self.assertIn('GeneX', data['not_found'])
        self.assertEqual(data['sequences'][0]['gene'], 'GeneA')
        self.assertEqual(data['sequences'][0]['sequence'], 'AAA')

    def test_sequences_download_ext_and_wrap(self):
        resp = self.client.get('/api/sequences/download?genes=GeneB&ext=fa&wrap=2')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('attachment; filename="sequences.fa"', resp['Content-Disposition'])
        body = resp.content.decode()
        self.assertTrue(body.startswith('>GeneB'))
        # BBBB wrapped by 2 => 2 lines of 2 chars
        self.assertIn('\nBB\nBB\n', body)

    def test_expressions_post(self):
        resp = self.client.post('/api/expressions', data={'genes': ['GeneA', 'Missing']}, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['samples'], ['Sample1','Sample2','Sample3','Sample4','Sample5','Sample6'])
        self.assertIn('Missing', data['not_found'])
        rows = {r['gene']: r['values'] for r in data['rows']}
        self.assertEqual(rows['GeneA'], [1,2,3,4,0,6])

    def test_expressions_download_tsv(self):
        resp = self.client.get('/api/expressions/download?genes=GeneA,GeneB')
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode().strip().splitlines()
        self.assertEqual(body[0], 'Gene\tSample1\tSample2\tSample3\tSample4\tSample5\tSample6')
        self.assertTrue(any(line.startswith('GeneA\t1\t2\t3\t4\t0\t6') for line in body[1:]))

    def test_limit_max_10(self):
        many = [f'G{i}' for i in range(15)]
        # create first 10
        for g in many[:10]:
            ProteinSequence.objects.get_or_create(gene_name=g, defaults={'sequence': 'X'})
        resp = self.client.post('/api/sequences', data={'genes': many}, content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        # Only first 10 considered
        self.assertEqual(len(resp.json()['sequences']), 10)

