from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group


from .models import *
from .forms import OrderForm,CreateUserForm
from .filters import OrderFilter
from .decorators import unauthenticated_user,allowed_users,admin_only
# Create your views here.
@unauthenticated_user
def registerPage(request):
	
	form = CreateUserForm()
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')

			group = Group.objects.get(name = 'customer')
			user.groups.add(group)

			messages.success(request,'Account was created for' +username)


			return redirect('login')

	context = {'form':form}
	return render(request,'register.html',context)

@unauthenticated_user
def loginPage(request):
		
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(request,username = username,password = password)
 
		if user is not None:
			login(request,user)
			return redirect('home')

		else:
			messages.info(request,'Username OR password is incorrect')

	context = {}
	return render(request,'login.html',context)

def logoutUser(request):
	logout(request)
	return redirect('login')



@login_required(login_url = 'login')
@admin_only
def home(request):

	orders = Order.objects.all()
	customers = Customer.objects.all()

	total_orders = orders.count()

	delivered = orders.filter(status = 'Delivered').count()
	pending = orders.filter(status = 'Pending').count()



	context = {'orders':orders,'customers':customers,'total_orders':total_orders
	,'delivered':delivered,'pending':pending}
	return render(request,'dashboard.html',context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['customer'])
def userPage(request):

	orders = request.user.customer.order_set.all()
	
	print('ORDERS:', orders)
		
	context = {'orders':orders}
	return render(request,'user.html',context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['admin'])
def medicine(request):

	medicine = Medicine.objects.all()

	return render(request,'medicine.html',{'medicine':medicine})

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['admin'])
def customer(request, pk_test):

	customer = Customer.objects.get(id=pk_test)

	orders = customer.order_set.all()
	order_count = orders.count()

	myFilter = OrderFilter(request.GET,queryset = orders)
	orders = myFilter.qs

	context = {'customer':customer,'orders':orders,'order_count':order_count,'myFilter':myFilter}
	return render(request,'customer.html',context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['admin'])
def createOrder(request,pk):

	orderFormSet = inlineformset_factory(Customer,Order,fields = ('medicine','status'),extra = 10)

	customer = Customer.objects.get(id = pk)
	formset = orderFormSet(queryset = Order.objects.none(), instance = customer)
	#form  = OrderForm(initial = {'customer':customer})
	if request.method == 'POST':
		#print("Printing POST:",request.POST)
		#form = OrderForm(request.POST)
		formset = orderFormSet(request.POST ,instance = customer)
		if formset.is_valid():
			formset.save()
			return redirect('home')
	context = {'formset':formset}

	return render(request,'order_form.html',context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['admin'])
def updateOrder(request, pk):

	order = Order.objects.get(id=pk)

	form = OrderForm(instance = order)

	if request.method == 'POST':
		#print("Printing POST:",request.POST)
		form = OrderForm(request.POST, instance =order)
		if form.is_valid():
			form.save()
			return redirect('home')

	context = {'form':form}

	return render(request,'order_form.html',context)

@login_required(login_url = 'login')
@allowed_users(allowed_roles = ['admin'])
def deleteOrder(request, pk):
	order = Order.objects.get(id=pk)
	if request.method == "POST":
		order.delete()
		return redirect('home')
	context = {'item':order}

	return render(request,'delete.html',context)