from django.shortcuts import render, redirect
from .models import Product, Buyer
from .forms import ProductForm

def admin_dashboard(request):
    products = Product.objects.all().order_by('-created_at')
    buyers = Buyer.objects.all().order_by('-purchased_at')
    return render(request, 'admin_dashboard.html', {'products': products, 'buyers': buyers})

def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})
