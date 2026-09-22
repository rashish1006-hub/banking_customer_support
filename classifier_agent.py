from typing import Dict, Any
import re
from config import Config

class ClassifierAgent:
    """
    Agent responsible for classifying user messages into:
    - Positive Feedback
    - Negative Feedback  
    - Query
    """
    
    def __init__(self):
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
        
        # Keywords and patterns for classification (fallback)
        self.positive_keywords = [
            'thank', 'thanks', 'great', 'excellent', 'amazing', 'wonderful',
            'appreciate', 'helpful', 'resolved', 'fixed', 'happy', 'satisfied',
            'love', 'awesome', 'perfect', 'brilliant', 'fantastic', 'good job',
            'well done', 'thanks for', 'thank you for', 'delighted', 'pleased'
        ]
        
        self.negative_keywords = [
            'issue', 'problem', 'error', 'failed', 'not working', 'broken',
            'complaint', 'disappointed', 'frustrated', 'angry', 'unhappy',
            'worst', 'terrible', 'poor', 'bad', 'slow', 'delay', 'late',
            'still not', 'has not', 'have not', 'did not', 'not received',
            'not arrived', 'not working', 'unable', 'cannot', 'can not',
            'has not arrived', 'have not arrived', 'still has not', 'still have not',
            'replacement', 'stuck', 'waiting', 'pending', 'no response'
        ]
        
        self.query_keywords = [
            'status', 'check', 'what is', 'how', 'when', 'where', 'why',
            'ticket', 'update', 'progress', 'information', 'tell me',
            'show me', 'can you', 'could you', 'would you', 'please check',
            'looking for', 'need to know', 'want to know'
        ]
    
    def classify_with_llm(self, message: str) -> Dict[str, Any]:
        """
        Classify the user message using LLM via OpenRouter.
        
        Args:
            message: The user's input message
            
        Returns:
            Dictionary containing classification and confidence
        """
        try:
            prompt = f"""
Classify the following customer message into one of these categories:
- positive_feedback: Customer expressing satisfaction, gratitude, or positive experience
- negative_feedback: Customer expressing dissatisfaction, complaints, or reporting issues
- query: Customer asking for information, status updates, or making inquiries

Customer message: "{message}"

Respond with only the classification (positive_feedback, negative_feedback, or query) and a confidence score between 0 and 1.
Format your response as: classification|confidence
Example: positive_feedback|0.95
"""
            
            response = self.llm_client.chat.completions.create(
                model=Config.OPENROUTER_MODEL,
                messages=[
                    {"role": "system", "content": "You are a customer service message classifier. Always respond in the format: classification|confidence"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=50
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse the response
            try:
                classification, confidence = result_text.split('|')
                classification = classification.strip().lower()
                confidence = float(confidence.strip())
                
                # Validate classification
                valid_classifications = ['positive_feedback', 'negative_feedback', 'query']
                if classification not in valid_classifications:
                    # Fallback to rule-based if invalid
                    return self.classify_with_rules(message)
                
                # Extract ticket number if present
                ticket_pattern = re.search(r'\b\d{6}\b', message)
                ticket_number = int(ticket_pattern.group()) if ticket_pattern else None
                
                return {
                    'classification': classification,
                    'confidence': confidence,
                    'scores': {'llm_based': True},
                    'ticket_number': ticket_number,
                    'method': 'llm'
                }
                
            except (ValueError, IndexError):
                # Fallback to rule-based if parsing fails
                return self.classify_with_rules(message)
                
        except Exception as e:
            print(f"LLM classification failed: {e}, falling back to rule-based")
            return self.classify_with_rules(message)
    
    def classify_with_rules(self, message: str) -> Dict[str, Any]:
        """
        Classify the user message using rule-based keyword matching (fallback).
        
        Args:
            message: The user's input message
            
        Returns:
            Dictionary containing classification and confidence
        """
        message_lower = message.lower()
        
        # Count keyword matches
        positive_score = sum(1 for keyword in self.positive_keywords if keyword in message_lower)
        negative_score = sum(1 for keyword in self.negative_keywords if keyword in message_lower)
        query_score = sum(1 for keyword in self.query_keywords if keyword in message_lower)
        
        # Check for ticket number pattern (6 digits)
        ticket_pattern = re.search(r'\b\d{6}\b', message)
        if ticket_pattern:
            query_score += 3  # Boost query score if ticket number is present
        
        # Determine classification based on scores
        scores = {
            'positive_feedback': positive_score,
            'negative_feedback': negative_score,
            'query': query_score
        }
        
        # Find the classification with highest score
        max_score = max(scores.values())
        
        if max_score == 0:
            # Default to query if no keywords match
            classification = 'query'
            confidence = 0.3
        else:
            classification = max(scores, key=scores.get)
            confidence = min(max_score / 3.0, 1.0)  # Normalize confidence
        
        # Special case: if message contains a ticket number, prioritize query
        # UNLESS there are strong negative feedback indicators
        if ticket_pattern and classification != 'query':
            if query_score > 0 and negative_score == 0:
                classification = 'query'
                confidence = 0.8
            elif negative_score > 0:
                # Keep as negative feedback even with ticket number
                confidence = max(confidence, 0.7)
        
        return {
            'classification': classification,
            'confidence': confidence,
            'scores': scores,
            'ticket_number': int(ticket_pattern.group()) if ticket_pattern else None,
            'method': 'rules'
        }
    
    def classify(self, message: str) -> Dict[str, Any]:
        """
        Classify the user message and return classification result.
        Uses LLM if configured, otherwise falls back to rule-based classification.
        
        Args:
            message: The user's input message
            
        Returns:
            Dictionary containing classification and confidence
        """
        if self.use_llm and self.llm_client:
            return self.classify_with_llm(message)
        else:
            return self.classify_with_rules(message)
    
    def route_to_agent(self, classification: str) -> str:
        """
        Determine which agent should handle the message based on classification.
        
        Args:
            classification: The classification result
            
        Returns:
            Name of the target agent
        """
        routing_map = {
            'positive_feedback': 'feedback_handler',
            'negative_feedback': 'feedback_handler',
            'query': 'query_handler'
        }
        return routing_map.get(classification, 'query_handler')
