1. Imports
(from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled, handoff
from dotenv import load_dotenv, find_dotenv
from openai.types.responses import ResponseTextDeltaEvent
import os
import asyncio
import speech_recognition as sr
import pyttsx3
import json
from datetime import datetime)
agents: Custom or SDK classes for agent-based AI workflows.
dotenv: Loads environment variables from a .env file.
openai.types.responses: For handling streamed response events.
os, asyncio, json, datetime: Standard Python libraries.
speech_recognition: For converting speech to text.
pyttsx3: For converting text to speech.
2. Environment Setup
(load_dotenv(find_dotenv())
set_tracing_disabled(disabled=True))
Loads environment variables (like API keys) from a .env file.
Disables tracing/logging for the agent SDK.
3. Main Chatbot Class
Class Definition
class AICallChatbot:
Defines the main chatbot class.
Initialization
def __init__(self):
    # Initialize OpenAI provider
    self.provider = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    
    # Initialize the model
    self.model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=self.provider,
    )
    
    # Initialize speech recognition
    self.recognizer = sr.Recognizer()
    
    # Initialize text-to-speech
    self.engine = pyttsx3.init()
    
    # Set up specialized agents
    self.setup_agents()
    
    # Initialize conversation history
    self.conversation_history = []
    OpenAI Provider: Sets up the connection to Gemini/OpenAI API using your API key.
Model: Sets up the chat model (here, "gemini-2.0-flash").
Speech Recognition: Prepares to listen to the user's voice.
Text-to-Speech: Prepares to speak responses.
Agents: Calls a method to set up specialized agents (see below).
Conversation History: Initializes an empty list to store the conversation.

Setting Up Specialized Agents
def setup_agents(self):
    # Customer Service Agent
    self.customer_service_agent = Agent(
        name="customer_service_agent",
        instructions="""...""",
        model=self.model,
    )
    
    # Technical Support Agent
    self.technical_support_agent = Agent(
        name="technical_support_agent",
        instructions="""...""",
        model=self.model,
    )
    
    # Main Chatbot Agent
    self.chatbot_agent = Agent(
        name="chatbot_agent",
        instructions="""...""",
        model=self.model,
        tools=[
            self.customer_service_agent.as_tool(
                tool_name="delegate_to_customer_service",
                tool_description="Delegate customer service related queries to the customer service agent"
            ),
            self.technical_support_agent.as_tool(
                tool_name="delegate_to_technical_support",
                tool_description="Delegate technical support queries to the technical support agent"
            )
        ]
    )
    Customer Service Agent: Handles general customer queries.
Technical Support Agent: Handles technical issues.
Main Chatbot Agent: Coordinates the conversation, decides when to delegate to the other agents using tools.

Voice Input Processing
async def process_voice_input(self):
    with sr.Microphone() as source:
        print("Listening...")
        self.recognizer.adjust_for_ambient_noise(source)
        audio = self.recognizer.listen(source)
        
        try:
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None
            Listens to the user's voice using the microphone.
Converts speech to text using Google’s speech recognition.
Handles errors if speech is not recognized or if there’s a request error.

Text-to-Speech Output
def speak_response(self, text):
    self.engine.say(text)
    self.engine.runAndWait()
    Converts the chatbot’s text response to speech and plays it aloud.

Main Conversation Loop
async def handle_conversation(self):
    print("Welcome to the AI Call Chatbot! How can I help you today?")
    self.speak_response("Welcome to the AI Call Chatbot! How can I help you today?")
    
    while True:
        # Get user input (voice or text)
        user_input = await self.process_voice_input()
        if not user_input:
            continue
        
        if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
            print("Goodbye! Have a great day!")
            self.speak_response("Goodbye! Have a great day!")
            break
        
        # Add user input to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Build conversation prompt
        prompt = "".join([
            f"{turn['role'].title()}: {turn['content']}\n"
            for turn in self.conversation_history
        ]) + "Assistant: "
        
        # Get response from chatbot
        result = Runner.run_streamed(starting_agent=self.chatbot_agent, input=prompt)
        
        full_response = ""
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                print(event.data.delta, end="", flush=True)
                full_response += event.data.delta
        
        print("\n")
        
        # Add assistant response to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": full_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Speak the response
        self.speak_response(full_response)
        
        # Save conversation history
        self.save_conversation_history()
        Greets the user and starts the conversation.
Listens for user input (voice).
Checks for exit commands (like "bye", "quit").
Stores each user and assistant message in the conversation history.
Builds a prompt from the conversation history for context.
Gets a streamed response from the chatbot agent and prints it as it comes in.
Speaks the response aloud.
Saves the conversation history to a file after each turn.

Saving Conversation History
    with open('conversation_history.json', 'w') as f:
Saves the entire conversation to a JSON file for record-keeping or future analysis.

4. Main Function and Script Entry Point
async def main():
    chatbot = AICallChatbot()
    await chatbot.handle_conversation()

if __name__ == "__main__":
    asyncio.run(main())
    main(): Creates an instance of the chatbot and starts the conversation loop.
if _name_ == "_main_":: Ensures the chatbot runs when the script is executed directly.
Summary
This code creates a voice-based AI chatbot that can handle both customer service and technical support queries.
It uses advanced AI models (OpenAI/Gemini) for natural language understanding and response.
It interacts with users via voice, making it suitable for call support scenarios.
It keeps a record of the conversation and is modular for easy extension.