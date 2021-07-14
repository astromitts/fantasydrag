from flags.models import FeatureFlag


def context_processor(request):
    flags = {flag.title: flag.value for flag in FeatureFlag.objects.all()}
    return {'flags': flags}
