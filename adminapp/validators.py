from django.core.exceptions import ValidationError
import os


def validate_files(feature_file, raw_file, type):
    """
    validate the files of the dataset before its creation to provide future errors.
    :param feature_file: feature file of the dataset
    :param raw_file: raw file of the dataset
    :param type: type of the dataset
    """
    error_msg = ''
    feature_file_validation = _validate_feature_file(feature_file, type)
    if feature_file_validation != '':
        error_msg += feature_file_validation + " \n"
    raw_file_validation = _validate_raw_file(raw_file, type)
    if raw_file_validation != '':
        error_msg += raw_file_validation
    if error_msg != '':
        raise ValidationError(error_msg)


def _validate_feature_file(feature_file, type):
    """
    validate feature file of the dataset before its creation to provide future errors.
    :param feature_file: feature file of the dataset
    :param type: type of the dataset
    :return: the error string or empty string if no error is found
    """
    from datautil.facade import Facade
    fail = _validate_feature_file_extension(feature_file)
    if fail:
        return 'Features file : Unsupported file extension.'
    else:
        success = Facade.validate_feature_data_format(feature_file, type)
        if not success:
            return 'Feature file: The uploaded file is not in the required format.'
        return ''


def _validate_feature_file_extension(value):
    """
    validate the extension of feature file of the dataset before its creation to provide future errors.
    :param value: feature file of the dataset
    :return:the error string or empty string if no error is found
    """
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.csv', '.xlsx', '.xls']
    fail = False
    if not ext.lower() in valid_extensions:
        fail = True
    return fail


def _validate_raw_file(raw_file, type):
    """
    validate the raw file of the dataset before its creation to provide future errors.
    :param raw_file: raw file of the dataset
    :return:the error string or empty string if no error is found
    """
    from datautil.facade import Facade
    fail = _validate_raw_file_extension(raw_file)
    if fail:
        return 'Raw data file : Unsupported file extension.'
    else:
        success = Facade.validate_raw_data_format(raw_file, type)
        if not success:
            return 'Raw file: The uploaded file is not in the required format.'
        return ''


def _validate_raw_file_extension(value):
    """
    validate the extension raw file of the dataset before its creation to provide future errors.
    :param value: raw file of the dataset
    :return:the error string or empty string if no error is found
    """
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.json']
    fail = False
    if not ext.lower() in valid_extensions:
        fail = True
    return fail
