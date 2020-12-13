from django import forms

from fakecsv.models import Schema, Column, Range


class BootstrapForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            if field.widget.attrs.get('class'):
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs['class'] = 'form-control'


class SchemaForm(BootstrapForm):

    class Meta:
        model = Schema
        fields = ['name', 'column_separator', 'string_character']


class ColumnForm(BootstrapForm):
    range_start = forms.IntegerField(required=False)
    range_end = forms.IntegerField(required=False)

    class Meta:
        model = Column
        fields = ['name', 'data_type', 'order']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['data_type'] in Column.DATA_TYPES_WITH_RANGE:
            if (cleaned_data['range_start'] is None or
                cleaned_data['range_end'] is None):
                raise forms.ValidationError(
                    'This data type is supposed to have a range'
                )
            elif cleaned_data['range_start'] > cleaned_data['range_end']:
                raise forms.ValidationError(
                    'Range end should be greater than or equal to range start'
                )
        return cleaned_data

    def save(self, commit=True):
        res = super().save(commit=commit)
        if (commit and
            self.cleaned_data['data_type'] in Column.DATA_TYPES_WITH_RANGE):
            range = Range(start=self.cleaned_data['range_start'],
                          end=self.cleaned_data['range_end'],
                          column=self.instance)
            range.save()
        return res


class BaseInlineColumnFormSet(forms.BaseInlineFormSet):
    def clean(self):
        order_numbers = []
        for form in self.forms:
            if any(self.errors):
                return
            
            if self.can_delete and self._should_delete_form(form):
                continue
            
            order = form.cleaned_data['order']
            if order in order_numbers:
                raise forms.ValidationError(
                    "You can't have duplicate values in Order"
                )
            order_numbers.append(order)


ColumnFormSet = forms.inlineformset_factory(
    Schema, Column, form=ColumnForm, formset=BaseInlineColumnFormSet,
    extra=1, can_order=False, can_delete=True
)
