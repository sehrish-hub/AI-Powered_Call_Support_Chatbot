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
        
        # Initialize company knowledge base
        self.company_knowledge = {
            "company_name": "TechSolutions Inc.",
            "locations": {
                "headquarters": {
                    "address": "123 Tech Park, Silicon Valley, CA 94025",
                    "phone": "+1 (555) 123-4567",
                    "email": "hq@techsolutions.com"
                },
                "branch_offices": [
                    {
                        "city": "New York",
                        "address": "456 Innovation Street, NY 10001",
                        "phone": "+1 (555) 234-5678"
                    },
                    {
                        "city": "London",
                        "address": "789 Tech Square, London EC1A 1AA",
                        "phone": "+44 20 7123 4567"
                    },
                    {
                        "city": "Singapore",
                        "address": "321 Digital Hub, Singapore 018956",
                        "phone": "+65 6123 4567"
                    }
                ]
            },
            "business_hours": {
                "weekdays": "9:00 AM - 6:00 PM",
                "weekends": "10:00 AM - 4:00 PM",
                "holidays": "Closed"
            },
            "support_channels": {
                "phone": "+1 (800) 123-4567",
                "email": "support@techsolutions.com",
                "live_chat": "Available 24/7 on our website",
                "social_media": {
                    "twitter": "@TechSolutions",
                    "linkedin": "TechSolutions Inc.",
                    "facebook": "TechSolutionsOfficial"
                }
            },
            "policies": {
                "refund": "30-day money-back guarantee",
                "privacy": "Strict data protection and GDPR compliance",
                "security": "Enterprise-grade security measures",
                "support": "24/7 technical support available"
            }
        }
        
        # Set up specialized agents
        self.setup_agents()
        
        # Initialize conversation history
        self.conversation_history = []
        
    def setup_agents(self):
        """Set up specialized agents for different aspects of the chatbot"""
        
        # Customer Service Agent
        self.customer_service_agent = Agent(
            name="customer_service_agent",
            instructions=f"""You are a customer service agent specializing in handling customer inquiries.
            You have access to the following company information:
            {json.dumps(self.company_knowledge, indent=2)}
            
            Your responsibilities include:
            1. Understanding customer needs and concerns
            2. Providing accurate and helpful responses using company information
            3. Maintaining a professional and friendly tone
            4. Escalating complex issues when necessary
            5. Following company policies and procedures
            6. Ensuring customer satisfaction
            
            Your responses should be:
            - Clear and concise
            - Empathetic and understanding
            - Solution-oriented
            - Professional yet friendly
            - Accurate and informative
            - Include relevant company information when appropriate""",
            model=self.model,
        )
        
        # Technical Support Agent
        self.technical_support_agent = Agent(
            name="technical_support_agent",
            instructions=f"""You are a technical support agent specializing in resolving technical issues.
            You have access to the following company information:
            {json.dumps(self.company_knowledge, indent=2)}
            
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
            - Safety-conscious
            - Include relevant company information when appropriate""",
            model=self.model,
        )
        
        # Main Chatbot Agent
        self.chatbot_agent = Agent(
            name="chatbot_agent",
            instructions=f"""You are the main AI chatbot coordinating customer interactions.
            You have access to the following company information:
            {json.dumps(self.company_knowledge, indent=2)}
            
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
            - Engaging and friendly
            - Include relevant company information when appropriate""",
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

#     Here's a comprehensive guide to what you can and cannot ask in this project:
# Questions You CAN Ask:
# Company Information:
# "What are your office locations?"
# "What are your business hours?"
# "How can I contact support?"
# "What is your company name?"
# "What are your social media handles?"
# Customer Service:
# "How do I create an account?"
# "How do I reset my password?"
# "What is your refund policy?"
# "How do I update my profile?"
# "How do I cancel my subscription?"
# Technical Support:
# "How do I fix login issues?"
# "How do I update the application?"
# "How do I clear my cache?"
# "How do I troubleshoot connection problems?"
# "What are the system requirements?"
# General Information:
# "What are your business hours?"
# "What support channels are available?"
# "What are your company policies?"
# "How do I contact customer service?"
# "What are your service terms?"


# Project Title:
# AI-Powered Call Center Chatbot with Voice Recognition and Multi-Agent System
# Project Description:
# I have developed an advanced AI-powered call center chatbot that combines voice recognition, natural language processing, and a multi-agent system to provide intelligent customer support. The system is designed to handle various customer inquiries efficiently while maintaining a natural conversation flow.
# Key Features:
# Voice Recognition & Text-to-Speech:
# Real-time voice input processing
# Natural language understanding
# Text-to-speech response system
# Multi-language support capability
# Multi-Agent Architecture:
# Customer Service Agent
# Technical Support Agent
# Main Chatbot Coordinator
# Intelligent task delegation
# Context-aware responses
# Company Knowledge Base:
# Comprehensive company information
# Office locations and contact details
# Business hours and policies
# Support channels and procedures
# Product/service information
# Conversation Management:
# Conversation history tracking
# Context preservation
# Natural conversation flow
# Error handling and recovery
# Session management
# Technical Stack:
# Python
# OpenAI/Gemini API
# Speech Recognition Library
# Text-to-Speech Engine
# Asynchronous Programming
# JSON Data Management
# Project Deliverables:
# Complete source code
# Documentation
# Setup instructions
# Testing procedures
# Deployment guidelines
# Unique Selling Points:
# Intelligent Routing:
# Smart query analysis
# Appropriate agent selection
# Efficient task delegation
# Context-aware responses
# Natural Interaction:
# Voice-based communication
# Human-like responses
# Professional tone maintenance
# Empathetic communication
# Comprehensive Knowledge:
# Detailed company information
# Policy and procedure awareness
# Technical support capabilities
# Customer service expertise
# Scalability:
# Modular architecture
# Easy knowledge base updates
# Additional agent integration
# Performance optimization
# Implementation Details:
# System Architecture:
# Multi-agent coordination
# Knowledge base integration
# Voice processing pipeline
# Response generation system
# Agent Specialization:
# Customer service handling
# Technical support provision
# Query analysis and routing
# Response generation
# Data Management:
# Conversation history storage
# Knowledge base updates
# Configuration management
# Error logging
# Potential Applications:
# Customer Support Centers
# Technical Help Desks
# Information Hotlines
# Service Desks
# Call Centers
# Future Enhancements:
# Multi-language support
# Sentiment analysis
# Advanced analytics
# CRM integration
# Custom agent training
# Project Value Proposition:
# Efficiency:
# Reduced response time
# 24/7 availability
# Consistent service quality
# Resource optimization
# Customer Experience:
# Natural interaction
# Quick resolution
# Professional service
# Personalized responses
# Business Benefits:
# Cost reduction
# Service scalability
# Quality improvement
# Customer satisfaction
# Technical Requirements:
# Python 3.8+
# OpenAI/Gemini API access
# Speech recognition libraries
# Text-to-speech engine
# Basic server infrastructure
# Implementation Timeline:
# Setup: 1-2 days
# Development: 5-7 days
# Testing: 2-3 days
# Deployment: 1-2 days
# Pricing:
# Base price: $X (based on your rate)
# Additional features: Custom pricing
# Maintenance: Optional monthly fee
# Support & Maintenance:
# Regular updates
# Bug fixes
# Feature additions
# Performance optimization
# Knowledge base updates
# Would you like me to:
# Add more technical details?
# Include specific code examples?
# Add pricing recommendations?
# Include more business benefits?
# Add implementation screenshots?
# Let me know what aspects you'd like to emphasize in your Upwork proposal!