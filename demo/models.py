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
    policy = models.CharField(max_length=40,choices=POLICY_CHOICES)
    policy_color = models.CharField(max_length=7,choices=COLOR_CHOICES)
    score_range_min = models.IntegerField(default=300)
    score_range_max = models.IntegerField(default=850)
    repay_score = models.IntegerField(default=75)
    default_score = models.IntegerField(default=-150)
    max_ir_range = models.FloatField(default=0.5)
    min_ir_range = models.FloatField(default=0.001)
    plane_range_max = models.FloatField(default=1, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    plane_range_min = models.FloatField(default=0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    plane_slice_step = models.FloatField(default=0.01, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])

    def __str__(self):
        return(str(self.session_id) + ": " + self.policy.name)

class MarketForm(ModelForm):
    class Meta:
        model = Market
        fields = ['policy', 'policy_color', 'score_range_min', 'score_range_max', 'repay_score', 'default_score', 'max_ir_range', 'min_ir_range']


class Bank(models.Model):
    session_id = models.CharField(max_length=64)
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7,choices=COLOR_CHOICES)
    line_style = models.CharField(max_length=3,choices=LINE_STYLE_CHOICES)
    low_score_interest_rate = models.FloatField(default=0.15)
    high_score_interest_rate = models.FloatField(default=0.06)
    score_shift = models.IntegerField(default=0)
    utility_repaid = models.FloatField(default=1)
    utility_default = models.FloatField(default=-4)
    interest_change_up = models.FloatField(default=0.01)
    interest_change_down = models.FloatField(default=-0.01)
    
    def __str__(self):
        return(str(self.session_id) + ": " + self.name) 

class BankForm(ModelForm):
    class Meta:
        model = Bank
        fields = ['name', 'color', 'line_style','low_score_interest_rate', 'high_score_interest_rate', 'score_shift',
            'utility_repaid', 'utility_default', 'interest_change_up', 'interest_change_down']


class Applicant_group(models.Model):
    session_id = models.CharField(max_length=64)
    name = models.CharField(max_length=10,choices=APPLICANT_GROUP_CHOICES)
    color = models.CharField(max_length=7,choices=COLOR_CHOICES)
    line_style = models.CharField(max_length=3,choices=LINE_STYLE_CHOICES)
    size = models.IntegerField()
    loan_demand = models.FloatField(default=0.1, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    error_rate = models.FloatField(default=0.1, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    score_error = models.IntegerField(default=150)
    interest_rate_limit = models.FloatField(default=0.3)
    
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
