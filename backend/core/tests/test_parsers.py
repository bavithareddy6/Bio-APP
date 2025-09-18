import os
import tempfile
from django.test import SimpleTestCase
from core.management.commands.load_bio_data import parse_fasta, parse_tsv


class ParserTests(SimpleTestCase):
    def test_parse_fasta_multiline(self):
        content = ">GeneA desc\nAA\nBB\n>GeneB\nCCC\n"
        with tempfile.NamedTemporaryFile('w+', delete=False) as f:
            f.write(content)
            path = f.name
        try:
            res = parse_fasta(path)
            self.assertEqual(res['GeneA'], 'AABB')
            self.assertEqual(res['GeneB'], 'CCC')
        finally:
            os.remove(path)

    def test_parse_tsv_12_cols_pairs(self):
        # name,val x6, first line is data (no header)
        content = "GeneA\t1\tGeneA\t2\tGeneA\t3\tGeneA\t4\tGeneA\t0\tGeneA\t6\n"
        with tempfile.NamedTemporaryFile('w+', delete=False) as f:
            f.write(content)
            path = f.name
        try:
            res = parse_tsv(path)
            self.assertIn('GeneA', res)
            self.assertEqual(res['GeneA'], (1, 2, 3, 4, 0, 6))
        finally:
            os.remove(path)

    def test_parse_tsv_7_cols_header(self):
        # header + 7 columns: gene + six values
        content = "Gene\tS1\tS2\tS3\tS4\tS5\tS6\nGeneA\t1\t2\t3\t4\t0\t6\n"
        with tempfile.NamedTemporaryFile('w+', delete=False) as f:
            f.write(content)
            path = f.name
        try:
            res = parse_tsv(path)
            self.assertEqual(res['GeneA'], (1, 2, 3, 4, 0, 6))
        finally:
            os.remove(path)

