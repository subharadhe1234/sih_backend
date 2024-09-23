from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
from firebase_admin import firestore,db,storage
from django.views.decorators.csrf import csrf_exempt
import jwt
from datetime import datetime
from django.contrib.auth.models import User,Group
from rest_framework import routers, serializers, viewsets,generics,status
# from .serializers import UserSerializer,ApprovalSerializer,CustomTokenObtainPairSerializer
from .models import CustomModel,Token
from rest_framework.response import Response
# Firebase Firestore client initialization
firestore_client = firestore.client()
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view
from .helper import *
@api_view(['POST'])
def registration(requrest):
    email=requrest.data.get('email')
    orkid_id=requrest.data.get('orkid_id')
    role=requrest.data.get('role')
    password=requrest.data.get('password')
    # user_id=

    # Check if a user with the same ORKID ID and role already exists
    if CustomModel.objects.filter(orkid_id=orkid_id,role=role,email=email).exists():
        return Response({'error':'A user with this ORKID ID, email, and role already exists.'},status=status.HTTP_400_BAD_REQUEST)

    

    # Create a new user with 'Pending' registration status
    user=CustomModel(
        
        orkid_id=orkid_id,
        email=email,
        role=role,
        password=password,
        registration_status='Pending',
        is_approved=False
        
        
    )
    user.set_user_id()
    user.save()


    # Notify higher authorities for approval
    notify_higher_authorities(user)


    return Response({
        'message': 'Registration submitted successfully. Awaiting approval.'
    }, status=status.HTTP_201_CREATED)




@api_view(['POST'])
def approve_registration(request):
    email=request.data.get('email')
    orkid_id=request.data.get('orkid_id')
    role=request.data.get('role')
    action = request.data.get('action')
    try:
        user=CustomModel.objects.get(orkid_id=orkid_id,role=role,email=email)
    
    except CustomModel.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # if user.is_approved :
    #     return Response({'error': 'user is alrady approved.'}, status=status.HTTP_400_BAD_REQUEST)

    # if authority approve the user 
    if action== 'approve':

        # genetate the public and privet key  
        public_key, private_key=generate_rsa_keys()

        # private key encriped by recover_key for storing 
        encrypt_private=encrypt_private_key(private_key,user.password.encode('utf-8'))

        # Update user record with the keys and change registration status
        user.public_key=public_key
        user.encrypted_private_key=encrypt_private
        user.registration_status= action
        user.is_approved= True
        user.save()

        # send private and recovary key the user

        send_private_key_to_user(user.email,private_key)

        private_key_en=private_key
        return Response({'message': f'User registration approved successfully. privetkey:{private_key_en}'}, status=status.HTTP_200_OK)
    elif action == 'reject':

        # Set user registration status as rejected
        user.registration_status= action
        user.save()
        return Response({'message': 'User registration rejected.'}, status=status.HTTP_200_OK)
    
    else:
        return Response({'error': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
def signup_view(request):
    user_id=request.data.get("user_id")
    private_key = request.data.get('private_key')
    try:
        user= CustomModel.objects.get(user_id=user_id)      
    except CustomModel.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if user.registration_status!='approve':
        return Response({'error': 'Registration not yet approved.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Verify private key and recovery key
    decrypt_private= decrypt_private_key(user.encrypted_private_key,user.password.encode('utf-8'))

    if(decrypt_private!=private_key):
        return Response({'error': 'Invalid private key or recovery key.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Finalize user registration
    # user.registration_status='Completed'
    user.save()
    token, created = Token.objects.get_or_create(user=user)
    print(token,created)
    if not created:
        token.genrate_key()
        token.save()
    return Response({'token': token.key}, status=status.HTTP_200_OK)




@api_view(['POST'])
def login_view(request):
    user_id=request.data.get("user_id")
    password = request.data.get('password')
    try:
        user= CustomModel.objects.get(user_id=user_id) 

    except CustomModel.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
    
    if user.password==password:
        token, created = Token.objects.get_or_create(user=user)
        if not created:
            token.genrate_key()
            token.save()

        return Response({'token': token.key
                        }, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'password is wrong'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_user_by_custom_id(request, user_id):
    # Example: user_id = "ORKID123-email@example.com-faculty"
    pass


@api_view(['POST'])
def recover_private_key_view(request):
    pass

@api_view(['POST'])
def access_data_view(request):
    pass

@api_view(['POST'])
def save_user_data_view(request):
    pass


# Simple index view
def index(request):
    return HttpResponse("radhe")

@api_view(['GET'])
@token_required
def home_view(request):
    return Response({'message': f'Welcome, {request.user.email}!'}, status=status.HTTP_200_OK)



@csrf_exempt  # Disable CSRF for this endpoint
def data_request(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        # doc_ref.document("krishna").set(data)  # Store data in Firestore under "krishna"
        # print(data)
        # users_ref = firestore_client.collection("users")
        # docs = users_ref.stream()
        # print(docs)
        # for doc in docs:
            # print(f"{doc.id} => {doc.to_dict()}")
        # realtime_db=db.reference("radhe").child("scores")
        # snapshot = realtime_db.order_by_value().get()   
        # for key, val in snapshot.items():
        #     print('The {0} dinosaur\'s score is {1}'.format(key, val))
        # print(snapshot)
        # print(request.GET)
        return JsonResponse({'result': data})
    
@csrf_exempt
def encription(requrest):
    if requrest.method == 'POST':
        data = json.loads(requrest.body.decode('utf-8'))
        secte_key="LKzLPry74GkbHoN_yBGon68lw2zdwexy6S7jcWjjPBoK16aoiNcpMTecoCPR1y9c "
        paylode={
            'user_id':'abc123',
            'username':"subhadip",
            'role':'user'
        }
        # tocken=jwt.encode(paylode,secte_key,algorithm='HS256')
        # print(tocken)
        tocken='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYWJjMTIzIiwidXNlcm5hbWUiOiJzdWJoYWRpcCIsInJvbGUiOiJ1c2VyIn0.hLZ5xmuZL0AmVYoAhqEwYsOLyEbnkp2m0vKaFUZSnxM'
        decode_paylode=jwt.decode(tocken,secte_key,algorithms=['HS256'])
        print(decode_paylode)
        return JsonResponse({'result': data})
