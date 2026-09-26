from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError

from .models import Equipment, Operator
from .services import validate_cumulative_hours


class HourEntryForm(forms.Form):
    operator = forms.ModelChoiceField(
        label="Operator ID",
        queryset=Operator.objects.none(),
        empty_label="Select Operator",
        error_messages={
            "required": "অনুগ্রহ করে অপারেটর আইডি নির্বাচন করুন।",
            "invalid_choice": "অনুগ্রহ করে বৈধ অপারেটর আইডি নির্বাচন করুন।",
        },
    )
    equipment = forms.ModelChoiceField(
        label="Equipment",
        queryset=Equipment.objects.none(),
        empty_label="Select Equipment",
        error_messages={
            "required": "অনুগ্রহ করে Equipment নির্বাচন করুন।",
            "invalid_choice": "অনুগ্রহ করে বৈধ Equipment নির্বাচন করুন।",
        },
    )
    total_hours = forms.DecimalField(
        label="Cumulative Hours",
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0"),
        error_messages={
            "required": "অনুগ্রহ করে মোট সময় (Cumulative Hours) লিখুন।",
            "invalid": "অনুগ্রহ করে সঠিক সংখ্যায় মোট সময় লিখুন।",
            "min_value": "সময় অবশ্যই শূন্য বা তার বেশি হতে হবে।",
        },
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Enter cumulative hours",
                "step": "0.01",
                "min": "0",
                "inputmode": "decimal",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["operator"].queryset = Operator.objects.filter(is_active=True)
        self.fields["equipment"].queryset = Equipment.objects.filter(is_active=True)
        self.reading_bounds = None

    def clean(self):
        cleaned_data = super().clean()
        equipment = cleaned_data.get("equipment")
        total_hours = cleaned_data.get("total_hours")
        operator = cleaned_data.get("operator")
        if not equipment or total_hours is None:
            return cleaned_data
        try:
            self.reading_bounds = validate_cumulative_hours(
                equipment, total_hours, operator
            )
        except ValidationError as error:
            raise forms.ValidationError(error.messages)
        return cleaned_data


class ReportFilterForm(forms.Form):
    from_date = forms.DateField(
        label="From Date",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    to_date = forms.DateField(
        label="To Date",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    equipment = forms.ModelChoiceField(
        label="Equipment",
        queryset=Equipment.objects.none(),
        required=False,
        empty_label="All Equipment",
    )
    operator = forms.ModelChoiceField(
        label="Operator",
        queryset=Operator.objects.none(),
        required=False,
        empty_label="All Operators",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["equipment"].queryset = Equipment.objects.all()
        self.fields["operator"].queryset = Operator.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        from_date = cleaned_data.get("from_date")
        to_date = cleaned_data.get("to_date")
        if from_date and to_date and from_date > to_date:
            raise forms.ValidationError("From Date অবশ্যই To Date-এর আগে হতে হবে।")
        return cleaned_data