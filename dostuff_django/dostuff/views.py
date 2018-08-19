from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Event, Category, UserEvent, UserCategory, EventCategory, UserProfile
from rest_framework import generics
from .serializers import EventSerializer
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
# import json



# Create your views here.

# class EventList(generics.ListCreateAPIView):
# 	queryset = Event.objects.all()
# 	serializer_class = EventSerializer

# class EventDetail(generics.RetrieveUpdateDestroyAPIView):
# 	queryset = Event.objects.all()
# 	serializer_class = EventSerializer
	

def events_list(request):
	events = Event.objects.all()
	events_serialized = serializers.serialize('json', events)

	# events = Event.objects.all()
	# serializer_class = EventSerializer
	return JsonResponse(events_serialized, safe=False)

@csrf_exempt
def user_add_event(request):
	if request.method == 'POST':
		event = Event.objects.get(pk=request.POST['eventid']) # change 1 to variable that holds userid --> sent in request
		# event_serialized = serializers.serialize('json', [event, ])

		user = User.objects.get(pk=request.POST['userid']) # change 1 to variable that holds userid --> sent in request

		user_event = UserEvent(userid=user, eventid=event)
		user_event.save()

		return JsonResponse({'status': 'Added Event to User'})

@csrf_exempt
def user_delete_event(request):
	if request.method == 'DELETE':
		event = Event.objects.get(pk=request.POST['eventid'])

		user = User.objects.get(pk=request.POST['userid'])

		user_event = UserEvent.objects.get(userid=request.POST['userid'], eventid=request.POST['eventid'])

		user_event.delete()

		return JsonResponse({'status': 'Removed Event from User'})



@csrf_exempt
def create_user(request):
	if request.method == 'POST':

		user = User.objects.create(username=request.POST['username'])
		user.set_password(request.POST['password'])

		user.save()

		user_profile = UserProfile(user=user, location=request.POST['location'])
		user_profile.save()
		

		return JsonResponse({'status': 'added user'})




@csrf_exempt
def edit_user(request):
	if request.method == 'PUT':
		# request.POST['userid']
		user_match = User.objects.get(pk=7)
		user_profile = UserProfile.objects.get(user=user_match)
		# print(user_profile.location, 'this is user profile location')
		print(request.POST, 'this is the request location')

		# user_profile.location = request.POST['location']
		# user_profile.save()

		# categories = UserCategory.objects.filter(userid=request.POST['userid'])

		# categories.delete()

		# for i in range(0, len(request.POST['category'])):
		# 	category_model = Category.objects.get(name=request.POST['category'][i])
		# 	user_category = UserCategory(userid=user_match, categoryid = category_model)
		# 	user_category.save()

		

		return JsonResponse({'status': 'updated user'})


@csrf_exempt
def dekete_user(request):
	if request.method == 'DELETE':
		# request.POST['userid']
		user_match = User.objects.get(pk=7)
		user_match.delete()	

		return JsonResponse({'status': 'deleted user'})




@csrf_exempt
def testing(request):
	if request.method == 'POST':

		# body_unicode = request.body.decode('utf-8')
		
		print(request.POST['test'], 'this is the request.body')		

		return JsonResponse({'status': 'added user'})




