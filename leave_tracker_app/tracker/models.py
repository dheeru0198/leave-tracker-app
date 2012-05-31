from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.db.models.signals import post_save
from django.core.mail import send_mail

LEAVE_CONST = 20

class Leave(models.Model):

    type_of_leave = models.CharField(max_length=20)
    number_fo_days = models.IntegerField(max_length=10)

    def __unicode__(self):
        return self.type_of_leave

    
class UserProfile(models.Model):

    user = models.OneToOneField(User)
    leaves_taken = models.PositiveIntegerField(max_length=10)
    total_leaves = models.PositiveIntegerField(max_length=10)
    
    def __unicode__(self):
        return self.user.username

def create_user_profile(sender, **kwargs):
    instance = kwargs["instance"]
    if kwargs["created"]:
        UserProfile.objects.create(user=instance, 
                                   leaves_taken = 0, 
                                   total_leaves = LEAVE_CONST)

post_save.connect(create_user_profile, sender=User)    
        
class LeaveApplication(models.Model):

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    usr = models.ForeignKey(UserProfile)
    leave = models.ForeignKey(Leave)
    status = models.BooleanField()
    subject = models.TextField()
    
    def __unicode__(self):
        return "%s %s" %(self.usr, self.start_date)

    
def send_approval_mail(sender, **kwargs):
    instance = kwargs["instance"]
    recipients = list(User.objects.filter(is_superuser=True).values_list('email', flat=True))
    subject = "Leave Modified"
    if kwargs["created"]:
        subject = "Leave Created"
    if instance.status == True:
        subject = 'Leave Approved'
        recipients.append(instance.usr.user.email)
    send_mail(subject, instance.subject, 'leave@agiliq.com',
                  recipients, fail_silently=False)
    
post_save.connect(send_approval_mail, sender=LeaveApplication)

