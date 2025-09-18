import json
from typing import List
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Prefetch
from .models import ProteinSequence, GeneExpression


def health(request):
    return JsonResponse({"status": "ok"})


def _normalize_genes(genes: List[str]) -> List[str]:
    out = []
    for g in genes:
        if not g:
            continue
        out.append(g.strip())
    # limit to 10 per requirements
    return out[:10]


@csrf_exempt
def sequences_view(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Use POST with JSON {"genes": [...]}')
    try:
        payload = json.loads(request.body.decode('utf-8'))
        genes = _normalize_genes(payload.get('genes', []))
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')
    if not genes:
        return HttpResponseBadRequest('No genes provided')

    qs = ProteinSequence.objects.filter(gene_name__in=genes)
    found = {p.gene_name: p.sequence for p in qs}
    not_found = [g for g in genes if g not in found]
    return JsonResponse({
        'count': len(found),
        'not_found': not_found,
        'sequences': [{'gene': g, 'sequence': found[g]} for g in genes if g in found]
    })


def sequences_download_view(request):
    genes_param = request.GET.get('genes', '')
    genes = _normalize_genes([g for g in genes_param.split(',') if g])
    if not genes:
        return HttpResponseBadRequest('Provide genes as comma-separated query param')
    # Allow choosing output extension: fa or fasta (default: fasta)
    ext = request.GET.get('ext', 'fasta').lower()
    if ext not in ('fa', 'fasta'):
        ext = 'fasta'
   
    try:
        wrap = int(request.GET.get('wrap', '0'))
        if wrap < 0:
            wrap = 0
    except ValueError:
        wrap = 0
    qs = ProteinSequence.objects.filter(gene_name__in=genes)
    fasta_lines = []
    for p in qs.order_by('gene_name'):
        fasta_lines.append(f'>{p.gene_name}')
        
        seq = p.sequence.replace('\r', '')
        # write as single line
        seq_single = seq.replace('\n', '')
        if wrap and wrap > 0:
            for i in range(0, len(seq_single), wrap):
                fasta_lines.append(seq_single[i:i+wrap])
        else:
            fasta_lines.append(seq_single)
    content = '\n'.join(fasta_lines) + '\n'
    resp = HttpResponse(content, content_type='text/plain')
    resp['Content-Disposition'] = f'attachment; filename="sequences.{ext}"'
    return resp


@csrf_exempt
def expressions_view(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Use POST with JSON {"genes": [...]}')
    try:
        payload = json.loads(request.body.decode('utf-8'))
        genes = _normalize_genes(payload.get('genes', []))
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')
    if not genes:
        return HttpResponseBadRequest('No genes provided')

    proteins = ProteinSequence.objects.filter(gene_name__in=genes).prefetch_related(
        Prefetch('expression', queryset=GeneExpression.objects.all())
    )
    rows = []
    found_genes = []
    for p in proteins:
        expr = getattr(p, 'expression', None)
        if not expr:
            continue
        rows.append({'gene': p.gene_name, 'values': expr.as_list()})
        found_genes.append(p.gene_name)
    not_found = [g for g in genes if g not in found_genes]
    return JsonResponse({
        'samples': ['Sample1','Sample2','Sample3','Sample4','Sample5','Sample6'],
        'rows': rows,
        'not_found': not_found
    })


def expressions_download_view(request):
    genes_param = request.GET.get('genes', '')
    genes = _normalize_genes([g for g in genes_param.split(',') if g])
    if not genes:
        return HttpResponseBadRequest('Provide genes as comma-separated query param')
    proteins = ProteinSequence.objects.filter(gene_name__in=genes).prefetch_related('expression')
    lines = ['Gene\tSample1\tSample2\tSample3\tSample4\tSample5\tSample6']
    for p in proteins:
        expr = getattr(p, 'expression', None)
        if not expr:
            continue
        vals = expr.as_list()
        lines.append(f"{p.gene_name}\t" + "\t".join(str(v) for v in vals))
    content = '\n'.join(lines) + '\n'
    resp = HttpResponse(content, content_type='text/tab-separated-values')
    resp['Content-Disposition'] = 'attachment; filename="expressions.tsv"'
    return resp
