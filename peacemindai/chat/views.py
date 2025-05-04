from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .utils import initialize_llm, load_documents, create_or_load_vector_db, setup_qa_chain
from .models import ChatMessage
from django.contrib import messages
import json

# Initialize the chatbot components
llm = initialize_llm()
docs = load_documents()
vector_db = create_or_load_vector_db(docs)
qa_chain = setup_qa_chain(vector_db, llm)

@login_required(login_url='login')
def lobby(request):
    # Get chat history for the user
    chat_history = ChatMessage.objects.filter(user=request.user).order_by('-timestamp')[:50]
    return render(request, 'chat/lobby.html', {'chat_history': chat_history})

@login_required(login_url='login')
def chat_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            
            if not user_message.strip():
                messages.warning(request, "Please enter a message.")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Message cannot be empty'
                }, status=400)
            
            # Get response from the chatbot
            response = qa_chain.run(user_message)
            
            # Save the chat message and response
            chat_message = ChatMessage.objects.create(
                user=request.user,
                message=user_message,
                response=response
            )
            
            return JsonResponse({
                'status': 'success',
                'response': response,
                'timestamp': chat_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
            
        except Exception as e:
            messages.error(request, "An error occurred while processing your message. Please try again.")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)