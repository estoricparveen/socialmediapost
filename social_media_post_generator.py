import streamlit as st
from datetime import datetime
import google.generativeai as genai
import openai
from streamlit.components.v1 import html

def create_copy_button(text, button_id):
    """Create an HTML/JavaScript copy button that won't affect the page state"""
    copy_button_html = f"""
        <div style="position: relative; margin-bottom: 15px;">
            <button 
                onclick="copyText_{button_id}()"
                style="
                    background-color: white;
                    border: 1px solid #ccc;
                    padding: 8px 15px;
                    border-radius: 5px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    gap: 5px;
                    font-size: 14px;
                "
            >
                <span style="font-size: 16px;">📋</span>
                <span>Copy</span>
            </button>
            <textarea id="textToCopy_{button_id}" style="position: absolute; top: -9999px;">{text}</textarea>
            <script>
                function copyText_{button_id}() {{
                    var copyText = document.getElementById("textToCopy_{button_id}");
                    copyText.select();
                    document.execCommand("copy");
                    var button = event.target;
                    if (button.tagName === 'SPAN') button = button.parentElement;
                    var originalText = button.innerHTML;
                    button.innerHTML = '<span>✓ Copied!</span>';
                    setTimeout(function() {{
                        button.innerHTML = originalText;
                    }}, 2000);
                }}
            </script>
        </div>
    """
    return copy_button_html

def setup_gemini(api_key):
    """Configure Gemini API with the provided key"""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-pro')

def setup_chatgpt(api_key):
    """Configure ChatGPT API with the provided key"""
    client = openai.OpenAI(api_key=api_key)
    return client

def generate_post_with_gemini(model, platform, event_name, date, description, venue):
    """Generate social media post using Gemini"""
    prompt = f"""Generate a {platform} post for an event with the following details:
    Event Name: {event_name}
    Date: {date}
    Venue: {venue}
    Description: {description}
    
    For {platform}, consider these specific requirements:
    - LinkedIn: Professional tone, include relevant hashtags, structured format
    - Twitter: Concise (under 280 characters), engaging, include hashtags
    - WhatsApp: Casual tone, use emojis, clear formatting with event details
    
    Generate only the post content without any explanations."""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating post: {str(e)}"

def generate_post_with_chatgpt(client, platform, event_name, date, description, venue):
    """Generate social media post using ChatGPT"""
    prompt = f"""Generate a {platform} post for an event with the following details:
    Event Name: {event_name}
    Date: {date}
    Venue: {venue}
    Description: {description}
    
    For {platform}, consider these specific requirements:
    - LinkedIn: Professional tone, include relevant hashtags, structured format
    - Twitter: Concise (under 280 characters), engaging, include hashtags
    - WhatsApp: Casual tone, use emojis, clear formatting with event details
    
    Generate only the post content without any explanations."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating post: {str(e)}"

def main():
    st.set_page_config(page_title="Social Media Post Generator", layout="wide")
    
    # Custom CSS
    st.markdown("""
        <style>
        .stTextInput > div > div > input {
            background-color: #f0f2f6;
        }
        .stTextArea > div > div > textarea {
            background-color: #f0f2f6;
        }
        .output-container {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #dee2e6;
            margin-top: 5px;
        }
        .generate-button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            border: none;
            cursor: pointer;
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # App title and description
    st.title("📱 Social Media Post Generator (AI-Powered)")
    st.markdown("Generate AI-powered platform-specific posts for your events")
    st.markdown("---")
    
    # Sidebar for API selection and configuration
    st.sidebar.title("API Configuration")
    api_choice = st.sidebar.radio("Select AI Service", ["Gemini", "ChatGPT"])
    
    # API Key input based on selection
    if api_choice == "Gemini":
        api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
        st.sidebar.markdown("[Get Gemini API Key](https://makersuite.google.com/app/apikey)")
    else:
        api_key = st.sidebar.text_input("Enter OpenAI API Key", type="password")
        st.sidebar.markdown("[Get OpenAI API Key](https://platform.openai.com/api-keys)")
    
    if not api_key:
        st.sidebar.warning(f"Please enter your {api_choice} API key to continue")
        st.info(f"👈 Enter your {api_choice} API key in the sidebar to get started")
        return
    
    try:
        if api_choice == "Gemini":
            model = setup_gemini(api_key)
        else:
            model = setup_chatgpt(api_key)
    except Exception as e:
        st.error(f"Error initializing {api_choice}: {str(e)}")
        return
    
    # Input section
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            event_name = st.text_input("Event Name", placeholder="Enter event name")
            date = st.date_input("Event Date", min_value=datetime.today())
            venue = st.text_input("Venue", placeholder="Enter event venue")
            description = st.text_area("Event Description", 
                                     placeholder="Enter a detailed description of your event",
                                     height=150)
            
            # Generate button
            generate = st.button("Generate Posts", type="primary", use_container_width=True)
        
        # Generate posts only if all fields are filled and button is clicked
        if all([event_name, date, venue, description]) and generate:
            with col2:
                formatted_date = date.strftime("%B %d, %Y")
                
                # Generate posts for each platform
                with st.spinner(f"Generating posts using {api_choice} AI..."):
                    # LinkedIn Post
                    st.subheader("LinkedIn Post")
                    if api_choice == "Gemini":
                        linkedin_post = generate_post_with_gemini(model, "LinkedIn", 
                                                                event_name, formatted_date, 
                                                                description, venue)
                    else:
                        linkedin_post = generate_post_with_chatgpt(model, "LinkedIn", 
                                                                 event_name, formatted_date, 
                                                                 description, venue)
                    html(create_copy_button(linkedin_post, "linkedin"))
                    st.markdown('<div class="output-container">', unsafe_allow_html=True)
                    st.markdown(linkedin_post)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Twitter Post
                    st.subheader("Twitter Post")
                    if api_choice == "Gemini":
                        twitter_post = generate_post_with_gemini(model, "Twitter", 
                                                               event_name, formatted_date, 
                                                               description, venue)
                    else:
                        twitter_post = generate_post_with_chatgpt(model, "Twitter", 
                                                                event_name, formatted_date, 
                                                                description, venue)
                    html(create_copy_button(twitter_post, "twitter"))
                    st.markdown('<div class="output-container">', unsafe_allow_html=True)
                    st.markdown(twitter_post)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # WhatsApp Post
                    st.subheader("WhatsApp Post")
                    if api_choice == "Gemini":
                        whatsapp_post = generate_post_with_gemini(model, "WhatsApp", 
                                                                event_name, formatted_date, 
                                                                description, venue)
                    else:
                        whatsapp_post = generate_post_with_chatgpt(model, "WhatsApp", 
                                                                 event_name, formatted_date, 
                                                                 description, venue)
                    html(create_copy_button(whatsapp_post, "whatsapp"))
                    st.markdown('<div class="output-container">', unsafe_allow_html=True)
                    st.markdown(whatsapp_post)
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            with col2:
                if not generate:
                    st.info("👈 Fill in all the event details and click 'Generate Posts'")
                
                # Example section
                st.markdown("### Example Input")
                st.markdown("""
                **Event Name:** Tech Conference 2025
                
                **Date:** January 15, 2025
                
                **Venue:** Virtual Event
                
                **Description:** Join us for an exciting day of technology insights, networking, and learning from industry experts. Featured topics include AI, Cloud Computing, and Digital Transformation.
                """)

if __name__ == "__main__":
    main()