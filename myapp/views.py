from base64 import urlsafe_b64decode, urlsafe_b64encode
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from myproject import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from .tokens import generate_token
from django.core.mail import EmailMessage, send_mail
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from datetime import datetime
from .models import Books, Data
from django.contrib.auth.decorators import login_required

# Create your views here.

def home(request):
    book_list = Books.objects.all()
    return render(request,"home.html",{'book_list':book_list})

def contact(request):
    if request.user.is_authenticated: 
        return render(request,'contact.html')
    return redirect("signin")

def service(request):
    if request.user.is_authenticated: 
        return render(request,'service.html')
    return redirect("signin")

def signup(request):

    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        phone = request.POST['phone']
        dob = request.POST['dob']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request,"Username already exist! Please try some other username")
            return redirect('home')

        if User.objects.filter(email=email):
            messages.error(request,"Email alreay registered!")
            return redirect('home')
        
        if len(phone) != 10:
            messages.error(request,"Phone numbe must be 10 digits")
        
        if len(username)>10:
            messages.error(request,"Username must be under 10 characters")

        if pass1 !=pass2:
            messages.error(request,"Passwords didn't match!")

        if not username.isalnum():
            messages.error(request,"Username must be Alpha_Numeric!")
            return redirect('home')

        myuser = User.objects.create_user(username, email, pass1 )
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_activae = False
        myuser.save()

        mydata = Data(username=username,fname=fname,lname=lname,phone=phone,email=email)
        mydata.save()

        messages.success(request, "Your Account has been successfully created.\n Please check the email for comfirm your email id")

        #Welcome Email
        subject = "Welcome to Django Login!!"
        message = "Hello "+ myuser.first_name + "!! \n" + "Weclome to Django!! \n Thanlyou for visiting our website \n We have also sent you a confirmation email, Please comfirm your email address in order to activate your account. \n\n Thanking you\n Abhishek Kumar"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True )

        # #Email Address Confirmation
        current_site = get_current_site(request)
        email_subject = "Comfirm your email @ Django Login!!"
        message2 = render_to_string('email_confirmation.html',{
            'name':myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token':generate_token.make_token(myuser),
            })
        
        email = EmailMessage(
                email_subject,
                message2,
                settings.EMAIL_HOST_USER,
                [myuser.email],
        )

        email.fail_silently = True
        email.send()

        return redirect('signin')
    
    return render(request,"signup.html")

def signin(request):

    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name
            book_list = Books.objects.all()
            messages.success(request,'Login Successfull')
            return render(request,"index.html",{'fname':fname, 'book_list':book_list})
        else:
            messages.error(request,"User not found")
            return redirect('home')
                
    return render(request,"login.html")

def signout(request):
    logout(request)
    messages.success(request,"Logout out Successfully")
    return redirect('home')

# insert book data
@login_required
def insert_book(request):

    if request.method == 'POST':
        title = request.POST['title']
        author = request.POST['author']
        publication_date = request.POST['publication_date']
        ISBN = request.POST['ISBN']
        genre = request.POST['genre']
        language = request.POST['language']
        summary = request.POST['summary']

        user_data = Data.objects.get(username=request.user)

        myuser = Books(title=title, username=user_data, author=author, publication_date=publication_date, ISBN=ISBN, genre=genre,language=language,summary=summary)
        myuser.save()

        messages.success(request, "Successfully Insert")
        
    return render(request,"insert_book.html")

# Create book table
def book_list(request):
    books = Books.objects.all()
    return render(request, 'home', {'books': books})

# Mail verify
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        user = None

    if user is not None and generate_token.check_token(user,token):
        user.is_active = True
        user.save()
            # Redirect to a success page or login page
        login(request,user)
        messages.success(request, "Your Account has been activated!!")
        return redirect('signin')
    else:
            # Token is invalid
            return render(request, 'activation_failed.html')

# @login_required 
def req_send(request):
    if request.user.is_authenticated:  # Check if the user is logged in
        if request.method == 'POST':
            book_name = request.POST.get('book_name')  # Use get() to safely retrieve form data
            
            # Retrieve book details based on the book_name
            try:
                book = Books.objects.get(title=book_name)
                author = book.author
                owner_username = book.username
                
                # Retrieve user details based on the owner's username
                owner = Data.objects.get(username=owner_username)
                owner_first_name = owner.fname

                current_site = get_current_site(request)
                email_subject = "Request for Book"
                message = render_to_string('EmailRequestForBook.html', {
                    'myuser': owner,
                    'name': owner_first_name,
                    'title': book_name,
                    'author': author,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(request.user.pk)),
                    'token': generate_token.make_token(request.user),
                })

                email = EmailMessage(
                    email_subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [request.user.email],
                )

                email.fail_silently = True
                email.send()

                messages.success(request, "Request successfully sent")
                return redirect("home")
            except Books.DoesNotExist:
                messages.error(request, "Book not found.")
                return redirect("home")
            except Data.DoesNotExist:
                messages.error(request, "Owner not found.")
                return redirect("home")
        else:
            messages.error(request, "Invalid request")
            return redirect("signin")
    
    return redirect('signin')

def book_req(request, uidb64, token):
    
    uid = urlsafe_base64_decode(uidb64).decode()
    user = get_user_model().objects.get(pk=uid)
    if user.is_authenticated:
        fname = user.first_name
        email = user.email
            
        #Email Comfirmation
        subject = "Request for book!!"
        message = "Hello "+ fname + "!! \n" + "Book owner has successfully comfirm your request!"
        from_email = settings.EMAIL_HOST_USER
        to_list = [user.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True )

        # Redirect to a success page or login page
        messages.success(request, "Your request has been comfirm!!")
        return redirect('home')
    else:
            # Token is invalid
        return render(request, 'activation_failed.html')    