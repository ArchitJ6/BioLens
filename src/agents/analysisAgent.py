from datetime import datetime, timedelta
import streamlit as st
from agents import ModelManager

class AnalysisAgent:
    """
    Agent responsible for managing report analysis, rate limiting,
    and implementing in-context learning from previous analyses.
    
    This agent interacts with a model manager to generate report analysis while 
    considering rate limits. It stores previous analyses in a knowledge base 
    for future in-context learning, allowing more relevant and informed analysis.
    """

    def __init__(self):
        """
        Initializes the AnalysisAgent, setting up the model manager and session state variables.
        """
        self.model_manager = ModelManager()
        self._init_state()
        
    def _init_state(self):
        """
        Initializes session state variables for tracking analysis count, last analysis time,
        analysis limit, models used, and knowledge base for in-context learning.
        """
        if 'analysis_count' not in st.session_state:
            st.session_state.analysis_count = 0
        if 'last_analysis' not in st.session_state:
            st.session_state.last_analysis = datetime.now()
        if 'analysis_limit' not in st.session_state:
            st.session_state.analysis_limit = 15
        if 'models_used' not in st.session_state:
            st.session_state.models_used = {}
        if 'knowledge_base' not in st.session_state:
            st.session_state.knowledge_base = {}
            
    def check_rate_limit(self):
        """
        Checks if the user has reached their daily analysis limit.
        
        Returns:
            tuple: A tuple containing a boolean indicating if the user can analyze 
                   and an optional error message.
        """
        # Calculate time until reset
        time_until_reset = timedelta(days=1) - (datetime.now() - st.session_state.last_analysis)
        hours, remainder = divmod(time_until_reset.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        # Reset counter after 24 hours
        if time_until_reset.days < 0:
            st.session_state.analysis_count = 0
            st.session_state.last_analysis = datetime.now()
            return True, None
        
        # Check if limit reached
        if st.session_state.analysis_count >= st.session_state.analysis_limit:
            error_msg = f"Daily limit reached. Reset in {hours}h {minutes}m"
            return False, error_msg
        return True, None

    def analyze_report(self, data, system_prompt, check_only=False, chat_history=None):
        """
        Analyzes report data using in-context learning from previous analyses.
        
        Args:
            data (dict): Report data to analyze.
            system_prompt (str): Base system prompt to guide the analysis.
            check_only (bool): If True, only check rate limit without generating analysis.
            chat_history (list, optional): Previous chat messages in the current session (default is None).
        
        Returns:
            dict: A dictionary containing the success status and the generated content 
                  or an error message.
        """
        can_analyze, error_msg = self.check_rate_limit()
        if not can_analyze:
            return {"success": False, "error": error_msg}
        
        if check_only:
            return can_analyze, error_msg
        
        # Process data before sending to model
        processed_data = self._preprocess_data(data)
        
        # Enhance prompt with in-context learning (only if chat_history is provided)
        enhanced_prompt = self._build_enhanced_prompt(system_prompt, processed_data, chat_history) if chat_history else system_prompt
        
        # Generate analysis using model manager
        result = self.model_manager.generate_analysis(processed_data, enhanced_prompt)
        
        if result["success"]:
            # Update analytics and learning systems
            self._update_analytics(result)
            self._update_knowledge_base(processed_data, result["content"])
        
        return result
    
    def _update_analytics(self, result):
        """
        Updates analytics after a successful analysis.
        
        This includes incrementing the analysis count, updating the last analysis time, 
        and tracking which models were used for the analysis.
        
        Args:
            result (dict): The result of the analysis generated by the model.
        """
        st.session_state.analysis_count += 1
        st.session_state.last_analysis = datetime.now()
        
        # Track which models are being used
        model_used = result.get("model_used", "unknown")
        if model_used in st.session_state.models_used:
            st.session_state.models_used[model_used] += 1
        else:
            st.session_state.models_used[model_used] = 1
    
    def _update_knowledge_base(self, data, analysis):
        """
        Updates the knowledge base with new analysis results for in-context learning.
        Maps key health indicators to analysis patterns.
        
        Args:
            data (dict): Report data that was analyzed.
            analysis (str): The analysis content generated by the model.
        """
        if not isinstance(data, dict) or 'report' not in data:
            return
            
        # Extract key health indicators and map them to analysis outcomes
        # This basic implementation can be expanded with more sophisticated extraction
        report_text = data['report'].lower()
        patient_profile = f"{data.get('age', 'unknown')}-{data.get('gender', 'unknown')}"
        
        # Look for key health indicators in the report
        key_indicators = [
            "hemoglobin", "glucose", "cholesterol", "triglycerides", 
            "hdl", "ldl", "wbc", "rbc", "platelet", "creatinine"
        ]
        
        # Store snippets of analysis associated with key health indicators
        for indicator in key_indicators:
            if indicator in report_text:
                # Find any mentions of this indicator in the analysis
                if indicator in analysis.lower():
                    # Store this learning in knowledge base
                    if indicator not in st.session_state.knowledge_base:
                        st.session_state.knowledge_base[indicator] = {}
                    
                    if patient_profile not in st.session_state.knowledge_base[indicator]:
                        st.session_state.knowledge_base[indicator][patient_profile] = []
                    
                    # Extract the relevant section from analysis (simple approach)
                    lines = analysis.split('\n')
                    relevant_lines = [l for l in lines if indicator in l.lower()]
                    if relevant_lines:
                        # Limit knowledge base size to prevent overflow
                        if len(st.session_state.knowledge_base[indicator][patient_profile]) >= 3:
                            st.session_state.knowledge_base[indicator][patient_profile].pop(0)
                        st.session_state.knowledge_base[indicator][patient_profile].append(relevant_lines[0])
    
    def _build_enhanced_prompt(self, system_prompt, data, chat_history):
        """
        Builds an enhanced prompt using in-context learning from:
        1. Knowledge base of previous analyses
        2. Current session chat history
        
        Args:
            system_prompt (str): The base system prompt.
            data (dict): Report data to analyze.
            chat_history (list): The current session's chat history (optional).
        
        Returns:
            str: The enhanced prompt incorporating relevant context.
        """
        enhanced_prompt = system_prompt
        
        # Add in-context learning from knowledge base
        if isinstance(data, dict) and 'report' in data:
            kb_context = self._get_knowledge_base_context(data)
            if kb_context:
                enhanced_prompt += "\n\n## Relevant Learning From Previous Analyses\n" + kb_context
        
        # Add session context from chat history
        if chat_history:
            session_context = self._get_session_context(chat_history)
            if session_context:
                enhanced_prompt += "\n\n## Current Session History\n" + session_context
        
        return enhanced_prompt
    
    def _get_knowledge_base_context(self, data):
        """
        Extracts relevant context from the knowledge base based on the current report data.
        
        Args:
            data (dict): Report data to analyze.
        
        Returns:
            str: The relevant context from the knowledge base.
        """
        if 'knowledge_base' not in st.session_state or not st.session_state.knowledge_base:
            return ""
            
        report_text = data.get('report', '').lower()
        patient_profile = f"{data.get('age', 'unknown')}-{data.get('gender', 'unknown')}"
        
        context_items = []
        
        # Find relevant knowledge from previous analyses
        for indicator, profiles in st.session_state.knowledge_base.items():
            if indicator in report_text:
                # Get insights from similar patient profiles first
                if patient_profile in profiles:
                    for insight in profiles[patient_profile]:
                        context_items.append(f"- {indicator} (similar patient profile): {insight}")
                
                # Then get general insights
                for profile, insights in profiles.items():
                    if profile != patient_profile:
                        for insight in insights:
                            context_items.append(f"- {indicator} (other patient profile): {insight}")
        
        # Limit context size
        if len(context_items) > 5:
            context_items = context_items[:5]
            
        return "\n".join(context_items) if context_items else ""
    
    def _get_session_context(self, chat_history):
        """
        Extracts relevant context from the current session's chat history.
        
        Args:
            chat_history (list): The current session's chat history.
        
        Returns:
            str: The relevant context from the current session.
        """
        if not chat_history or len(chat_history) < 2:
            return ""
            
        # Get the last few message pairs (up to 2)
        context_items = []
        for i in range(len(chat_history) - 1, 0, -2):
            if i >= 1 and chat_history[i-1]['role'] == 'user' and chat_history[i]['role'] == 'assistant':
                user_msg = chat_history[i-1]['content']
                ai_msg = chat_history[i]['content']
                
                # Keep only the first 200 chars of each message to avoid token explosion
                if len(user_msg) > 200:
                    user_msg = user_msg[:197] + "..."
                if len(ai_msg) > 200:
                    ai_msg = ai_msg[:197] + "..."
                    
                context_items.append(f"User: {user_msg}\nAssistant: {ai_msg}")
                
                # Limit to last 2 exchanges
                if len(context_items) >= 2:
                    break
                    
        return "\n\n".join(reversed(context_items)) if context_items else ""
    
    def _preprocess_data(self, data):
        """
        Pre-processes the data before sending it to the model for analysis.
        
        Args:
            data (dict): Report data to analyze.
        
        Returns:
            dict: Processed data with only the necessary information.
        """
        if isinstance(data, dict):
            # Extract only necessary information to reduce token usage
            processed = {
                "patient_name": data.get("patient_name", ""),
                "age": data.get("age", ""),
                "gender": data.get("gender", ""),
                "report": data.get("report", "")
            }
            return processed
        return data