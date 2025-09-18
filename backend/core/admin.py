from django.contrib import admin
from .models import ProteinSequence, GeneExpression


@admin.register(ProteinSequence)
class ProteinSequenceAdmin(admin.ModelAdmin):
    search_fields = ('gene_name',)
    list_display = ('gene_name',)


@admin.register(GeneExpression)
class GeneExpressionAdmin(admin.ModelAdmin):
    list_display = ('protein', 'sample1', 'sample2', 'sample3', 'sample4', 'sample5', 'sample6')

