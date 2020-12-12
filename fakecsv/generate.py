import csv
from string import ascii_lowercase
from random import randint, choices
from datetime import date, timedelta
from functools import partial

from fakecsv.models import Column


class CSVGenerator:

    WORD_LENGTH_RANGE = (1, 20)
    WORD_SYMBOLS = ascii_lowercase
    MIN_DATE = date(1900, 1, 1)
    DAYS_BETWEEN_DATES_RANGE = (1, 80000)
    BATCH_SIZE = 10000
    QUOTING_POLICY = csv.QUOTE_NONNUMERIC
    PHONE_NUMBER_RANGE = (10**7, 10**15)

    def __init__(self, dataset, columns, n_rows):
        self.n_rows = n_rows
        self.dataset = dataset
        self.columns = columns
        self.map_data_type_to_function()

    def map_data_type_to_function(self):
        self.data_generators = {
            Column.DataType.FULL_NAME: self.generate_full_name,
            Column.DataType.COMPANY: self.generate_word,
            Column.DataType.JOB: self.generate_word,
            Column.DataType.EMAIL: self.generate_email,
            Column.DataType.INTEGER: self.generate_number,
            Column.DataType.PHONE_NUMBER: self.generate_phone_number,
            Column.DataType.DATE: self.generate_date,
        }

    def generate_item(self, column):
        if column.data_type in Column.DATA_TYPES_WITH_RANGE:
            generate = partial(self.data_generators[column.data_type],
                               column.range.start, column.range.end)
        else:
            generate = self.data_generators[column.data_type]
        return generate()

    def generate(self):
        columns = sorted(self.columns, key=lambda column: column.order)

        with open(self.dataset.file.path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(
                csvfile, delimiter=self.dataset.schema.column_separator,
                quotechar=self.dataset.schema.string_character,
                quoting=self.QUOTING_POLICY
            )
            csv_writer.writerow((column.name for column in columns))

            rows_to_generate = self.n_rows
            while rows_to_generate > 0:
                batch_size = min(self.BATCH_SIZE, rows_to_generate)
                rows_to_generate = rows_to_generate - batch_size

                chunk = ((self.generate_item(column)
                          for column in columns)
                         for row in range(batch_size))
                csv_writer.writerows(chunk)

    def generate_number(self, range_start, range_end):
        return randint(range_start, range_end)

    def generate_phone_number(self):
        return self.generate_number(*self.PHONE_NUMBER_RANGE)

    def generate_word(self):
        word_length = self.generate_number(*self.WORD_LENGTH_RANGE)
        return ''.join(choices(self.WORD_SYMBOLS, k=word_length))

    def generate_words(self, k):
        return (self.generate_word() for i in range(k))

    def generate_full_name(self):
        return "{} {}".format(*self.generate_words(2)).title()

    def generate_email(self):
        return "{}@{}.{}".format(*self.generate_words(3))

    def generate_date(self):
        days_passed = self.generate_number(*self.DAYS_BETWEEN_DATES_RANGE)
        return self.MIN_DATE + timedelta(days=days_passed)
