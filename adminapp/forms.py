from django.forms.models import inlineformset_factory
from django import forms

from adminapp.models import Setup, Subspace, Dataset


class DatasetForm(forms.ModelForm):
    class Meta:
        model = Dataset
        exclude = ("type", "date", "normalized_feature_file", "raw_data_visualization")


class DatasetUpdateForm(forms.ModelForm):
    class Meta:
        model = Dataset
        exclude = ("type", "date", "feature_file", "raw_file", "normalized_feature_file", "raw_data_visualization")


class CustomModelChoiceField(forms.ModelChoiceField):
    """
    gets the label from the wanted object
    """

    def label_from_instance(self, obj):
        return "%s" % (obj.name)


class SetupForm(forms.ModelForm):
    dataset_id = CustomModelChoiceField(queryset=Dataset.objects.all())

    class Meta:
        model = Setup
        exclude = ("date", "status", "subspaces_gridpoints_JSON", "parameters")


SubspaceFormSet = inlineformset_factory(Setup, Subspace, fields='__all__', exclude=('subspace_order',), extra=1,
                                        can_delete=False)


class SetupUpdateForm(forms.ModelForm):
    # to print the name of the dataset object instead of id
    dataset_id = CustomModelChoiceField(queryset=Dataset.objects.all())

    class Meta:
        model = Setup
        exclude = ("date", "status", "subspaces_gridpoints_JSON")


SubspaceFormSetUpdate = inlineformset_factory(Setup, Subspace, fields='__all__',
                                              exclude=('subspace_order', "subspaces_gridpoints_JSON"), extra=1,
                                              can_delete=True)
