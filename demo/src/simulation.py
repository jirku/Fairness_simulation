import numpy as np
import random

#django model classes
from ..models import Market as Market_model
from ..models import Bank as Bank_model
from ..models import Applicant_group as Group_model

import demo.src.fico as fico
import demo.src.support_functions as sf

#main model classses
from demo.src.market import Market
from demo.src.bank import Bank
from demo.src.applicant_group import Applicant_group
from demo.src.applicant import Applicant


DATA_DIR = 'demo/data/'


class Simulation:

    #Creates instances for simulation from DB
    def __init__(self, session_id):
        print("Simulation initializing")
        #Set up main simulation classes according to setting
        market_instance = Market_model.objects.get(session_id=session_id)
        self.market = Market(policy=market_instance.policy, policy_color=market_instance.policy_color,
            score_range=[market_instance.score_range_min,market_instance.score_range_max],
            repay_score=market_instance.repay_score, default_score=market_instance.default_score,
            max_interest_rate_range = [market_instance.max_ir_range,market_instance.max_ir_range],
            min_interest_rate_range=[market_instance.min_ir_range,market_instance.min_ir_range],
            plane_range=[market_instance.plane_range_min,market_instance.plane_range_max],
            plane_slice_step= market_instance.plane_slice_step)

        bank_instances = Bank_model.objects.filter(session_id=session_id)
        self.banks =[]
        for bank_instance in bank_instances:
            self.banks.append(Bank(name=bank_instance.name, color=bank_instance.color, line_style=bank_instance.line_style,
                                   interest_rate_range=[bank_instance.low_score_interest_rate,bank_instance.high_score_interest_rate],
                                   interest_change_up=bank_instance.interest_change_up,interest_change_down=bank_instance.interest_change_down,
                                   market=self.market, score_shift=bank_instance.score_shift, utility_repaid=bank_instance.utility_repaid,
                                   utility_default=bank_instance.utility_default))

        group_instances = Group_model.objects.filter(session_id=session_id)
        repays, applicant_totals, ref_applicant_scores = self.prepare_initial_group_data(group_instances)
        self.groups = []
        i=0
        for group_instance in group_instances:
            self.groups.append(Applicant_group(name=group_instance.name, color=group_instance.color, line_style=group_instance.line_style,
                                               size=applicant_totals[i], scores=ref_applicant_scores[i], loan_demand=group_instance.loan_demand,
                                               error_rate=group_instance.error_rate, score_error=group_instance.score_error, market=self.market,
                                               repays=repays, ir_limit=group_instance.interest_rate_limit))
            i+=1



    def run_oligopoly(self, steps):
        market=self.market
        banks=self.banks
        groups=self.groups

        #init values of model classes
        for bank in banks:
            market.max_irates[bank.name] = []
            market.min_irates[bank.name] = []
            market.max_irates[bank.name].append(bank.interest_rate_range[0])
            market.min_irates[bank.name].append(bank.interest_rate_range[1])

            for group in groups:
                bank.N_loan_curves[group.name] = []
                bank.total_utility_curves[group.name] = []

        group_mean_score_change_curve = {}
        total_loans = {}
        total_utility = {}
        for group in groups:
            group_mean_score_change_curve[group.name] = [0]
            market.loans[group.name] = [0]
            market.utility[group.name] = [0]
            total_loans[group.name] = 0
            total_utility[group.name] = 0

        #run through simulation steps
        for step in range(0, steps):
            print("############### STEP "+ str(market.step) + " -> " + str(market.step+1) + " ##################" )
            utilities = {}
            utility_curves = {}
            N_loans = {}
            step_loans = 0
            step_applicants = 0

            ### Before ###
            selection_rates, max_util = market.get_selection_rate(banks, groups)
            for bank in banks:
                bank.set_selection_rate(selection_rates[bank.name])
                utilities[bank.name] = {}
                utility_curves[bank.name] = {}
                N_loans[bank.name] = {}

            ### During ###
            for group in groups:
                for bank in banks:
                    utilities[bank.name][group.name] = 0
                    utility_curves[bank.name][group.name] = []
                    N_loans[bank.name][group.name] = 0

                #select part of customer base at random according to group loan demand
                applicants = np.sort(random.sample(range(0, group.size), int(group.size*group.loan_demand)))
                step_applicants += len(applicants)
                #go over all selected customers in the group
                for j in applicants:
                    best_bank = None
                    best_interest_rate = np.Infinity

                    # check which bank gives best interest rate
                    for k in range(len(banks)):
                        if j/group.size <= banks[k].group_selection_rate[group.name]:
                            expected_applicant_score = banks[k].get_expected_applicant_score(market, group.applicants[j].score)
                            interest_rate = banks[k].score_interest_rates[expected_applicant_score]

                            if interest_rate < best_interest_rate and interest_rate < group.applicants[j].ir_limit:
                                best_interest_rate = interest_rate
                                best_bank = k

                    #print(best_bank)
                    if best_bank is not None:
                        #get loan outcome and change score
                        step_loans += 1
                        total_loans[group.name] += 1
                        N_loans[banks[best_bank].name][group.name] += 1
                        loan_outcome = group.applicants[j].get_repay_outcome(market)
                        expected_applicant_score = banks[best_bank].get_expected_applicant_score(market, group.applicants[j].score)

                        #get bank utility
                        interest_rate = banks[best_bank].score_interest_rates[group.applicants[j].score]
                        utility_change = banks[best_bank].get_applicant_utility(interest_rate, loan_outcome)
                        utilities[banks[best_bank].name][group.name] += utility_change
                        total_utility[group.name] += utility_change
                        utility_curves[banks[best_bank].name][group.name].append(utilities[banks[best_bank].name][group.name])

                for bank in banks:
                    if market.step == 0:
                        bank.N_loan_curves[group.name].append(N_loans[bank.name][group.name])
                        bank.total_utility_curves[group.name].append(utilities[bank.name][group.name])
                    else:
                        bank.N_loan_curves[group.name].append(bank.N_loan_curves[group.name][-1] + N_loans[bank.name][group.name])
                        bank.total_utility_curves[group.name].append(bank.total_utility_curves[group.name][-1] + utilities[bank.name][group.name])
                group.sort_by_score()
                group_mean_score_change_curve[group.name].append(group.get_mean_score_change())
                print(group.name + " group mean score change: " + str(group.get_mean_score_change()))

            market.step += 1

            ### After ###
            #adjust interest rate, we will need market share and utilities for this
            for bank in banks:

                bank_clients = 0
                total_clients = 0
                max_expected_utility = 0
                real_utility = 0
                #calculate market share and utilities
                for group in groups:
                    bank.real_group_utility_curve[group.name] = utility_curves[bank.name][group.name]
                    total_clients += group.size * group.loan_demand * bank.group_selection_rate[group.name]
                    bank_clients += len(bank.real_group_utility_curve[group.name])
                    max_expected_utility += np.max(bank.expected_group_utility_curve[group.name])* group.loan_demand

                    if len(bank.real_group_utility_curve[group.name])>0:
                        real_utility += bank.real_group_utility_curve[group.name][-1]

                bank.market_share = bank_clients/total_clients
                #change interest rate according to actual market share and utility
                if bank.market_share >= 1/len(banks) and real_utility >= max_expected_utility/len(banks):
                    bank.change_interest_rate(bank.interest_change_up, market)
                elif bank.market_share < 1/len(banks):
                    bank.change_interest_rate(bank.interest_change_down, market)

                print(bank.name + " bank - Market share: "  + str(bank.market_share) + ", Interest rate: " + str(bank.interest_rate_range))

                market.max_irates[bank.name].append(bank.interest_rate_range[0])
                market.min_irates[bank.name].append(bank.interest_rate_range[1])

            for group in groups:
                market.loans[group.name].append(total_loans[group.name])
                market.utility[group.name].append(total_utility[group.name])

            #market.plot_market_situation_oligo(banks, groups, group_mean_score_change_curve)
        return banks, groups, group_mean_score_change_curve

    def prepare_initial_group_data(self, group_instances):
        group_names = list(group.name for group in group_instances)
        all_cdfs, performance, totals = fico.get_FICO_data(data_dir=DATA_DIR)
        cdfs = all_cdfs[group_names]
        cdf_groups = np.transpose(cdfs.values)

        scores = cdfs.index
        scores_list = scores.tolist()
        scores_repay = cdfs.index

        repays = performance[group_names]

        ##### comment to use dataset totals (too many people)
        for group in group_instances:
            totals[group.name] = group.size
        ####

        group_totals = np.zeros(len(group_names), dtype=np.int32)
        for i in range(0,len(group_names)):
            group_totals[i] = int(totals[group_names[i]])

        pis = np.zeros(cdf_groups.shape)
        applicant_totals = np.zeros(len(group_names), dtype=np.int32)

        for i in range(0, len(group_names)):
            pis[i] = sf.get_pmf(cdf_groups[i])
            applicant_totals[i] = np.sum(np.round(pis[i]*group_totals[i]))
        print("Reference group totals: " + str(group_totals))
        print("Calculated group totals: " + str(applicant_totals))

        #demographic statistics
        group_ratio = np.array((applicant_totals[0], applicant_totals[1]))
        group_size_ratio = group_ratio/group_ratio.sum()
        print("Group size ratio: " + str(group_size_ratio))

        pis_total = np.round(pis*group_totals[:, None])

        ref_applicant_scores = sf.get_ref_applicants(applicant_totals, pis_total, scores_list)

        return repays, applicant_totals, ref_applicant_scores