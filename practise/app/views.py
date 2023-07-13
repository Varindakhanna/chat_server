from django.shortcuts import render
from .models import Chat,Group
# Create your views here.
def index(request , group_name):
    print(group_name)
    group=Group.objects.filter(name=group_name).first() #checking if grp already exsits or not
    chats=[]
    if group:
        chats=Chat.objects.filter(group=group) #load previous chats
    else:
        group=Group(name=group_name)
        group.save()
    return render(request,'app/index.html', {'groupname':group_name , 'chats':chats}) #if yes send to index.html that displays your chats
    

