import json
import traceback
from pprint import pprint

from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_list_or_404
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseServerError
from django.http import HttpResponseNotAllowed

# from apprentice_learner.models import ActionSet
from apprentice_learner.models import Agent
from agents.Dummy import Dummy
from agents.WhereWhenHow import WhereWhenHow
from agents.WhereWhenHowNoFoa import WhereWhenHowNoFoa
from agents.RLAgent import RLAgent

agents = {'Dummy': Dummy,
          'WhereWhenHowNoFoa': WhereWhenHowNoFoa,
          'WhereWhenHow': WhereWhenHow,
          'RLAgent': RLAgent}

debug = True


@csrf_exempt
def create(request):
    """
    This is used to create a new agent with the provided configuration.

    .. todo:: TODO Ideally there should be a way to create agents both using
    the browser and via a POST object.
    """
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    data = json.loads(request.body.decode('utf-8'))

    if debug:
        pprint(data)

    if 'agent_type' not in data or data['agent_type'] is None:
        print("request body missing 'agent_type'")
        return HttpResponseBadRequest("request body missing 'agent_type'")

    if data['agent_type'] not in agents:
        print("Specified agent not supported")
        return HttpResponseBadRequest("Specified agent not supported")

    if 'action_set' not in data or data['action_set'] is None:
        print("request body missing 'action_set'")
        return HttpResponseBadRequest("request body missing 'action_set'")

    # try:
    #     action_set = ActionSet.objects.get(name=data['action_set'])
    # except ActionSet.DoesNotExist:
    #     print("Specified action set does not exist")
    #     return HttpResponseBadRequest("Specified action set does not exist")
    action_set = data['action_set']

    if 'args' not in data:
        args = {}
    else:
        args = data['args']

    try:
        args['action_set'] = action_set
        instance = agents[data['agent_type']](**args)
        agent_name = data.get('name', '')
        agent = Agent(instance=instance, action_set=action_set,
                      name=agent_name)
        agent.save()
        ret_data = {'agent_id': str(agent.id)}

    except Exception as e:
        print("Failed to create agent", e)
        return HttpResponseServerError("Failed to create agent, "
                                       "ensure provided args are "
                                       "correct.")

    return HttpResponse(json.dumps(ret_data))


@csrf_exempt
def request(request, agent_id):
    """
    Returns an SAI description for a given a problem state according to the
    current knoweldge base.  Expects an HTTP POST with a json object stored as
    a utf-8 btye string in the request body.
    That object should have the following fields:
    """
    try:
        if request.method != "POST":
            return HttpResponseNotAllowed(["POST"])
        data = json.loads(request.body.decode('utf-8'))

        if 'state' not in data or data['state'] is None:
            print("request body missing 'state'")
            return HttpResponseBadRequest("request body missing 'state'")

        agent = Agent.objects.get(id=agent_id)
        agent.inc_request()
        response = agent.instance.request(data['state'])
        agent.save()
        return HttpResponse(json.dumps(response))

    except Exception as e:
        traceback.print_exc()
        return HttpResponseServerError(str(e))


@csrf_exempt
def request_by_name(http_request, agent_name):
    agent = get_list_or_404(Agent, name=agent_name)[0]
    return request(http_request, agent.id)


@csrf_exempt
def train(request, agent_id):
    """
    Trains the Agent with an state annotated with the SAI used / with
    feedback.
    """
    try:
        if request.method != "POST":
            return HttpResponseNotAllowed(["POST"])
        data = json.loads(request.body.decode('utf-8'))

        if 'state' not in data or data['state'] is None:
            print("request body missing 'state'")
            return HttpResponseBadRequest("request body missing 'state'")
        if 'label' not in data or data['label'] is None:
            print("request body missing 'label'")
            data['label'] = 'NO_LABEL'
            # return HttpResponseBadRequest("request body missing 'label'")
        if 'foas' not in data or data['foas'] is None:
            print("request body missing 'foas'")
            data['foas'] = {}
            # return HttpResponseBadRequest("request body missing 'foas'")
        if 'selection' not in data or data['selection'] is None:
            print("request body missing 'selection'")
            return HttpResponseBadRequest("request body missing 'selection'")
        if 'action' not in data or data['action'] is None:
            print("request body missing 'action'")
            return HttpResponseBadRequest("request body missing 'action'")
        if 'inputs' not in data or data['inputs'] is None:
            print("request body missing 'inputs'")
            return HttpResponseBadRequest("request body missing 'inputs'")
        if 'correct' not in data or data['correct'] is None:
            print("request body missing 'correct'")
            return HttpResponseBadRequest("request body missing 'correct'")

        agent = Agent.objects.get(id=agent_id)
        agent.inc_train()

        agent.instance.train(data['state'], data['label'], data['foas'],
                             data['selection'], data['action'], data['inputs'],
                             data['correct'])
        agent.save()
        return HttpResponse("OK")

    except Exception as e:
        traceback.print_exc()
        return HttpResponseServerError(str(e))


@csrf_exempt
def train_by_name(request, agent_name):
    agent = get_list_or_404(Agent, name=agent_name)[0]
    return train(request, agent.id)


@csrf_exempt
def check(request, agent_id):
    """
    Uses the knoweldge base to check the correctness of an SAI in provided
    state.
    """
    try:
        if request.method != "POST":
            return HttpResponseNotAllowed(["POST"])
        data = json.loads(request.body.decode('utf-8'))

        if 'state' not in data:
            return HttpResponseBadRequest("request body missing 'state'")
        if 'selection' not in data:
            return HttpResponseBadRequest("request body missing 'selection'")
        if 'action' not in data:
            return HttpResponseBadRequest("request body missing 'action'")
        if 'inputs' not in data:
            return HttpResponseBadRequest("request body missing 'inputs'")

        agent = Agent.objects.get(id=agent_id)
        agent.inc_check()
        agent.save()

        response = {}

        response['correct'] = agent.instance.check(data['state'],
                                                   data['selection'],
                                                   data['action'],
                                                   data['inputs'])
        return HttpResponse(json.dumps(response))

    except Exception as e:
        traceback.print_exc()
        return HttpResponseServerError(str(e))


@csrf_exempt
def check_by_name(request, agent_name):
    agent = get_list_or_404(Agent, name=agent_name)[0]
    return check(request, agent.id)


def report(request, agent_id):
    if request.method != "GET":
            return HttpResponseNotAllowed(["GET"])

    agent = get_object_or_404(Agent, id=agent_id)

    response = {
        'id': agent.id,
        'name': agent.name,
        'num_request': agent.num_request,
        'num_train': agent.num_train,
        'num_check': agent.num_check,
        'created': agent.created,
        'updated': agent.updated
    }

    response = {k: str(response[k]) for k in response}
    return HttpResponse(json.dumps(response))


def report_by_name(request, agent_name):
    agent = get_list_or_404(Agent, name=agent_name)[0]
    return report(request, agent.id)
