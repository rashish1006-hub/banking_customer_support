from typing import Dict, Any, Optional
import re
from database import SupportDatabase
from config import Config

class QueryHandlerAgent:
    """
    Agent responsible for handling user queries about ticket status.
    - Extract ticket number from message
    - Query database for ticket status
    - Return formatted response with status
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
    
    def extract_ticket_number(self, message: str) -> Optional[int]:
        """
        Extract 6-digit ticket number from message.
        
        Args:
            message: The user's query message
            
        Returns:
            Ticket number if found, None otherwise
        """
        # Look for 6-digit numbers
        ticket_pattern = re.search(r'\b(\d{6})\b', message)
        if ticket_pattern:
            return int(ticket_pattern.group(1))
        return None
    
    def generate_query_response_with_llm(self, customer_name: str, message: str, ticket_info: Dict[str, Any]) -> str:
        """
        Generate personalized query response using LLM.
        
        Args:
            customer_name: Name of the customer
            message: The original query message
            ticket_info: Dictionary containing ticket information
            
        Returns:
            Personalized response with ticket status
        """
        try:
            prompt = f"""
Generate a personalized response for a customer asking about their ticket status.

Customer name: {customer_name}
Customer message: "{message}"
Ticket ID: {ticket_info['ticket_id']}
Ticket Status: {ticket_info['status']}
Classification: {ticket_info['classification']}

Requirements:
- Be helpful and informative
- Include the ticket number and current status
- Add context based on the status (e.g., if unresolved, mention team is working on it)
- Keep it concise (1-2 sentences)
- Professional and friendly tone
"""
            
            response = self.llm_client.chat.completions.create(
                model=Config.OPENROUTER_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful customer service agent. Generate informative, professional responses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"LLM response generation failed: {e}, using fallback")
            return self.generate_fallback_response(ticket_info)
    
    def generate_fallback_response(self, ticket_info: Dict[str, Any]) -> str:
        """Generate fallback response without LLM."""
        ticket_number = ticket_info['ticket_id']
        status = ticket_info['status']
        
        response = f"Your ticket #{ticket_number} is currently marked as: {status}."
        
        # Add additional context if available
        if status == 'Unresolved':
            response += " Our team is actively working on your issue."
        elif status == 'Resolved':
            response += " We hope this resolves your concern. Feel free to reach out if you need further assistance."
        
        return response
    
    def handle_query(self, customer_name: str, message: str, ticket_number: Optional[int] = None) -> Dict[str, Any]:
        """
        Handle query by checking ticket status in database.
        
        Args:
            customer_name: Name of the customer
            message: The original query message
            ticket_number: Optional ticket number (if not provided, will extract from message)
            
        Returns:
            Dictionary containing response and metadata
        """
        # Extract ticket number if not provided
        if ticket_number is None:
            ticket_number = self.extract_ticket_number(message)
        
        if ticket_number is None:
            return {
                'success': False,
                'response': f"I couldn't find a ticket number in your message. Please provide a valid 6-digit ticket number.",
                'ticket_found': False,
                'customer_name': customer_name,
                'original_message': message
            }
        
        # Query database for ticket status
        ticket_info = self.database.get_ticket_status(ticket_number)
        
        if ticket_info is None:
            return {
                'success': False,
                'response': f"Ticket #{ticket_number} not found in our system. Please verify the ticket number and try again.",
                'ticket_found': False,
                'ticket_id': ticket_number,
                'customer_name': customer_name,
                'original_message': message
            }
        
        # Generate response
        if self.use_llm and self.llm_client:
            response = self.generate_query_response_with_llm(customer_name, message, ticket_info)
        else:
            response = self.generate_fallback_response(ticket_info)
        
        return {
            'success': True,
            'response': response,
            'ticket_found': True,
            'ticket_id': ticket_number,
            'ticket_status': ticket_info['status'],
            'customer_name': customer_name,
            'original_message': message,
            'ticket_info': ticket_info
        }
    
    def process(self, customer_name: str, message: str) -> Dict[str, Any]:
        """
        Process query by extracting ticket number and checking status.
        
        Args:
            customer_name: Name of the customer
            message: The original query message
            
        Returns:
            Dictionary containing response and metadata
        """
        return self.handle_query(customer_name, message)
