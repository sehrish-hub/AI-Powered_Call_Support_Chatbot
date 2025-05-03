from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled, handoff
from dotenv import load_dotenv, find_dotenv
from openai.types.responses import ResponseTextDeltaEvent
import os
import asyncio
import speech_recognition as sr
import pyttsx3
import json
from datetime import datetime

# Load environment variables
load_dotenv(find_dotenv())
set_tracing_disabled(disabled=True)

class AICallChatbot:
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
        
    def setup_agents(self):
        """Set up specialized agents for different aspects of the chatbot"""
        
        # Customer Service Agent
        self.customer_service_agent = Agent(
            name="customer_service_agent",
            instructions="""You are a customer service agent specializing in handling customer inquiries.
            Your responsibilities include:
            1. Understanding customer needs and concerns
            2. Providing accurate and helpful responses in complete detailed 
            3. Maintaining a professional and friendly tone
            4. Escalating complex issues when necessary
            5. Following company policies and procedures
            6. Ensuring customer satisfaction
            
            Your responses should be:
            - Clear and concise
            - Empathetic and understanding
            - Solution-oriented
            - Professional yet friendly
            - Accurate and informative""",
            model=self.model,
        )
        
        # Technical Support Agent
        self.technical_support_agent = Agent(
            name="technical_support_agent",
            instructions="""You are a technical support agent specializing in resolving technical issues.
            Your responsibilities include:
            1. Diagnosing technical problems
            2. Providing step-by-step solutions
            3. Explaining technical concepts in simple terms
            4. Troubleshooting common issues
            5. Escalating complex technical problems
            6. Following security protocols
            
            Your responses should be:
            - Technical yet understandable
            - Methodical and systematic
            - Solution-focused
            - Clear and precise
            - Safety-conscious""",
            model=self.model,
        )
        
        # Main Chatbot Agent
        self.chatbot_agent = Agent(
            name="chatbot_agent",
            instructions="""You are the main AI chatbot coordinating customer interactions.
            Your responsibilities include:
            1. Understanding the context of customer queries
            2. Routing queries to appropriate specialized agents
            3. Maintaining conversation flow
            4. Ensuring natural and engaging interactions
            5. Handling conversation transitions
            6. Managing escalation procedures
            
            Your responses should be:
            - Natural and conversational
            - Context-aware
            - Professional and helpful
            - Clear and concise
            - Engaging and friendly""",
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
    
    async def process_voice_input(self):
        """Process voice input from the user"""
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
    
    def speak_response(self, text):
        """Convert text response to speech"""
        self.engine.say(text)
        self.engine.runAndWait()
    
    async def handle_conversation(self):
        """Main conversation loop"""
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
    
    def save_conversation_history(self):
        """Save conversation history to a file"""
        with open('conversation_history.json', 'w') as f:
            json.dump(self.conversation_history, f, indent=2)

async def main():
    chatbot = AICallChatbot()
    await chatbot.handle_conversation()

if __name__ == "__main__":
    asyncio.run(main()) 


#     AI Chatbot Developer for Call Support

# We are seeking an experienced developer to create an AI-powered chatbot capable of handling call interactions. The ideal candidate will have expertise in natural language processing and machine learning to ensure a seamless user experience. The chatbot should be able to understand and respond to customer inquiries effectively. If you possess a strong background in AI development and are passionate about enhancing customer support through innovative technology, we would love to hear from you.

# Skills and Expertise
# Chatbot Development
# Natural Language Processing
# Artificial Intelligence
# Python
# IBM Watson

# Tech & IT
# Individual client




# Here are the types of questions you can ask the AI chatbot, categorized by different areas:
# Customer Service Questions:
# "How do I create a new account?"
# "How can I reset my password?"
# "What are your business hours?"
# "How do I check my bill?"
# "What is your refund policy?"
# "How do I register a complaint?"
# "How do I update my contact information?"
# "What are your service terms and conditions?"
# Technical Support Questions:
# "How do I fix my internet connection?"
# "How do I update the application?"
# "I'm having login issues, how can I resolve them?"
# "The website is running slow, how can I fix it?"
# "What does this error message mean?"
# "What are the system requirements?"
# "How do I troubleshoot connection problems?"
# "How do I clear my cache and cookies?"
# Account Management Questions:
# "How do I change my account settings?"
# "How can I update my profile information?"
# "How do I manage my subscription?"
# "How do I add a new payment method?"
# "How can I improve my account security?"
# "How do I change my notification preferences?"
# "How do I delete my account?"
# "How do I export my data?"
# Product/Service Information Questions:
# "What are the new features?"
# "What are the pricing plans?"
# "What is the service coverage area?"
# "What are the product specifications?"
# "What is the warranty information?"
# "What are the available payment methods?"
# "What are the service limitations?"
# "What are the supported devices?"
# Troubleshooting Questions:
# "How do I fix app crashes?"
# "How do I resolve loading issues?"
# "What does this error code mean?"
# "How do I fix performance issues?"
# "How do I resolve compatibility problems?"
# "How do I fix audio/video issues?"
# "How do I recover lost data?"
# "How do I fix synchronization problems?"
# General Information Questions:
# "What are the company policies?"
# "What is the contact information?"
# "What support options are available?"
# "Where can I find FAQs?"
# "Where can I download documentation?"
# "What are the office locations?"
# "What are the support hours?"
# "How do I request a callback?"
# You can ask these questions:
# Using voice (through microphone)
# Using text (typing)
# In English
# In Urdu/Roman Urdu
# In a mix of languages
# The chatbot will:
# Understand your question
# Route it to the appropriate agent
# Provide a detailed response
# Speak the response back to you
# Save the conversation history
# Would you like to try asking any specific question from these categories? I can help you test the chatbot with a sample question!

# Proposal: AI-Powered Call Support Chatbot Development
# Hello,
# I am excited to submit my proposal for your project seeking an AI Chatbot Developer for Call Support. I have hands-on experience in building advanced AI chatbots that handle real-time voice interactions, leveraging the latest in Natural Language Processing (NLP) and Artificial Intelligence (AI).
# Project Overview
# I have developed a robust AI-powered chatbot system that can:
# Listen to users via voice input (using SpeechRecognition)
# Understand and process natural language queries (using OpenAI/Gemini APIs)
# Respond with human-like synthesized speech (using pyttsx3)
# Handle both customer service and technical support queries through specialized agents
# Maintain conversation history for context-aware and seamless interactions
# Technical Highlights
# Python-based implementation for flexibility and easy integration
# Modular agent architecture: Separate agents for customer service and technical support, coordinated by a main chatbot agent
# Voice-to-text and text-to-voice pipeline for natural, call-like user experience
# OpenAI/Gemini integration for state-of-the-art NLP and AI responses
# Easily extendable: Can integrate with other AI providers (such as IBM Watson) if required by your business
# Skills & Expertise
# Chatbot Development
# Natural Language Processing (NLP)
# Artificial Intelligence (AI)
# Python Programming
# Voice Recognition and Text-to-Speech
# API Integration (OpenAI, Gemini, IBM Watson on request)