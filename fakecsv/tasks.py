from celery import shared_task
from fakecsv.generate import CSVGenerator
from fakecsv.models import Dataset, Column


@shared_task
def generate_csv(dataset_id, n_rows):
    dataset = Dataset.objects.select_related('schema') \
                             .get(id=dataset_id)
    columns = Column.objects.select_related('schema') \
                            .filter(schema=dataset.schema)

    csv_generator = CSVGenerator(dataset, columns, n_rows)
    csv_generator.generate()

    dataset.is_ready = True
    dataset.save()
