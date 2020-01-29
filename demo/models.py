from django.db import models
from django.forms import ModelForm
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.
POLICY_CHOICES = [
    ('Max. utility', 'Maximum utility'),
    ('Dem. parity', 'Demographic parity'),
    ('Equal opportunity', 'Equal opportunity'),
]

COLOR_CHOICES = [
    ('#B80F0A', 'Red'),
    ('#50C878', 'Green'),
    ('#4E73DF', 'Blue'),
    ('#000000', 'Black'),
    ('#C0C0C0', 'Silver'),
]

LINE_STYLE_CHOICES = [
    ('-', '- solid line'),
    (':', ': dotted line'),
    ('--', '-- dashed line'),
    ('-.', '-. dashdot line'),
]

APPLICANT_GROUP_CHOICES = [
    ('White', 'White'),
    ('Black', 'Black'),
    ('Asian', 'Asian'),
    ('Hispanic', 'Hispanic'),
]


class Policy(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7,choices=COLOR_CHOICES)

    def __str__(self):
        return self.name

class Market(models.Model):
    session_id = models.CharField(max_length=64)
    policy = models.CharField(max_length=40,choices=POLICY_CHOICES, help_text = 'Which policy will be used on the market to evaluate credit applicants')
    policy_color = models.CharField(max_length=7,choices=COLOR_CHOICES,  help_text = 'Choose color to be associated with the policy')
    score_range_min = models.IntegerField(default=300, help_text = 'Set minimum of score range. Default FICO score range minimum is 300')
    score_range_max = models.IntegerField(default=850, help_text = 'Set maximum of score range. Default FICO score range maximum is 850')
    repay_score = models.IntegerField(default=75, help_text = 'Set score increase in case of repaid loan')
    default_score = models.IntegerField(default=-150, help_text = 'Set score decrease in case of default loan')
    max_ir_range = models.FloatField(default=0.5, help_text = 'Maximum interest rate that can be given on the market')
    min_ir_range = models.FloatField(default=0.001, help_text = 'Minimum interest rate that can be given on the market.')
    plane_range_max = models.FloatField(default=1, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], help_text = 'Defines the maximal market share boundaries for banks. Range from 0.0 to 1.0')
    plane_range_min = models.FloatField(default=0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], help_text = 'Defines the minimal market share boundaries for banks. Range from 0.0 to 1.0')
    plane_slice_step = models.FloatField(default=0.01, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], help_text = 'Market share granularity. Range from 0.0 to 1.0')

    def __str__(self):
        return(str(self.session_id) + ": " + self.policy.name)

class MarketForm(ModelForm):
    class Meta:
        model = Market
        fields = ['policy', 'policy_color', 'score_range_min', 'score_range_max', 'repay_score', 'default_score', 'max_ir_range', 'min_ir_range']


class Bank(models.Model):
    session_id = models.CharField(max_length=64)
    name = models.CharField(max_length=100, help_text="Choose bank name")
    color = models.CharField(max_length=7,choices=COLOR_CHOICES, help_text="Choose color which would represent the bank in plots.")
    line_style = models.CharField(max_length=3,choices=LINE_STYLE_CHOICES, help_text="Choose line styl which would represent the bank in plots.")
    low_score_interest_rate = models.FloatField(default=0.15, help_text="Initial interest rate for applicants with low scores.")
    high_score_interest_rate = models.FloatField(default=0.06, help_text="Initial interest rate for applicants with high scores.")
    score_shift = models.IntegerField(default=0, validators=[MinValueValidator(-550), MaxValueValidator(550)], help_text="The score shift represents the bank's subjective applicant evaluation and information asymmetry across banks. With positive score shift the bank believes in applicants higher repay probability. Range from -550 to 550.")
    utility_repaid = models.FloatField(default=1, validators=[MinValueValidator(0.0)], help_text="This represents the utility, which the bank has from repaid loan. The interest rate is later added to this utility. Should be positive number greater or equal to 0.0.")
    utility_default = models.FloatField(default=-4, validators=[ MaxValueValidator(0.0)], help_text="This represents the utility, which the bank has from defaulted loan. Should be negative number less or equal to 0.0.")
    interest_change_up = models.FloatField(default=0.01, validators=[MinValueValidator(0.0)], help_text="The increase of interest rates offered by bank, if the bank meets certain conditions after each time step. Should be positive number greater or equal to 0.0.")
    interest_change_down = models.FloatField(default=-0.01, validators=[ MaxValueValidator(0.0)], help_text="The decrease of interest rates offered by bank, if the bank does not meet certain conditions after each time step. Should be negative number less or equal to 0.0.")
    
    def __str__(self):
        return(str(self.session_id) + ": " + self.name) 

class BankForm(ModelForm):
    class Meta:
        model = Bank
        fields = ['name', 'color', 'line_style','low_score_interest_rate', 'high_score_interest_rate', 'score_shift',
            'utility_repaid', 'utility_default', 'interest_change_up', 'interest_change_down']


class Applicant_group(models.Model):
    session_id = models.CharField(max_length=64)
    name = models.CharField(max_length=10,choices=APPLICANT_GROUP_CHOICES, help_text="In the dataset used for this simulation there are four groups with different repay probabilities and score distributions based on historical data.")
    color = models.CharField(max_length=7,choices=COLOR_CHOICES, help_text="Choose color representing this group in plots.")
    line_style = models.CharField(max_length=3,choices=LINE_STYLE_CHOICES, help_text="Choose line style representing this group in plots.")
    size = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100000)], help_text="Choose the size of the group from 1 to 100 000.")
    loan_demand = models.FloatField(default=0.1, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], help_text="Proportion of the group to be randomly chosen to apply for a loan in one simulation step. Range from 0.0 to 1.0.")
    error_rate = models.FloatField(default=0.1, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], help_text="Proportion of the group with an induced error/score change. Range from 0.0 to 1.0.")
    score_error = models.IntegerField(default=150, validators=[MinValueValidator(-550), MaxValueValidator(550)], help_text="Score change of applicants selected by the error rate. Negative score leads to lower repay probability. Positive score leads to higher repay probability. Range from -550 to 550.")
    interest_rate_limit = models.FloatField(default=0.3, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], help_text="Maximal interest rate of the applicants in this group, under which they will take loan. Range from 0.0 to 1.0.")

    def __str__(self):
        return(str(self.session_id) + ": " + self.name + ": " + self.str(size)) 


class Applicant_groupForm(ModelForm):
    class Meta:
        model = Applicant_group
        fields = ['name', 'color', 'line_style', 'size', 'loan_demand', 'error_rate', 'score_error', 'interest_rate_limit']


class Group_state(models.Model):
    session_id = models.CharField(max_length=64)
    size = models.IntegerField()
    score_histogram = models.TextField()
    score_histogram_bins = models.TextField()
    real_score_histogram = models.TextField()
    real_score_histogram_bins = models.TextField()
    mean_score_change_curve = models.TextField()
    total_loans = models.TextField()

class Market_state(models.Model):
    session_id = models.CharField(max_length=64)
    step = models.IntegerField()


class Bank_state(models.Model):
    session_id = models.CharField(max_length=64)
    max_irates = models.TextField()
    min_irates = models.TextField()


class Applicant(models.Model):
    group = models.ForeignKey(Group_state, on_delete=models.CASCADE)
    score = models.IntegerField()
    real_score = models.IntegerField()

    def __str__(self):
        return(str(self.group) + ": " + self.score + " : " + self.real_score)
