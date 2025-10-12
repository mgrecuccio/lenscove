from django import forms

class AddToCartForm(forms.Form):
    dimensions = forms.ChoiceField(
        initial='normal',
        choices=[('normal', '10x15'), ('medium', '13x18'), ('large', '20x30')],
        widget=forms.RadioSelect
    )
    frame_type = forms.ChoiceField(
        initial='plastic',
        choices=[('plastic', 'Plastic'), ('wood', 'Wood')],
        widget=forms.RadioSelect
    )
    frame_color = forms.ChoiceField(
        initial='black',
        choices=[('black', 'Black'), ('white', 'White'), ('wooden', 'Wooden')],
        widget=forms.RadioSelect
    )

    quantity = forms.IntegerField(
        min_value=0,
        max_value=99,
        initial=1,
        widget=forms.NumberInput(attrs={
            "class": "form-control text-center bord",
            "style": "width: 80px;",
            "id": "quantityInput"
        })
    )
    
    