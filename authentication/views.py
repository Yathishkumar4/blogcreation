from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from blogadmin import settings
from django.core.mail import EmailMessage, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_text
from . tokens import generate_token

def index(request):
  return render(request,'authentication/index.html')

def signup(request):

  if request.method == "POST":
    # username = request.POST.get('username')
    username = request.POST['username']
    fname = request.POST['fname']
    lname = request.POST['lname']
    email = request.POST['email']
    password1 = request.POST['password1']
    password2 = request.POST['password2']

    if User.objects.filter(username=username):
      messages.error(request,"Username already exit! Please try some other username")
      return redirect('index')

    if User.objects.filter(email=email).exists():
      messages.error(request,"email already exit! Please try some other email")
      return redirect('index')
    
    if len(username)>20:
      messages.error(request,"Username must be less than 10 characters")
      return redirect('index')

    if password1 != password2:
      messages.error(request,"password didn't match!")
      return redirect('index')

    if not username.isalnum():
      messages.error(request,"Username must be Alpha-Numaric")
      return redirect('index')

    
    myuser = User.objects.create_user(username, email, password1)
    myuser.first_name = fname
    myuser.last_name =lname
    myuser.is_active =False
    myuser.save()

    messages.success(request,"Your Account has been successfully created.We have sent a conformation email,plz conform your account to activate.")
    
    subject = "Welcom to Blog -Post Creation login"
    message = "Hello" + myuser.first_name + "!! \n" + "welcome to Post Creation blog \n the mail as been sent mail id plz comform the mail address in order to activate your account"
    from_email = settings.EMAIL_HOST_USER
    to_list =[myuser.email]
    send_mail(subject,message, from_email, to_list, fail_silently=True)

    #Email Address Conformation

    current_site = get_current_site(request)
    email_subject ="confirm your email @ blog - login"
    message2 = render_to_string('email_confirmation.html',{
      'name': myuser.first_name,
      'domain': current_site.domain,
      'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
      'token': generate_token.make_token(myuser),
    })
    email = EmailMessage(
      email_subject,
      message2,
      settings.EMAIL_HOST_USER,
      [myuser.email],
    )
    email.fail_silently= True
    email.send()

    return redirect('signin')

  return render(request, 'authentication/signup.html')

def signin(request):

  if request.method == "POST":
    username = request.POST['username']
    password1 = request.POST['password1']

    user = authenticate(username=username,password=password1)

    if user is not None:
      login(request, user)
      fname = user.first_name   
      return render(request,"authentication/index.html",{'fname': fname})

    else:
      messages.error(request,"invalid details")
      return redirect('index')



  return render(request, 'authentication/signin.html')

def signout(request):
  logout(request)
  messages.success(request,"Logged Out Successfully")
  return redirect('index')

def activate(request, uifb64, token):
  try:
    uid = force_text(urlsafe_base64_encode(uidb64))
    myuser = User.objects.get(pk=uid)
  except (TypeError, ValueError, OverflowError, User.DoesNotExit):
    myuser = None

  if myuser is not None and generate_token.check_token(myuser,token):
    myuser.is_active =True
    myuser.save()
    login(request, myuser)
    return redirect('index')
  else:
    return render(request,'activation_faild.html')
  # Create your views here