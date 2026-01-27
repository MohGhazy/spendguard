from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import datetime, date
from .models import Transaction, Wallet, Category, Profile

@login_required
def dashboard_view(request):
    user = request.user
    now = datetime.now()

    month = request.GET.get('month')
    year = request.GET.get('year')

    month = int(month) if month else now.month
    year = int(year) if year else now.year

    tx_all = Transaction.objects.filter(
        user=user,
        date__month=month,
        date__year=year
    )

    # SUMMARY
    expense_total = tx_all.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0
    initial_income = Wallet.objects.filter(user=user).aggregate(total=Sum('initial_balance'))['total'] or 0
    real_income = tx_all.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0
    income_total = float(initial_income) + float(real_income)
    balance = income_total - float(expense_total)

    # EXPENSE DONUT
    expense_group = (
        tx_all.filter(type='expense')
        .values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    donut_labels = [row['category__name'] for row in expense_group]
    donut_values = [float(row['total']) for row in expense_group]

    total_expense = sum(donut_values) if donut_values else 0

    breakdown = []
    for name, val in zip(donut_labels, donut_values):
        pct = (val / total_expense * 100) if total_expense > 0 else 0
        breakdown.append({
            'name': name,
            'value': val,
            'pct': round(pct, 1)
        })

    breakdown.sort(key=lambda x: x['value'], reverse=True)

    # WALLET BREAKDOWN (REAL BALANCE)
    wallets = Wallet.objects.filter(user=request.user)
    wallet_breakdown = []

    for w in wallets:
        income = Transaction.objects.filter(wallet=w, type='income').aggregate(total=Sum('amount'))['total'] or 0
        expense = Transaction.objects.filter(wallet=w, type='expense').aggregate(total=Sum('amount'))['total'] or 0
        real_balance = float(w.initial_balance) + float(income) - float(expense)

        wallet_breakdown.append({
            'name': w.name,
            'balance': real_balance,
        })

    wallet_breakdown.sort(key=lambda x: x['balance'], reverse=True)

    # RECENT
    tx_recent = tx_all.order_by('-date', '-id')[:10]

    # FILTER UI
    months = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]
    years = list(range(now.year - 3, now.year + 1)) 

    context = {
        'tx': tx_recent,
        'income_total': income_total,
        'expense_total': expense_total,
        'balance': balance,
        'months': months,
        'years': years,
        'selected_month': month,
        'selected_year': year,
        'donut_labels': donut_labels,
        'donut_values': donut_values,
        'breakdown': breakdown,
        'wallet_breakdown': wallet_breakdown,
        'wallet_labels': [w['name'] for w in wallet_breakdown],
        'wallet_values': [w['balance'] for w in wallet_breakdown],
        'today': date.today().strftime('%Y-%m-%d'),
        'wallets': wallets,
        'categories': Category.objects.filter(user=user),
        'categories_income': Category.objects.filter(user=request.user, type='income'),
        'categories_expense': Category.objects.filter(user=request.user, type='expense'),
    }

    return render(request, 'main/dashboard.html', context)

@login_required
def onboard_wallet(request):
 if request.method == 'POST':
  name = request.POST.get('name')
  balance = request.POST.get('balance') or 0

  Wallet.objects.create(
   user=request.user,
   name=name,
   initial_balance=balance
  )

  return redirect('onboard_income')

 return render(request, 'main/onboard_wallet.html')


@login_required
def onboard_income(request):
 if request.method == 'POST':
  selected = request.POST.getlist('categories')
  custom = request.POST.get('custom')

  for cat in selected:
   Category.objects.create(user=request.user, name=cat, type='income')

  if custom:
   Category.objects.create(user=request.user, name=custom, type='income')

  return redirect('onboard_expense')

 income_defaults = ['Salary', 'Bonus', 'Freelance', 'Investment']
 return render(request, 'main/onboard_income.html', {'defaults': income_defaults})


