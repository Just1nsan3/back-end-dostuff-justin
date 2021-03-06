from django.shortcuts import render
from django.http import JsonResponse, QueryDict
from django.contrib.auth.models import User
from .models import Event, Category, UserEvent, UserCategory, EventCategory, UserProfile
from rest_framework import generics
from .serializers import EventSerializer
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import requests
import time
import datetime
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict

@csrf_exempt
def not_logged_in(request):
	return JsonResponse({'status': 400, 'data': 'User not authenitcated'})


@csrf_exempt
def log_user_in(request):


	parsedData = json.loads(request.body)


	username = parsedData['username']
	password = parsedData['password']

	user = authenticate(request, username=username, password=password)
	if user is not None:
		login(request, user)
		user_match = User.objects.get(username=username)
		user_categories = UserCategory.objects.filter(userid=user)
		categories = []
		for i in range(0, len(user_categories)):
			# cat = Category.objects.get(pk=user_categories[i].categoryid)
			categories.append(user_categories[i].categoryid)
		user_categories_JSON = serializers.serialize('json', categories)
		return JsonResponse({'status': 200, 'userid': user_match.id, 'categories': user_categories_JSON })
	else:
		return JsonResponse({'status': 400, 'data': 'Did not Log in'})



@csrf_exempt
def logout_view(request):
	if request.user.is_authenticated:
	    logout(request)
	    return JsonResponse({'status': 200, 'data': 'Logged Out'})
	else: 
		return JsonResponse({'status': 400, 'data': 'User not authenticated'})
	


# SEND BACK ALL EVENTS IF NOT LOGGED IN AND ALL CATEGORIES
# SEND BACK USER EVENTS AND CATEGORIES IF LOGGED IN
def events_list(request):
	events = Event.objects.all()
	for i in range(0, len(events)):
		print(model_to_dict(events[i]))

	categories = Category.objects.all()

	# Need to find user's location for intial event search
	# Need to update date so it only pulls event from today onwards

	current_time = int(time.time())
	next_week = current_time + 604800

	response = requests.get("https://api.yelp.com/v3/events?location=Chicago&limit=50&start_date={}&end_date={}".format(current_time, next_week), headers={'Authorization': 'Bearer gr0amugCLWzgKkSCIgPZnPI8e7cRXFuEprIOGszYzUIo9JH5kWT1LMMZUkIW0tOBpywUrjmxns-zKDh5FoGsj4_SPNZG_-WDeGAzOCESd0wG9ZX5tUOXIRo4H2poW3Yx'})

	response_json = response.json()

	in_database = False

	# for every event we got from yelp
	for i in range(0, len(response_json['events'])):

		print("latitude", response_json['events'][i]['latitude'])
		print("longitude", response_json['events'][i]['longitude'])
		print("---------")

		# for every event in the database
		for j in range(0, len(events)):

			# if the URLs match
			if events[j].url == response_json['events'][i]['event_site_url']:
				# this event is in database
				in_database = True

		# if this event from response is not in database
		if in_database == False:

			#add event to database:

			#set time according to yelp response:
			date_str, time_str = response_json['events'][i]['time_start'].split(' ')
			year, month, day = date_str.split('-')

			# make a dd/mm/yyy formatted string according to time from response json
			s = '{}/{}/{}'.format(day, month, year)

			# get unix time from that
			unix_time = time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())

			# create event instance from Model
			e = Event(
				name=response_json['events'][i]['name'], 
				date=unix_time, time=time_str, 
				description=response_json['events'][i]['description'], 
				url=response_json['events'][i]['event_site_url'], 
				category=response_json['events'][i]['category'],
				image_url=response_json['events'][i]['image_url'],
				address=response_json['events'][i]['location']['address1'],
				city=response_json['events'][i]['location']['city'],
				state=response_json['events'][i]['location']['state'],
				latitude=response_json['events'][i]['latitude'],
				longitude=response_json['events'][i]['longitude'],
			)

			# save it
			e.save()

			for k in range(0, len(categories)):
				if(categories[k].name == response_json['events'][i]['category']):
					ec = EventCategory(eventid=e, categoryid=categories[k])
					ec.save()



			# also need to find category and search database for category match then add to eventcategory table
			in_database = False

	new_event_list = Event.objects.all()
	events_serialized = serializers.serialize('json', new_event_list)

	category_list = Category.objects.all()
	categories_serialized = serializers.serialize('json', category_list)
	
	# response.json()
	# response_json = serializers.serialize('json', response)

	# events = Event.objects.all()
	# serializer_class = EventSerializer
	return JsonResponse({'status': 200, 'data': {'events': events_serialized, 'categories': categories_serialized}})




