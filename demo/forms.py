from django import forms

class ModelSetting(forms.Form):
    session_id = models.IntegerField()
    policy = models.ForeignKey(Policy,on_delete=models.CASCADE)
    score_range_min = models.IntegerField(default=300)
    score_range_max = models.IntegerField(default=850)
    repay_score = models.IntegerField(default=75)
    default_score = models.IntegerField(default=-150)
    max_ir_range = models.FloatField(default=0.5)
    min_ir_range = models.FloatField(default=0.001)
    plane_range_max = models.FloatField(default=1)
    plane_range_min = models.FloatField(default=0)
    plane_slice_step = models.FloatField(default=0.01)
    step = models.IntegerField(default=0)