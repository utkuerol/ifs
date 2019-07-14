from datetime import datetime
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from .validators import validate_files
import django.utils.timezone as timezone


class Dataset(models.Model):
    """
    Model for Dataset object in database.

        Fields:
            -name: name (models.CharField)
            -description: description (models.CharField)
            -date: creation date (models.DateTimeField)
            -type: type of dataset {MNIST or HIPE} (models.ChoiceField)
            -feature_file: feature file (models.FileField)
            -normalized_feature_json: feature file with normalized values (models.CharField)
            -raw_file = raw file (models.FileField)
    """
    TYPE_CHOICES = (
        ("HIPE", "HIPE"),
        ("MNIST", "MNIST")
    )
    name = models.CharField(max_length=10000, null=False, unique=True)
    description = models.CharField(max_length=10000, null=False)
    date = models.DateTimeField(default=timezone.now, blank=True, null=False)
    type = models.CharField(max_length=10000, null=False, choices=TYPE_CHOICES)
    feature_file = models.FileField(upload_to='documents/%Y/%m/%d', null=False)
    normalized_feature_JSON = models.CharField(max_length=10000000, default=None, blank=True, null=True)
    raw_file = models.FileField(upload_to='documents/%Y/%m/%d', null=False)

    def get_absolute_url(self):
        return reverse('dataset-detail', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('dataset-update', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse('dataset-delete', kwargs={'pk': self.pk})

    def clean(self):
        """
        override the method to validate feature and raw data files.
        """
        feature_file = self.feature_file
        raw_file = self.raw_file
        type = self.type
        if feature_file and raw_file and type:
            validate_files(feature_file, raw_file, type)


class Setup(models.Model):
    """
    Model for Setup object in database.

        Fields:
            -dataset_id: id of the dataset for the experiment (models.ForeignKey)
            -name: name (models.CharField)
            -description: description (models.CharField)
            -classifier: selection of the classifier type {VanillaSVDD, SVDDNeg, SSAD (for further info: https://github.com/englhardt/OcalAPI.jl)} {required input for OcalAPI} (models.ChoiceField)
            -query_strategy: selection of the query strategy
                            {MinimumMarginQs, ExpectedMinimumMarginQs, MaximumEntropyQs, MaximumEntropyQs, MaximumLossQs, HighConfidenceQs, DecisionBoundaryQs, NeighborhoodBasedQs, BoundaryNeighborCombination, RandomQs, RandomOutlierQs}
                            {required input for OcalAPI} (models.ChoiceField)
            -parameters: gamma value for the classifier (models.FloatField)
            -cost-function: cost value for the classifier (models.FloatField)
            -feedback_mode: selection of feedback mode {User, OcalAPI or Hybrid} (models.ChoiceField)
            -number_of_iterations: permitted number Of Iterations (models.IntegerField)
            -status: status {draft, final} (models.ChoiceField)
            -unknown_allowed: if true user can choose "Unknown" as an answer (models.BooleanField)
            -raw_data_visible: if true user can see raw data (models.BooleanField)
            -feature_data_visible: if true user can see all columns from the feature data (models.BooleanField)
            -date: creation date (models.DateTimeField)
            -subspace_gridpoints_JSON: JSON File for the calculated gridpoints for each subspace (models.CharField)
    """
    YN_CHOICES = (
        ("Yes", "Yes"),
        ("No", "No")
    )
    CLASSIFIER_CHOICES = (
        ("VanillaSVDD", "Vanilla Support Vector Data Description"),
        ("SVDDneg", "SVDD with negative examples"),
        ("SSAD", "Semi-supervised Anomaly Detection")
    )
    QS_CHOICES = (
        ("MinimumMarginQs", "MinimumMarginQs"),
        ("ExpectedMinimumMarginQs", "ExpectedMinimumMarginQs"),
        ("MaximumLossQs", "MaximumLossQs"),
        ("MaximumEntropyQs", "MaximumEntropyQs"),
        ("HighConfidenceQs", "HighConfidenceQs"),
        ("DecisionBoundaryQs", "DecisionBoundaryQs"),
        ("NeighborhoodBasedQs", "NeighborhoodBasedQs"),
        ("BoundaryNeighborCombination", "BoundaryNeighborCombination"),
        ("RandomQs", "RandomQs"),
        ("RandomOutlierQs", "RandomOutlierQs")
    )
    FM_CHOICES = (
        ("user", "User"),
        ("system", "System"),
        ("hybrid", "Hybrid")
    )
    SETUP_STATUS_CHOICES = (
        ("draft", "draft"),
        ("final", "final")
    )
    dataset_id = models.ForeignKey(Dataset, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=10000, null=False, unique=True)
    description = models.CharField(max_length=10000, null=False)
    classifier = models.CharField(max_length=100, null=True, choices=CLASSIFIER_CHOICES)
    gamma = models.FloatField(null=True, validators=[MinValueValidator(0.01)])
    cost_function = models.FloatField(null=True, validators=[MinValueValidator(0.01)])
    query_strategy = models.CharField(max_length=100, null=True, choices=QS_CHOICES)
    feedback_mode = models.CharField(null=False, max_length=100, choices=FM_CHOICES)
    number_of_iterations = models.IntegerField(null=True, validators=[MinValueValidator(1)])
    status = models.CharField(null=False, max_length=100, default="draft", choices=SETUP_STATUS_CHOICES)
    unknown_allowed = models.CharField(max_length=100, null=True, choices=YN_CHOICES)
    raw_data_visible = models.CharField(max_length=100, null=True, choices=YN_CHOICES)
    feature_data_visible = models.CharField(max_length=100, null=True, choices=YN_CHOICES)
    date = models.DateTimeField(default=timezone.now, blank=True, null=False)
    subspaces_gridpoints_JSON = models.CharField(max_length=100000000, default=None, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('setup-detail', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('setup-update', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse('setup-delete', kwargs={'pk': self.pk})


class Session(models.Model):
    """
    Model for Session object in database.

        Fields:
            -setup_id: id of the setup that session belongs to (models.ForeignKey)
            -user_id: id of the user participating to the session (models.ForeignKey)
            -status: status {inactive, ongoing, finished, accepted} (models.ChoiceField)
            -date: creation date (models.DateTimeField)
    """
    SESSION_STATUS_CHOICES = (
        ("inactive", "inactive"),
        ("ongoing", "ongoing"),
        ("finished", "finished"),
        ("accepted", "accepted"),
        ("not_completed", "not_completed")
    )
    setup_id = models.ForeignKey(Setup, on_delete=models.CASCADE, null=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, default=None, blank=False)
    status = models.CharField(null=False, max_length=100, choices=SESSION_STATUS_CHOICES)
    date = models.DateTimeField(default=timezone.now, blank=True, null=False)

    def get_absolute_url(self):
        return reverse('session-detail', kwargs={'pk': self.pk})


class Iteration(models.Model):
    """
    Model for Iteration object in database.

        Fields:
            -session_id: id of the session that iteration belongs to (models.ForeignKey)
            -duration: time spent by user on the iteration (models.TimeField)
            -iteration_order: order of the iteration (models.IntegerField)
            -ocal_query_id: chosen object by OcalAPI for the feedback (models.IntegerField)
            -ocal_prediction: predicted labeling of OcalAPI (models.CharField)
            -user_feedback: feedback of the user for the object {Inlier, Outlier, Unknown} (models.ChoiceField)
            -ocal_output: calculation of OcalAPI after getting the user feedback (models.FileField)
    """
    session_id = models.ForeignKey(Session, on_delete=models.CASCADE, null=False)
    duration = models.IntegerField(default=0, blank=True, null=True)
    iteration_order = models.IntegerField(null=False)
    ocal_query_id = models.IntegerField(null=True)
    ocal_prediction = models.CharField(max_length=100, null=True)
    user_feedback = models.CharField(max_length=100, null=True)
    ocal_output = models.CharField(max_length=100000, null=True)

    class Meta:
        index_together = [
            ("session_id", "iteration_order")
        ]


class Subspace(models.Model):
    """
    Model for Subspace object in database.

        Fields:
        -setup_id: id of the setup that subspace belongs to (models.ForeignKey)
        -feature_x_id: id of the feature to be used in x-Axis of the subspace (models.IntegerField)
        -feature_y_id: id of the feature to be used in y-Axis of the subspace (models.IntegerField)
        -gridpoints_x: amount of points in each row in the gridpoints layout (models.IntegerField)
        -gridpoints_y: amount of points in each column in the gridpoints layout (models.IntegerField)
    """
    setup_id = models.ForeignKey(Setup, on_delete=models.CASCADE, null=False)
    feature_x_id = models.IntegerField(null=False)
    feature_y_id = models.IntegerField(null=False)
    gridpoints_x = models.IntegerField(null=True)
    gridpoints_y = models.IntegerField(null=True)

    class Meta:
        index_together = [
            ("setup_id", "feature_x_id", "feature_y_id")
        ]


class SubspaceUserInteractionStats(models.Model):
    """
    Model for SubspaceUserInteractionStats object in database.

        Fields:
        -subspace_id: id of subspace that the statistics belongs to (models.ForeignKey)
        -iteration_id: id of iteration that subspace belongs to (models.ForeignKey)
        -duration: time spent by user on observing the subspace (models.TimeField)
    """
    subspace_id = models.ForeignKey(Subspace, on_delete=models.CASCADE, null=False)
    iteration_id = models.ForeignKey(Iteration, on_delete=models.CASCADE, null=False)
    duration = models.IntegerField(default=0, blank=True, null=True)

    class Meta:
        index_together = [
            ("subspace_id", "iteration_id")
        ]