# NO DATA NEEDED IN RESPONSE
@csrf_exempt
def user_add_event(request):
	if request.method == 'POST' and request.user.is_authenticated:
		event = Event.objects.get(pk=request.POST['eventid']) # change 1 to variable that holds userid --> sent in request
		# event_serialized = serializers.serialize('json', [event, ])

		user = User.objects.get(pk=request.POST['userid']) # change 1 to variable that holds userid --> sent in request

		user_event = UserEvent(userid=user, eventid=event)
		user_event.save()

		return JsonResponse({'status': 'Added Event to User'})
	else: 
		return JsonResponse({'status': 400, 'data': 'User not authenticated'})



# NO DATA NEEDED IN RESPONSE
@csrf_exempt
def user_delete_event(request):
	if request.method == 'DELETE' and request.user.is_authenticated:
		event = Event.objects.get(pk=request.POST['eventid'])

		user = User.objects.get(pk=request.POST['userid'])

		user_event = UserEvent.objects.get(userid=request.POST['userid'], eventid=request.POST['eventid'])

		user_event.delete()

		return JsonResponse({'status': 'Removed Event from User'})
	else: 
		return JsonResponse({'status': 400, 'data': 'User not authenticated'})




# USERID AND LOGGED IN TRUE 
@csrf_exempt
def create_user(request):
	if request.method == 'POST':

		parsedData = json.loads(request.body)

		user = User.objects.create(username=parsedData['username'])
		user.set_password(parsedData['password'])

		user.save()

		user_profile = UserProfile(user=user, location=parsedData['location'])
		user_profile.save()

		return JsonResponse({'status': 200, 'userid': user.id})





# UPDATED LIST OF ALL USER CATEGORY EVENTS
@csrf_exempt
def edit_user(request):

	if request.method == 'PUT' and request.user.is_authenticated:
		# request.POST['userid']
		request_dict = json.loads(request.body)
		# request_dict = QueryDict(request.body).dict()

		user_match = User.objects.get(pk=request_dict['userid'])
		user_profile = UserProfile.objects.get(user=user_match)

		user_profile.location = request_dict['location']
		user_profile.save()

		categories = UserCategory.objects.filter(userid=request_dict['userid'])

		categories.delete()

		# cat_list = eval(request_dict['categories'])
		cat_list = request_dict['categories']

		user_events = []

		for i in range(0, len(cat_list)):
			category_model = Category.objects.get(name=cat_list[i])
			user_category = UserCategory(userid=user_match, categoryid = category_model)
			user_category.save()


		user_cats = UserCategory.objects.filter(userid=request_dict['userid'])

		for i in range(0, len(user_cats)):
			cat_events = EventCategory.objects.filter(categoryid=user_cats[i].categoryid)
			user_events.extend(cat_events)

		events = []

		for i in range(0, len(user_events)):
			# found_event = Event.objects.get(id=user_events[i].eventid)
			events.append(user_events[i].eventid)




		events_serialized = serializers.serialize('json', events)
		#FIND ALL CATEGORIES ASSOCIATED WITH USER
		#FIND ALL EVENTS ASSOCIATED WITH THOSE CATEGORIES


		return JsonResponse({'status': 200, 'data': events_serialized})

	else: 
		return JsonResponse({'status': 400, 'data': 'User not authenticated'})




# REMOVE LOGGED IN TRUE
@csrf_exempt
def delete_user(request):
	if request.method == 'DELETE' and request.user.is_authenticated:

		request_dict = QueryDict(request.body).dict()
		user_match = User.objects.get(pk=request_dict['userid'])
		user_match.delete()	

		return JsonResponse({'status': 'deleted user'})
	else: 
		return JsonResponse({'status': 400, 'data': 'User not authenticated'})




# CONFIRMATON THAT CATEGORIES WERE ADDED
@csrf_exempt 
# Just used to initially load categories into database
def populate_categories(request):
	categories=['music', 'food-and-drink', 'other', 'performing-arts', 'charities', 'festivals-fairs', 'sports-active-life', 'nightlife', 'visual-arts', 'kids-family', 'fashion', 'film', 'lectures-books']

	database_categories = Category.objects.all()
	database_categories.delete()

	for i in range(0, len(categories)):
		c = Category(name=categories[i])
		c.save()

	return JsonResponse({'status': 'Created Categories'})


@csrf_exempt 
def testing(request):
	print(request.user)


	return JsonResponse({'status': 200})


