from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('translation', '0004_sentence_alignments'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportedFile',
            fields=[
                ('path', models.CharField(help_text='e.g. content/JHN/JHN.1.1-18.json', max_length=255, primary_key=True, serialize=False)),
                ('digest', models.CharField(help_text='SHA-256 of the file as imported', max_length=64)),
                ('imported_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
