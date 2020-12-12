from django.views.generic import (CreateView, DeleteView,
                                  ListView, DetailView)
from django.contrib.auth.mixins import LoginRequiredMixin


class OwnerListView(LoginRequiredMixin, ListView):

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerDetailView(LoginRequiredMixin, DetailView):

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerCreateView(LoginRequiredMixin, CreateView):

    def form_valid(self, form):
        object_to_create = form.save(commit=False)
        object_to_create.owner = self.request.user
        object_to_create.save()
        return super().form_valid(form)


class OwnerDeleteView(LoginRequiredMixin, DeleteView):

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)
