from django.db import models


class ProteinSequence(models.Model):
    gene_name = models.CharField(max_length=255, unique=True, db_index=True)
    sequence = models.TextField()

    def __str__(self):
        return self.gene_name


class GeneExpression(models.Model):
    protein = models.OneToOneField(ProteinSequence, on_delete=models.CASCADE, related_name='expression')
    sample1 = models.IntegerField(default=0)
    sample2 = models.IntegerField(default=0)
    sample3 = models.IntegerField(default=0)
    sample4 = models.IntegerField(default=0)
    sample5 = models.IntegerField(default=0)
    sample6 = models.IntegerField(default=0)

    def as_list(self):
        return [self.sample1, self.sample2, self.sample3, self.sample4, self.sample5, self.sample6]

