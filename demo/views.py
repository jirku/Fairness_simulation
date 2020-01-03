from django.shortcuts import render
from django.http import HttpResponseRedirect
import matplotlib.pyplot as plt
import json

# Create your views here.
from django.conf import settings

from .models import Market, Policy, Bank, Applicant_group, MarketForm, BankForm, Applicant_groupForm
from .src.simulation import Simulation

def index(request):
    if not request.session.exists(request.session.session_key):
        request.session.create()
        create_default_models(request)

    session_id = request.session.session_key
    groups = Applicant_group.objects.filter(session_id=session_id)
    market = Market.objects.get(session_id=session_id)
    banks = Bank.objects.filter(session_id=session_id)
    group_names =list(group.name for group in groups)
    group_sizes =list(group.size for group in groups)
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:

        if 'start' in request.POST:
            simulation=Simulation(session_id)
            steps=request.POST.get("steps")
            sim_banks, sim_groups, group_mean_score_change_curve = simulation.run_oligopoly(int(steps))
            groups_plot =[]
            step_array = []
            for group in sim_groups:
                n ,bins, patches = plt.hist(group.get_scores(),range = [market.score_range_min,market.score_range_max])
                bins =bins.tolist()
                bins.pop(0)
                step_array=list(range(len(group_mean_score_change_curve[group.name])))
                groups_plot.append({'name':group.name, 'color':group.color, 'hist':n.tolist(), 'hist_labels':bins, 'mean_score_change':group_mean_score_change_curve[group.name]})


            context = {'session_id': session_id, 'groups_plot':groups_plot, 'steps':steps, 'market':market, "groups":groups,
                'banks':banks,'step_array':step_array, }

            return render(request, 'index.html', context)


    context = {'session_id': session_id, 'group_names':group_names, 'group_sizes':group_sizes, "groups":groups, 'market':market, 'banks':banks}

    return render(request, 'index.html', context)

def setting(request):
# if this is a POST request we need to process the form data
        if not request.session.exists(request.session.session_key):
                request.session.create()
                create_default_models(request)

        session_id = request.session.session_key
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:

            form = MarketForm(request.POST)

            # check whether it's valid:
            if form.is_valid():
                # process the data in form.cleaned_data as required
                try:
                    instance = Market.objects.get(session_id=session_id)
                except(Market.DoesNotExist):
                    print("No previous market for this session id")
                else:
                    instance.delete()

                obj = form.save(commit=False)
                obj.session_id = session_id
                obj.save()

                return HttpResponseRedirect('../setting/')

        # if a GET (or any other method) we'll create a blank form
        else:
            form = MarketForm()

        markets = Market.objects.filter(session_id=session_id)


        return render(request, 'setting.html', {'form': form, 'markets':markets})

def model(request):
        if not request.session.exists(request.session.session_key):
                request.session.create()
                create_default_models(request)

        session_id = request.session.session_key
        Bform = BankForm()
        AGform =Applicant_groupForm()
# if this is a POST request we need to process the form data
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:

            if 'bank' in request.POST:
                Bform = BankForm(request.POST)
                AGform = Applicant_groupForm()
                # check whether it's valid:
                if Bform.is_valid():
                    # process the data in form.cleaned_data as required
                    obj = Bform.save(commit=False)
                    obj.session_id = session_id
                    obj.save()
                    # redirect to a new URL:
                    return HttpResponseRedirect('../model/')

            elif 'group' in request.POST:
                AGform = Applicant_groupForm(request.POST)
                Bform = BankForm()
                # check whether it's valid:
                if AGform.is_valid():
                    # process the data in form.cleaned_data as required
                    obj = AGform.save(commit=False)
                    obj.session_id = session_id
                    obj.save()
                    # redirect to a new URL:
                    return HttpResponseRedirect('../model/')

            elif "delete_bank" in request.POST:
                instance = Bank.objects.get(pk=request.POST.get("delete_bank"))
                instance.delete()
                return HttpResponseRedirect('../model/')

            elif "delete_group" in request.POST:
                instance = Applicant_group.objects.get(pk=request.POST.get("delete_group"))
                instance.delete()
                return HttpResponseRedirect('../model/')


        banks = Bank.objects.filter(session_id=session_id)
        applicant_groups = Applicant_group.objects.filter(session_id=session_id)

        return render(request, 'model.html', {'Bform': Bform,'AGform': AGform, 'banks':banks, 'applicant_groups':applicant_groups})

def create_default_models(request):
        session_id = request.session.session_key
        default_market=Market(session_id=session_id, policy="Max. utility")
        default_market.save()
        default_reference_bank=Bank(session_id=session_id, name="reference bank", color="red", line_style='-', low_score_interest_rate=0.15, high_score_interest_rate=0.06)
        default_reference_bank.save()
        default_conservative_bank=Bank(session_id=session_id, name="conservative bank", color="blue", line_style='--', low_score_interest_rate=0.18, high_score_interest_rate=0.04, score_shift=-25)
        default_conservative_bank.save()
        default_risk_taking_bank=Bank(session_id=session_id, name="risk taking bank", color="green", line_style=':', low_score_interest_rate=0.1, high_score_interest_rate=0.08, score_shift=50)
        default_risk_taking_bank.save()
        white_group=Applicant_group(session_id=session_id, name="White", color="grey", line_style='-', size=880, error_rate=0.1 ,score_error=-150, interest_rate_limit=0.3 )
        white_group.save()
        black_group=Applicant_group(session_id=session_id, name="Black", color="black", line_style=':', size=120, error_rate=0.1 ,score_error=150, interest_rate_limit=0.3 )
        black_group.save()