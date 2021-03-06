from urllib import response
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from .serializers import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_201_CREATED
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication

# Create your views here.
class Signup(APIView):
    # permission_classes = (IsAdminUser,)
    def post(self, request):
        fname = request.data.get('fname')
        lname = request.data.get('lname')
        uname = request.data.get('uname')
        email = request.data.get('email')
        try:
            user = User.objects.get(username=uname)
            return Response({"message": "Username already exits"}, HTTP_200_OK)
        except:
            pass
        pwd = request.data.get('pwd')
        user = User.objects.create(username=uname, first_name=fname, last_name=lname, email=email)
        user.set_password(pwd)
        user.save()
        Customer.objects.create(user=user, email=email)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'key': token.key},
                        status=HTTP_200_OK)


class Login(APIView):

    def post(self, request):
        # uname = request.data.get('uname')
        email = request.data.get('email')
        pwd = request.data.get('pwd')
        username = User.objects.get(email=email.lower()).username
        user = authenticate(username=username, password=pwd)
        # cust = Customer.objects.get(user=user)

        if email is None or pwd is None:
            return Response({'error': 'Please provide both username and password'}, status=HTTP_400_BAD_REQUEST)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'key': token.key},
                            status=HTTP_200_OK)
        else:
            return Response({'error': 'That user is not exist. Please sign up.'}, status=HTTP_404_NOT_FOUND)


class Admin_login(APIView):

    def post(self, request):
        uname = request.data.get('uname')
        pwd = request.data.get('pwd')
        user = authenticate(username=uname, password=pwd)
        if user.is_staff:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'key': token.key},
                            status=HTTP_200_OK)
        else:
            return Response({"error": "User is not an admin"},
                            status=HTTP_200_OK)

class BusinessView(APIView):
    serializer_class = BusinessSerializer
    # permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        pro = Business.objects.all()

        serializer = self.serializer_class(pro, many=True).data
        return Response(serializer, HTTP_200_OK)

class ServiceView(APIView):
    serializer_class = ServiceSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        pro = Service.objects.all()
        serializer = self.serializer_class(pro, many=True).data
        return Response(serializer, HTTP_200_OK)

class CustomerView(APIView):
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]
    authentication_classes = (TokenAuthentication,)

    def get(self,request):
        pro = Customer.objects.all()
        serializer = self.serializer_class(pro, many = True).data
        return Response(serializer, HTTP_200_OK)

class AppointmentClientView(APIView):
    serializer_class = AppointmentSerializer
    # permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        user = User.objects.get(username=request.user)
        customer = Customer.objects.get(user=user)
        date = request.data.get('date')
        pro = Appointment.objects.filter(customer = customer.id, status='confirmed', date=date)
        serializer = self.serializer_class(pro, many = True).data
        return Response(serializer, HTTP_200_OK)

class AppointmentBusinessView(APIView):
    serializer_class = AppointmentSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        user = User.objects.get(username=request.user)
        business = Business.objects.get(user=user)
        date = request.data.get('date')
        pro = Appointment.objects.filter(business = business.name, date = date)
        serializer = self.serializer_class(pro, many=True).data
        return Response(serializer, HTTP_200_OK)

class AddAppointment(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        user = User.objects.get(username=request.user)
        customer = Customer.objects.get(user=user)
        # paid = request.data.get('booking')
        business_name = request.data.get("business")
        business = Business.objects.get(name = business_name)
        service = business.service
        date = request.data.get('date')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        status = ""
        appointments = Appointment.objects.filter(date=date)
        for appointment in appointments:
            if (start_time >= appointment.start_time & start_time <= appointment.end_time) | (end_time >= appointment.start_time & end_time <= appointment.end_time):
                return Response({'message': 'That time slot is already appointed'}, status=HTTP_400_BAD_REQUEST)
                break
        Appointment.objects.create(service=service, customer=customer, business=business, status=status, date=date, start_time=start_time, end_time=end_time)
        return Response({"message": "Appointment create successfully. Please wait until business accept it."}, status=HTTP_201_CREATED)

def deleteAppointment(request, id):
    Appointment.objects.filter(id=id).delete()
    return Response({'message': "Your appointment is canceled"}, status=HTTP_200_OK)    

class RUDAppointment(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    serializer_class = AppointmentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Appointment.objects.all()

class ConfirmedAppointment(APIView):
    serializer_class = AppointmentSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        user = User.objects.get(username=request.user)
        customer = Customer.objects.get(user=user)
        pro = Appointment.objects.filter(customer=customer.user.username, status = 'confirmed')
        serializer = self.serializer_class(pro, many=True).data
        return Response(serializer, HTTP_200_OK)
