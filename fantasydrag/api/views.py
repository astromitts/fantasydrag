from rest_framework.response import Response
from rest_framework.views import APIView

from fantasydrag.models import (
    Episode,
    Rule,
    Score,
    Queen,
)
from fantasydrag.api.serializers import (
    EpisodeScore,
    ScoreSerializer
)


class NewsPostApi(APIView):
    def get(self, request, *args, **kwargs):
        episode = Episode.objects.get(pk=kwargs['episode_id'])
        serializer = EpisodeScore(instance=episode, many=False)
        response = serializer.data
        return Response(response)

    def put(self, request, *args, **kwargs):
        episode = Episode.objects.get(pk=kwargs['episode_id'])
        queen = Queen.objects.get(pk=request.data['queen'])
        rule = Rule.objects.get(pk=request.data['rule'])
        score = Score(
            episode=episode,
            rule=rule,
            queen=queen
        )
        score.save()
        serializer = ScoreSerializer(instance=score, many=False)
        response = serializer.data
        return Response(response)

    def patch(self, request, *args, **kwargs):
        episode = Episode.objects.get(pk=kwargs['episode_id'])
        if episode.is_scored:
            episode.is_scored = False
        else:
            episode.is_scored = True
        episode.save()
        serializer = EpisodeScore(instance=episode, many=False)
        response = serializer.data
        return Response(response)

    def delete(self, request, *args, **kwargs):
        score = Score.objects.get(pk=kwargs['score_id'])
        score.delete()
        response = {'status': 'ok'}
        return Response(response)
