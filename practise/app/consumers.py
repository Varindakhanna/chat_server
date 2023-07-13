#practise
from channels.consumer import SyncConsumer, AsyncConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync
from time import sleep
import asyncio
import json 
from .models import Chat,Group
from channels.db import database_sync_to_async

class MySyncConsumer(SyncConsumer):
  def websocket_connect(self, event):
    print('Websocket Connected...', event)
    print('channel_layer',self.channel_layer) # to get default channel layer of a project
    print('channel_name',self.channel_name) # to get default channel name of a project. new instance is created every time

    self.group_name=self.scope['url_route']['kwargs']['groupname']
    print("group name is ",self.group_name)
    
    async_to_sync(self.channel_layer.group_add)(
      self.group_name,  #grp name
      self.channel_name
      )
    #adding channel to the grp
    
    self.send({
      'type':'websocket.accept',
    })
  
  def websocket_receive(self, event):  #This method is called when a message is received from the client. 
                                       #It extracts the message data, processes it, and sends it back to the group using group_send.
                                       #  If the user is not authenticated, it sends a response indicating that login is required.
    print('Message received from Client', event['text'])
    print('type received from Client',type( event['text']))

    data=json.loads(event['text'])
    print("Data",data)
    print(self.scope['user'])

    #find group object
    group=Group.objects.get(name=self.group_name)

    if self.scope['user'].is_authenticated:   #making authentication compulsory
      #create new chat object
      chat=Chat(
        content=data['msg'],
        group=group
      )
      chat.save()

      async_to_sync(self.channel_layer.group_send)(self.group_name,{ #integrating that msg shd send to all channels in a grp
        'type':'chat.message',
        'message':event['text']
      })
    else:
      self.send({
        'type':'websocket.send',
        'text':json.dumps({"msg":"login required"}) #converting python to string dictionary
      })

  def chat_message(self,event):
      print('event ... ',event['message'])
      print('type of evnt',type(event['message']))
      self.send({                                           #sending msgs
        'type':'websocket.send',
        'text':event['message']
      })
   
    #from server to client
    # for i in range(10):
    #   self.send({
    #     'type':'websocket.send',
    #     'text': str(i)
    #   })
    #   sleep(1) #taki dheere dheere jaye

  def websocket_disconnect(self, event):
    print('Websocket Disconnected...', event)
    async_to_sync (self.channel_layer.group_discard)(self.group_name,self.channel_name) 
    raise StopConsumer()

class MyAsyncConsumer(AsyncConsumer):
  async def websocket_connect(self, event):
    print('Websocket Connected...', event)
    print('channel_layer',self.channel_layer) # to get default channel layer of a project
    print('channel_name',self.channel_name) # to get default channel name of a project. new instance is created every time

    self.group_name=self.scope['url_route']['kwargs']['groupname']
    print("group name is ",self.group_name)

    await self.channel_layer.group_add(
      self.group_name,  #grp name
      self.channel_name
      )
    #adding channel to the grp
    
    await self.send({
      'type':'websocket.accept',
    })
  
  async def websocket_receive(self, event):
    print('Message received from Client', event['text'])
    print('type received from Client',type( event['text']))

    data=json.loads(event['text'])
    print("Data",data)
    print(self.scope['user'])

    #find group object
    group=await database_sync_to_async(Group.objects.get)(name=self.group_name)

    if self.scope['user'].is_authenticated:
    #create new chat object
      chat=Chat(
        content=data['msg'],
        group=group
      )
      await database_sync_to_async(chat.save)()

      await self.channel_layer.group_send(self.group_name,{ #integrating that msg shd send to all channels in a grp
        'type':'chat.message',
        'message':event['text']
      })
    else:
       await self.send({
        'type':'websocket.send',
        'text':json.dumps({"msg":"login required"}) #converting python to string dictionary
      })


  async def chat_message(self,event):
      print('event ... ',event['message'])
      print('type of evnt',type(event['message']))
      await self.send({                                           #sending msgs
        'type':'websocket.send',
        'text':event['message']
      })
   
    #from server to client
    # for i in range(10):
    #   self.send({
    #     'type':'websocket.send',
    #     'text': str(i)
    #   })
    #   sleep(1) #taki dheere dheere jaye

  async def websocket_disconnect(self, event): 
    print('Websocket Disconnected...', event)
    await self.channel_layer.group_discard(self.group_name,self.channel_name) 
    raise StopConsumer()