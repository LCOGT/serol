from django.shortcuts import get_object_or_404
from status.models import UserAnswer, Answer


def add_answers(answers, user):
    for answer_id in answers:
        aid = answer_id.replace('answer-', '')
        answer = get_object_or_404(Answer, pk=aid)
        created, ua = UserAnswer.objects.get_or_create(answer=answer, user=user)
    return True

def completed_missions(user):
    completed_missions = []
    for mid in range(1,4):
        if getattr(user, 'mission_'+str(mid)):
            completed_missions.append(mid)
    return completed_missions
