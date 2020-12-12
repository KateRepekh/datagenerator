from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from uuid import uuid4

from fakecsv.models import Schema, Dataset
from fakecsv.forms import SchemaForm, ColumnFormSet
from fakecsv.ownerviews import (
    OwnerListView, OwnerDetailView,
    OwnerCreateView, OwnerDeleteView)
from fakecsv.tasks import generate_csv


class SchemaListView(OwnerListView):
    model = Schema


class SchemaDetailView(OwnerDetailView):
    model = Schema

    def post(self, request, pk=None):
        n_rows = int(request.POST['n_rows'])
        schema = get_object_or_404(Schema, pk=pk, owner=self.request.user)
        dataset = Dataset(schema=schema)
        dataset.file.save('{}.csv'.format(uuid4()), ContentFile(''))
        dataset.save()
        generate_csv.delay(dataset.id, n_rows)
        return redirect(reverse('fakecsv:schema_detail', args=[schema.id]))


class SchemaCreateView(OwnerCreateView):
    form_class = SchemaForm
    success_url = reverse_lazy('fakecsv:schemas')
    template_name = 'fakecsv/schema_form.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx['column_forms'] = ColumnFormSet(
                self.request.POST, self.request.FILES, prefix='column'
            )
        else:
            ctx['column_forms'] = ColumnFormSet(prefix='column')
        return ctx

    def form_valid(self, form):
        ctx = self.get_context_data()
        column_forms = ctx['column_forms']
        if column_forms.is_valid():
            response = super().form_valid(form=form)
            column_forms.instance = self.object
            column_forms.save()
            return response
        else:
            return self.form_invalid(form=form)


class SchemaDeleteView(OwnerDeleteView):
    model = Schema
    success_url = reverse_lazy('fakecsv:schemas')


class DatasetDownloadView(LoginRequiredMixin, View):

    def get(self, request, pk):
        dataset = get_object_or_404(Dataset, pk=pk,
                                    schema__owner=self.request.user)
        response = HttpResponse(dataset.file,
                                content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="{}"' \
                                          .format(dataset.file.name)
        return response
