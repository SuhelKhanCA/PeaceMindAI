import json
from channels.generic.websocket import WebsocketConsumer
from . import utils
from .models import ChatMessage
import asyncio
import traceback
from django.core.cache import cache
from datetime import datetime, timedelta
from langchain.memory import ConversationBufferMemory

class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = None
        self.qa_chain = None
        self.initialization_error = None
        self.memory = None

    def initialize_components(self):
        """Initialize LLM components if not already initialized"""
        if self.llm is None:
            try:
                print("Initializing ChatConsumer components...")
                self.llm = utils.initialize_llm()
                self.docs = utils.load_documents()
                self.vector_db = utils.create_or_load_vector_db(self.docs)
                
                # Initialize memory for this user
                user_id = self.scope["user"].id
                self.memory = ConversationBufferMemory(
                    memory_key="chat_history",
                    return_messages=True
                )
                
                # Load previous chat history from database
                previous_messages = ChatMessage.objects.filter(
                    user=self.scope["user"]
                ).order_by('timestamp')[:50]  # Get last 50 messages
                
                for msg in previous_messages:
                    self.memory.chat_memory.add_user_message(msg.message)
                    self.memory.chat_memory.add_ai_message(msg.response)
                
                self.qa_chain = utils.setup_qa_chain(self.vector_db, self.llm)
                print("ChatConsumer initialization successful")
                return True
            except Exception as e:
                print(f"Error initializing ChatConsumer: {str(e)}")
                print(traceback.format_exc())
                self.initialization_error = str(e)
                return False
        return True

    def connect(self):
        print(f"WebSocket connect attempt by user: {self.scope['user']}")
        if not self.scope["user"].is_authenticated:
            print("Unauthenticated connection attempt - closing")
            self.close()
            return

        self.accept()
        print("Connection accepted")

        # Initialize components after accepting the connection
        if not self.initialize_components():
            print(f"Connection accepted but closing due to initialization error: {self.initialization_error}")
            self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Sorry, the chat service is currently unavailable. Please try again later.'
            }))
            self.close()
            return

    def disconnect(self, close_code):
        print(f"WebSocket disconnected with code: {close_code}")
        pass

    def check_rate_limit(self):
        """Rate limit: 30 messages per 5 minutes per user"""
        user_id = self.scope["user"].id
        cache_key = f"chat_rate_limit_{user_id}"
        
        # Get the current timestamp
        now = datetime.now()
        
        # Get or create the list of timestamps for this user
        timestamps = cache.get(cache_key, [])
        
        # Remove timestamps older than 5 minutes
        cutoff = now - timedelta(minutes=5)
        timestamps = [ts for ts in timestamps if ts > cutoff]
        
        # Check if user has exceeded rate limit
        if len(timestamps) >= 30:
            print(f"Rate limit exceeded for user {user_id}")
            return False
        
        # Add current timestamp and update cache
        timestamps.append(now)
        cache.set(cache_key, timestamps, timeout=300)  # 5 minutes timeout
        return True

    def receive(self, text_data):
        print(f"Received message from user {self.scope['user'].id}")
        try:
            # Check rate limit
            if not self.check_rate_limit():
                print("Rate limit check failed")
                self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'You are sending messages too quickly. Please wait a few minutes and try again.'
                }))
                return

            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            print(f"Processing message: {message[:50]}...")  # Log first 50 chars of message

            # Get response from the AI
            try:
                print("Getting AI response...")
                response = self.qa_chain.run(message)
                print(f"AI response received: {response[:50]}...")  # Log first 50 chars of response
            except Exception as e:
                print(f"Error getting AI response: {str(e)}")
                print(traceback.format_exc())
                response = "I apologize, but I'm having trouble processing your message right now. Please try again."

            # Store the message in the database
            try:
                print("Storing message in database...")
                ChatMessage.objects.create(
                    user=self.scope["user"],
                    message=message,
                    response=response
                )
                print("Message stored successfully")
            except Exception as e:
                print(f"Error storing message: {str(e)}")
                print(traceback.format_exc())
                # Continue even if storage fails
                pass

            # Send message to WebSocket
            print("Sending response back to client")
            self.send(text_data=json.dumps({
                'type': 'chat',
                'message': response
            }))

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid message format'
            }))
        except KeyError as e:
            print(f"Key error: {str(e)}")
            self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message content missing'
            }))
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            print(traceback.format_exc())
            self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'An unexpected error occurred. Please try again.'
            }))