from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ProteinSequence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gene_name', models.CharField(db_index=True, max_length=255, unique=True)),
                ('sequence', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='GeneExpression',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sample1', models.IntegerField(default=0)),
                ('sample2', models.IntegerField(default=0)),
                ('sample3', models.IntegerField(default=0)),
                ('sample4', models.IntegerField(default=0)),
                ('sample5', models.IntegerField(default=0)),
                ('sample6', models.IntegerField(default=0)),
                ('protein', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='expression', to='core.proteinsequence')),
            ],
        ),
    ]

