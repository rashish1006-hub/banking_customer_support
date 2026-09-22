from typing import Dict, Any
from database import SupportDatabase
from config import Config

class FeedbackHandlerAgent:
    """
    Agent responsible for handling feedback messages.
    - Positive Feedback: Generate personalized thank-you message
    - Negative Feedback: Create ticket and generate empathetic response
    """
    
    def __init__(self, database: SupportDatabase):
        self.database = database
        
        # Validate configuration
        Config.validate()
        
        # Initialize LLM client if configured
        self.use_llm = Config.USE_LLM
        self.llm_client = None
        if self.use_llm:
            try:
                self.llm_client = Config.get_openai_client()
            except Exception as e:
                print(f"Failed to initialize LLM client: {e}")
                self.use_llm = False
        
        # Fallback template responses
        self.positive_responses = [
            "Thank you for your kind words, {customer_name}! We're delighted to assist you.",
            "We appreciate your positive feedback, {customer_name}! It's our pleasure to help.",
            "Thanks for reaching out, {customer_name}! We're glad we could help resolve your issue.",
            "Your feedback means a lot to us, {customer_name}! Thank you for choosing our services.",
            "We're thrilled to hear that, {customer_name}! Thank you for your patience and trust."
        ]
        
        self.negative_responses = [
            "We apologize for the inconvenience, {customer_name}. A new ticket #{ticket_id} has been generated, and our team will follow up shortly.",
            "We're sorry to hear about your experience, {customer_name}. Ticket #{ticket_id} has been created and our support team will investigate this promptly.",
            "Thank you for bringing this to our attention, {customer_name}. We've created ticket #{ticket_id} and our team will work to resolve this issue.",
            "We understand your frustration, {customer_name}. A support ticket #{ticket_id} has been generated and we'll address this as a priority."
        ]
    
    def generate_positive_response_with_llm(self, customer_name: str, message: str) -> str:
        """
        Generate personalized thank-you message using LLM.
        
        Args:
            customer_name: Name of the customer
            message: The original feedback message
            
        Returns:
            Personalized thank-you message
        """
        try:
            prompt = f"""
Generate a warm, personalized thank-you message for a customer who provided positive feedback.

Customer name: {customer_name}
Customer message: "{message}"

Requirements:
- Be warm and appreciative
- Personalize with the customer's name
- Acknowledge their positive experience
- Keep it concise (1-2 sentences)
- Professional but friendly tone
"""
            
            response = self.llm_client.chat.completions.create(
                model=Config.OPENROUTER_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful customer service agent. Generate warm, personalized responses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"LLM response generation failed: {e}, using fallback")
            import random
            return random.choice(self.positive_responses).format(customer_name=customer_name)
    
    def generate_negative_response_with_llm(self, customer_name: str, message: str, ticket_id: int) -> str:
        """
        Generate empathetic response for negative feedback using LLM.
        
        Args:
            customer_name: Name of the customer
            message: The original feedback message
            ticket_id: The generated ticket ID
            
        Returns:
            Empathetic response with ticket information
        """
        try:
            prompt = f"""
Generate an empathetic response for a customer who provided negative feedback.

Customer name: {customer_name}
Customer message: "{message}"
Ticket ID: {ticket_id}

Requirements:
- Be empathetic and apologetic
- Acknowledge their frustration
- Include the ticket number
- Assure them of follow-up
- Keep it concise (1-2 sentences)
- Professional and caring tone
"""
            
            response = self.llm_client.chat.completions.create(
                model=Config.OPENROUTER_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful customer service agent. Generate empathetic, professional responses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"LLM response generation failed: {e}, using fallback")
            import random
            return random.choice(self.negative_responses).format(
                customer_name=customer_name,
                ticket_id=ticket_id
            )
    
    def handle_positive_feedback(self, customer_name: str, message: str) -> Dict[str, Any]:
        """
        Handle positive feedback by generating a personalized thank-you message.
        
        Args:
            customer_name: Name of the customer
            message: The original feedback message
            
        Returns:
            Dictionary containing response and metadata
        """
        if self.use_llm and self.llm_client:
            response = self.generate_positive_response_with_llm(customer_name, message)
        else:
            import random
            response = random.choice(self.positive_responses).format(customer_name=customer_name)
        
        return {
            'success': True,
            'response': response,
            'classification': 'positive_feedback',
            'ticket_created': False,
            'customer_name': customer_name,
            'original_message': message
        }
    
    def handle_negative_feedback(self, customer_name: str, message: str) -> Dict[str, Any]:
        """
        Handle negative feedback by creating a ticket and generating empathetic response.
        
        Args:
            customer_name: Name of the customer
            message: The original feedback message
            
        Returns:
            Dictionary containing response, ticket ID, and metadata
        """
        # Create a new ticket in the database
        ticket_id = self.database.create_ticket(
            customer_name=customer_name,
            message=message,
            classification='negative_feedback'
        )
        
        if self.use_llm and self.llm_client:
            response = self.generate_negative_response_with_llm(customer_name, message, ticket_id)
        else:
            import random
            response = random.choice(self.negative_responses).format(
                customer_name=customer_name,
                ticket_id=ticket_id
            )
        
        return {
            'success': True,
            'response': response,
            'classification': 'negative_feedback',
            'ticket_created': True,
            'ticket_id': ticket_id,
            'customer_name': customer_name,
            'original_message': message
        }
    
    def process(self, classification: str, customer_name: str, message: str) -> Dict[str, Any]:
        """
        Process feedback based on classification (positive or negative).
        
        Args:
            classification: Either 'positive_feedback' or 'negative_feedback'
            customer_name: Name of the customer
            message: The original message
            
        Returns:
            Dictionary containing response and metadata
        """
        if classification == 'positive_feedback':
            return self.handle_positive_feedback(customer_name, message)
        elif classification == 'negative_feedback':
            return self.handle_negative_feedback(customer_name, message)
        else:
            return {
                'success': False,
                'error': f'Unknown classification: {classification}',
                'response': 'I apologize, but I encountered an error processing your feedback.'
            }
