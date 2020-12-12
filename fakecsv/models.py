from django.db import models
from django.conf import settings
from django.core.validators import slug_unicode_re, RegexValidator


class Schema(models.Model):

    class ColumnSeparator(models.TextChoices):
        COMMA = ',', 'Comma (,)'
        SEMICOLON = ';', 'Semicolon (;)'
        TAB = '\t', 'Tab (\t)'
        SPACE = ' ', 'Space ( )'
        PIPE = '|', 'Pipe (|)'

    class StringCharacter(models.TextChoices):
        DOUBLE_QUOTE = '"', 'Double Quote (")'
        SINGLE_QUOTE = "'", "Single Quote (')"

    name = models.CharField(max_length=128)
    column_separator = models.CharField(max_length=1,
                                        choices=ColumnSeparator.choices)
    string_character = models.CharField(max_length=1,
                                        choices=StringCharacter.choices)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Column(models.Model):

    DataType = models.IntegerChoices(
        'DataType',
        [
            'FULL_NAME', 'JOB', 'EMAIL', 'COMPANY',
            'PHONE_NUMBER', 'INTEGER', 'DATE']
    )
    DATA_TYPES_WITH_RANGE = [DataType.INTEGER]

    name = models.CharField(
        max_length=128,
        validators=[RegexValidator(
            regex=slug_unicode_re,
            message='Only letters, numbers, _ and - are allowed'
        )]
    )
    data_type = models.IntegerField(choices=DataType.choices)
    order = models.PositiveBigIntegerField()
    schema = models.ForeignKey(Schema, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('schema', 'order')

    def __str__(self):
        return self.name


class Range(models.Model):
    start = models.BigIntegerField()
    end = models.BigIntegerField()
    column = models.OneToOneField(Column, on_delete=models.CASCADE)

    def __str__(self):
        return 'between {} and {}'.format(self.start, self.end)


class Dataset(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    is_ready = models.BooleanField(default=False)
    file = models.FileField(upload_to='fakecsv/%Y-%m-%d')
    schema = models.ForeignKey(Schema, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.created_at)
