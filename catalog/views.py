from django.shortcuts import render

from catalog.models import Book, Author, BookInstance, Genre

from django.contrib.auth.mixins import (LoginRequiredMixin, PermissionRequiredMixin)
# Create your views here.

def index(request):

	num_books = Book.objects.all().count()
	num_instances = BookInstance.objects.all().count()

	num_instances_available = BookInstance.objects.filter(status__exact='a').count()

	num_authors = Author.objects.count()

	num_genres = Genre.objects.count()
	num_books_with_pride = Book.objects.filter(title__iexact='Pride').count()

	num_visits = request.session.get('num_visits', 0)
	request.session['num_visits'] = num_visits + 1

	context = {
	'num_books': num_books,
	'num_instances': num_instances,
	'num_instances_available': num_instances_available,
	'num_authors': num_authors,
	'num_genres': num_genres,
	'num_books_with_pride': num_books_with_pride,
	'num_visits': num_visits,
	}

	return render(request, 'index.html', context=context)


from django.views.generic import (ListView, DetailView)

class BookListView(ListView):
	model = Book
	paginate_by = 5


class BookDetailView(DetailView):
	model = Book


class AuthorListView(ListView):
	model = Author
	paginate_by = 5

class AuthorDetailView(DetailView):
	model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, ListView):
	model = BookInstance
	template_name = 'catalog/bookinstance_list_borrowed_user.html'
	paginate_by = 10

	def get_queryset(self):
		return BookInstance.objects.filter(borrower = self.request.user).filter(status__exact='o').order_by('due_back')

class LoanedBooksAllListView(PermissionRequiredMixin, ListView):

	model = BookInstance
	permission_required = 'catalog.can_mark_returned'
	template_name = 'catalog/bookinstance_list_borrowed_all.html'
	paginate_by = 10

	def get_queryset(self):
		return BookInstance.objects.filter(status__exact='o').order_by('due_back')


import datetime

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from django.contrib.auth.decorators import permission_required

from catalog.forms import RenewBookForm

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
	book_instance = get_object_or_404(BookInstance, pk=pk)

	if request.method == 'POST':
		form = RenewBookForm(request.POST)

		if form.is_valid():
			book_instance.due_back = form.cleaned_data['renewal_date']
			book_instance.save()

			return HttpResponseRedirect(reverse('all-borrowed'))

	else:
		proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
		form = RenewBookForm(initial={'renewal_date' : proposed_renewal_date})
		# form = RenewBookModelForm(initial={'due_back' : proposed_renewal_date})


	context = {
	'form' : form,
	'book_instance' : book_instance,
	}

	return render(request, 'catalog/book_renew_librarian.html', context=context)


from django.views.generic.edit import (CreateView, UpdateView, DeleteView)
from django.urls import reverse_lazy

from catalog.models import Author, Book

class AuthorCreate(PermissionRequiredMixin, CreateView):
	permission_required = 'catalog.can_mark_returned'
	model = Author
	fields = '__all__'
	initial = {'date_of_death': '05/01/2018'}


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
	permission_required = 'catalog.can_mark_returned'
	model = Author
	fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


class AuthorDelete(PermissionRequiredMixin, DeleteView):
	permission_required = 'catalog.can_mark_returned'
	model = Author
	success_url = reverse_lazy('authors')


class BookCreate(CreateView):
	model = Book
	fields = '__all__'
	permission_required = 'catalog.can_mark_returned'


class BookUpdate(UpdateView):
	model = Book
	fields = '__all__'
	permission_required = 'catalog.can_mark_returned'


class BookDelete(DeleteView):
	model = Book
	success_url = reverse_lazy('books')
	permission_required = 'catalog.can_mark_returned'