@login_required
def onboard_expense(request):
 if request.method == 'POST':
  selected = request.POST.getlist('categories')
  custom = request.POST.get('custom')

  for cat in selected:
   Category.objects.create(user=request.user, name=cat, type='expense')

  if custom:
   Category.objects.create(user=request.user, name=custom, type='expense')

  profile = Profile.objects.get(user=request.user)
  profile.is_onboarded = True
  profile.save()

  return redirect('dashboard')

 expense_defaults = ['Food', 'Transport', 'Bills', 'Rent', 'Shopping', 'Health']
 return render(request, 'main/onboard_expense.html', {'defaults': expense_defaults})

@login_required
def transaction_list(request):
 user = request.user

 tx = Transaction.objects.filter(user=user).order_by('-date', '-id')

 context = {
  'tx': tx,
  'wallets': Wallet.objects.filter(user=user),
  'categories': Category.objects.filter(user=user),
 }
 return render(request, 'main/transactions.html', context)

@login_required
def transaction_add(request):
 if request.method == 'POST':
  user = request.user
  wallet = Wallet.objects.get(id=request.POST['wallet'])
  category = Category.objects.get(id=request.POST['category'])
  amount = request.POST['amount']
  tx_type = request.POST['type']
  date = request.POST['date']
  note = request.POST.get('note', '')

  Transaction.objects.create(
   user=user,
   wallet=wallet,
   category=category,
   type=tx_type,
   amount=amount,
   date=date,
   note=note,
  )

  return redirect('transactions')

 context = {
  'wallets': Wallet.objects.filter(user=request.user),
  'categories': Category.objects.filter(user=request.user),
 }
 return render(request, 'main/transaction_add.html', context)

@login_required
def transaction_edit(request, tx_id):
 tx = Transaction.objects.get(id=tx_id, user=request.user)

 if request.method == 'POST':
  tx.type = request.POST['type']
  tx.wallet_id = request.POST['wallet']
  tx.category_id = request.POST['category']
  tx.amount = request.POST['amount']
  tx.date = request.POST['date']
  tx.note = request.POST.get('note', '')
  tx.save()

  return redirect('transactions')

 context = {
  'tx': tx,
  'wallets': Wallet.objects.filter(user=request.user),
  'categories': Category.objects.filter(user=request.user),
 }
 return render(request, 'main/transaction_edit.html', context)

@login_required
def transaction_delete(request, tx_id):
 tx = Transaction.objects.get(id=tx_id, user=request.user)
 tx.delete()
 return redirect('transactions')

@login_required
def settings_home(request):
 return render(request, 'main/settings_home.html')

@login_required
def wallet_list(request):
 wallets = Wallet.objects.filter(user=request.user)
 return render(request, 'main/wallet_list.html', {'wallets': wallets})

@login_required
def wallet_add(request):
 if request.method == 'POST':
  Wallet.objects.create(
   user=request.user,
   name=request.POST['name'],
   initial_balance=request.POST.get('initial_balance', 0)
  )
  return redirect('wallet_list')

 return render(request, 'main/wallet_form.html')

@login_required
def wallet_edit(request, id):
 w = Wallet.objects.get(id=id, user=request.user)

 if request.method == 'POST':
  w.name = request.POST['name']
  w.initial_balance = request.POST.get('initial_balance', 0)
  w.save()
  return redirect('wallet_list')

 return render(request, 'main/wallet_form.html', {'wallet': w})

@login_required
def wallet_delete(request, id):
 Wallet.objects.get(id=id, user=request.user).delete()
 return redirect('wallet_list')

@login_required
def category_list(request):
 categories = Category.objects.filter(user=request.user)
 return render(request, 'main/category_list.html', {'categories': categories})

@login_required
def category_add(request):
 if request.method == 'POST':
  Category.objects.create(
   user=request.user,
   name=request.POST['name'],
   type=request.POST['type'],
  )
  return redirect('category_list')

 return render(request, 'main/category_form.html')

@login_required
def category_edit(request, id):
 c = Category.objects.get(id=id, user=request.user)
 if request.method == 'POST':
  c.name = request.POST['name']
  c.type = request.POST['type']
  c.save()
  return redirect('category_list')

 return render(request, 'main/category_form.html', {'category': c})

@login_required
def category_delete(request, id):
 Category.objects.get(id=id, user=request.user).delete()
 return redirect('category_list')