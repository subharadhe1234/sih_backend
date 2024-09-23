from django.db import models
from django.utils import timezone
import uuid



# # class ExampleModel(models.Model):
# #     username = models.CharField(max_length=100)
# #     email = models.EmailField()



# class CustomUser(AbstractUser):
#     ROLE_CHOICES = [
#     ('faculty', 'Faculty'),
#     ('hod', 'HOD'),
#     ('dean', 'Dean'),
#     ('vc', 'VC'),
#     ]
    
#     email=models.EmailField(unique=True)
#     role=models.CharField(max_length=20,choices=ROLE_CHOICES)
#     university = models.CharField(max_length=255)
#     orchid_id = models.CharField(max_length=100, unique=True)
#     is_approved = models.BooleanField(default=False)


#     REQUIRED_FIELDS = ['email', 'role', 'university', 'orchid_id']

#     def __str__(self):
#         return f"{self.username} ({self.university}) - {self.role}"
    


# class Approval(models.Model):
#     user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
#     approved_by = models.ForeignKey(CustomUser,related_name='approvals',on_delete=models.CASCADE)
#     is_approved = models.BooleanField(default=False)
#     timestamp = models.DateTimeField(auto_now_add=True)



class CustomModel(models.Model):
    user_id=models.TextField(null=True,blank= True)
    orkid_id = models.CharField(max_length=150)
    email = models.EmailField(unique= True)
    role = models.CharField(max_length=20)
    password=models.CharField(max_length=10)
    
    public_key = models.TextField(null=True, blank=True)
    encrypted_private_key = models.BinaryField(null=True, blank=True)
    registration_status = models.CharField(max_length=20, default='Pending')
    is_approved = models.BooleanField(default=False)

    class Meta:
    # REQUIRED_FIELDS = ['orkid_id', 'email', 'role'] 
        unique_together = ('orkid_id', 'email', 'role')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['orkid_id', 'role']

    def __str__(self):
        return f'{self.orkid_id}-{self.email}-{self.role}'
    
    # @property
    def set_user_id(self):
        # Custom user ID: "ORKID-EMAIL-ROLE"
        self.user_id = f'{self.orkid_id}-{self.email}-{self.role}'
        # return f'{self.orkid_id}-{self.email}-{self.role}'
    

    @property
    def is_anonymous(self):
        """Always return False. CustomUser cannot be anonymous."""
        return False

    @property
    def is_authenticated(self):
        """Always return True. CustomUser is always authenticated."""
        return True
    



class Token(models.Model):

    user=models.OneToOneField(CustomModel,on_delete=models.CASCADE)
    key=models.CharField(max_length=256,unique=True)
    created_at=models.DateTimeField(default=timezone.now)

    def genrate_key(self):
        """Generates a new key for the token."""
        self.key=uuid.uuid4().hex
    @staticmethod
    def verify_token(key):
        """Verify if the token exists and is valid."""
        try:
            token = Token.objects.get(key=key)
            return token.user
        except Token.DoesNotExist:
            return None
