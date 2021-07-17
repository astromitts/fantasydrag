from flags.models import FeatureFlag


def context_processor(request):
    flags = {flag.title: flag.value == 1 for flag in FeatureFlag.objects.all()}
    return {'flags': flags}
