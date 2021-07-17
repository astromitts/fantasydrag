from flags.models import FeatureFlag


def context_processor(request):
    feature_flags = FeatureFlag.objects.all()
    flags = {}
    for flag in feature_flags:
        if flag.has_users and request.user in flag.users.all():
            flags[flag.title] = flag.value == 1
        else:
            flags[flag.title] = flag.value == 1
    return {'flags': flags}
