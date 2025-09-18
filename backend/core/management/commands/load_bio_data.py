import argparse
from typing import Dict, Tuple, List
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from core.models import ProteinSequence, GeneExpression


def parse_fasta(path: str) -> Dict[str, str]:
    seqs: Dict[str, List[str]] = {}
    name = None
    with open(path, 'r') as fh:
        for line in fh:
            line = line.rstrip('\n')
            if not line:
                continue
            if line.startswith('>'):
                header = line[1:].strip()
                name = header.split()[0]
                if name not in seqs:
                    seqs[name] = []
            else:
                if name is None:
                    continue
                seqs[name].append(line.strip())
    return {k: ''.join(v) for k, v in seqs.items()}


def parse_tsv(path: str) -> Dict[str, Tuple[int, int, int, int, int, int]]:
    result: Dict[str, Tuple[int, int, int, int, int, int]] = {}
    with open(path, 'r') as fh:
        first = fh.readline()
        if not first:
            return {}
        cols = first.rstrip('\n').split('\t')
        if len(cols) == 7 and not cols[0].isdigit():
            # Treat as header + 7 columns: gene + 6 values; keep header names unused
            for line in fh:
                parts = line.rstrip('\n').split('\t')
                if len(parts) != 7:
                    continue
                gene = parts[0].strip()
                vals = []
                for i in range(1, 7):
                    try:
                        vals.append(int(parts[i]))
                    except ValueError:

                        vals.append(0)
                result[gene] = tuple(vals)  
        else:
            # Assume 12 cols = 6 pairs: name,value,name,value,... (no header)
            # First line is data line already read
            lines = [cols] + [l.rstrip('\n').split('\t') for l in fh]
            for parts in lines:
                if len(parts) < 12:
                    continue
                gene = parts[0].strip()
                indices = [1, 3, 5, 7, 9, 11]
                vals = []
                for idx in indices:
                    try:
                        vals.append(int(parts[idx]))
                    except (ValueError, IndexError):
                        vals.append(0)
                result[gene] = tuple(vals) 
    return result


class Command(BaseCommand):
    help = 'Load protein sequences and gene expression data into the database.'

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('--fasta', required=True, help='Path to FASTA file')
        parser.add_argument('--tsv', required=True, help='Path to TSV file')

    def handle(self, *args, **options):
        fasta_path = options['fasta']
        tsv_path = options['tsv']
        self.stdout.write(self.style.NOTICE('Parsing FASTA...'))
        seqs = parse_fasta(fasta_path)
        self.stdout.write(self.style.SUCCESS(f'Parsed {len(seqs)} sequences'))

        self.stdout.write(self.style.NOTICE('Parsing TSV...'))
        exprs = parse_tsv(tsv_path)
        self.stdout.write(self.style.SUCCESS(f'Parsed {len(exprs)} expression rows'))

        created_seq = 0
        created_expr = 0
        updated_expr = 0
        with transaction.atomic():
            # Create ProteinSequence for all FASTA entries
            for gene, sequence in seqs.items():
                obj, created = ProteinSequence.objects.get_or_create(
                    gene_name=gene,
                    defaults={'sequence': sequence}
                )
                if not created and obj.sequence != sequence:
                    obj.sequence = sequence
                    obj.save(update_fields=['sequence'])
                if created:
                    created_seq += 1

            # Upsert GeneExpression for genes found in TSV that also exist as ProteinSequence
            proteins = {p.gene_name: p for p in ProteinSequence.objects.filter(gene_name__in=exprs.keys())}
            for gene, vals in exprs.items():
                p = proteins.get(gene)
                if not p:
                    # If expression exists without FASTA, skip creating ProteinSequence
                    continue
                obj, created = GeneExpression.objects.get_or_create(
                    protein=p,
                    defaults={
                        'sample1': vals[0], 'sample2': vals[1], 'sample3': vals[2],
                        'sample4': vals[3], 'sample5': vals[4], 'sample6': vals[5],
                    }
                )
                if created:
                    created_expr += 1
                else:
                    # Update if values changed
                    current = obj.as_list()
                    if current != list(vals):
                        obj.sample1, obj.sample2, obj.sample3, obj.sample4, obj.sample5, obj.sample6 = vals
                        obj.save()
                        updated_expr += 1

        self.stdout.write(self.style.SUCCESS(
            f'Created sequences: {created_seq}; Created expressions: {created_expr}; Updated expressions: {updated_expr}'
        ))

