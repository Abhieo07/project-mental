from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import openai

from django.contrib import auth
from .models import Chat,CustomUser,Profile

from django.utils import timezone

openai_api_key = "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"
openai.api_key = openai_api_key

def ask_openai(message):
    text = " you are my therapist and response accordingly to this and dont use any acknowledgment like certnaily,ofcource,just aact like professional"
    response = openai.Completion.create(
        model = "text-davinci-003",
        prompt = message+text,
        max_tokens = 50,
        n = 1,
        stop = None,
        temperature = 0.7,
    )
    # print(response)
    answer = response.choices[0].text.strip()
    return answer

# create to ask ai to analysis the conversation
def get_analysis(chats):
    conversation_list = []
    for chat in chats:
        conversation_list.append(chat.message)
        conversation_list.append("Therapist: "+chat.response)

    str = "you are a proffessional therapist and analyse the above therapist-client interaction and generate a good report for this too. \n"
    mystr = "\n".join(conversation_list)

    prompt = mystr + "\n" + str

    response = openai.Completion.create(
        model = "text-davinci-003",
        prompt = prompt,
        max_tokens = 50,
        n = 1,
        stop = None,
        temperature = 0.7,
    )
    answer = response.choices[0].text.strip()

    return answer

# Create your views here.
@login_required(login_url='login')
def main(request):
    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)

        chat = Chat.objects.create(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()

        return JsonResponse({'message': message, 'response':response})
    return render(request, 'chat.html',{'chats':chats, 'user':request.user })

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(request, email=email, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('main')
        else:
            error_message = 'Invalid email or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = CustomUser.objects.create_user(email=email, password=password1, first_name=first_name, last_name=last_name)
                user.save()
                user_login = auth.authenticate(request, email=email,password=password1)
                auth.login(request, user_login)

                #create a Profile object for the new user
                user_model = CustomUser.objects.get(email = email)
                new_profile = Profile.objects.create(user=user_model)
                new_profile.save()
                return redirect('setting')
            except:
                error_message = 'Error creating account '
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = "Password don't match"
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

@login_required(login_url='login')
def profile(request):
    chats = Chat.objects.filter(user = request.user)
    user_profile = Profile.objects.get(user = request.user)
    
    if chats != []:
        report = get_analysis(chats)
    else:
        report = "You don't have enough intraction with therapist to get any analysis!"
    # chats.condtition = context #condition will be added to this after analysis of chats
    return render(request,'profile.html',{
        'profile':user_profile,
        'analysis':report
    })

@login_required(login_url='login')
def setting(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        try:
            if request.FILES.get('image') == None:
                image = user_profile.profileimg
                age = request.POST['age']
                sex = request.POST['sex']
                support_number = request.POST['support_number']

                user_profile.profileimg = image
                user_profile.age = age
                user_profile.sex = sex
                user_profile.support_number = support_number
                user_profile.save()
            if request.FILES.get('image') != None:
                image = request.FILES.get('image')
                age = request.POST['age']
                sex = request.POST['sex']
                support_number = request.POST['support_number']

                user_profile.profileimg = image
                user_profile.age = age
                user_profile.sex = sex
                user_profile.support_number = support_number
                user_profile.save()
            
            return redirect('main')
        except:
            error_message = 'Oops there is some error! make sure to enter correct details'
            return render(request, 'setting.html', {'error_message': error_message})

    return render(request, 'setting.html', {'user_profile': user_profile})

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')