from google.adk.agents import Agent
from google.cloud import vision
import requests
import json
from typing import Dict, Any
import os
from datetime import datetime

def capture_screenshot(url: str) -> Dict[str, Any]:
    """Captures page screenshot using Google Cloud Vision API."""
    try:
        # Initialize Vision client
        client = vision.ImageAnnotatorClient()
        
        # For this example, we'll use a web service to capture screenshot
        # In production, you might use Puppeteer or similar headless browser
        screenshot_api = f"https://api.screenshotlayer.com/api/capture"
        params = {
            'access_key': os.getenv('SCREENSHOTLAYER_API_KEY'),
            'url': url,
            'viewport': '1440x900',
            'format': 'PNG'
        }
        
        response = requests.get(screenshot_api, params=params)
        
        if response.status_code == 200:
            # Analyze screenshot with Vision API
            image = vision.Image(content=response.content)
            
            # Detect text in the image
            text_response = client.text_detection(image=image)
            texts = text_response.text_annotations
            
            # Basic analysis
            text_content = texts[0].description if texts else "No text detected"
            
            return {
                "status": "success",
                "screenshot_captured": True,
                "text_detected": len(texts) > 0,
                "text_preview": text_content[:200] + "..." if len(text_content) > 200 else text_content,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"status": "error", "message": f"Screenshot capture failed: {response.status_code}"}
            
    except Exception as e:
        return {"status": "error", "message": f"Screenshot analysis error: {str(e)}"}

def analyze_page_speed(url: str) -> Dict[str, Any]:
    """Analyzes page speed using PageSpeed Insights API."""
    try:
        api_key = os.getenv('PAGESPEED_API_KEY')
        api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        
        params = {
            'url': url,
            'key': api_key,
            'strategy': 'desktop',
            'category': ['performance', 'accessibility', 'best-practices', 'seo']
        }
        
        response = requests.get(api_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            lighthouse_result = data.get('lighthouseResult', {})
            categories = lighthouse_result.get('categories', {})
            
            scores = {
                'performance': categories.get('performance', {}).get('score', 0) * 100,
                'accessibility': categories.get('accessibility', {}).get('score', 0) * 100,
                'best_practices': categories.get('best-practices', {}).get('score', 0) * 100,
                'seo': categories.get('seo', {}).get('score', 0) * 100
            }
            
            # Core Web Vitals
            audits = lighthouse_result.get('audits', {})
            core_vitals = {
                'largest_contentful_paint': audits.get('largest-contentful-paint', {}).get('displayValue', 'N/A'),
                'first_input_delay': audits.get('max-potential-fid', {}).get('displayValue', 'N/A'),
                'cumulative_layout_shift': audits.get('cumulative-layout-shift', {}).get('displayValue', 'N/A')
            }
            
            return {
                "status": "success",
                "url": url,
                "scores": scores,
                "core_web_vitals": core_vitals,
                "overall_performance": scores['performance'],
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"status": "error", "message": f"PageSpeed API error: {response.status_code}"}
            
    except Exception as e:
        return {"status": "error", "message": f"Page speed analysis error: {str(e)}"}

def check_mobile_friendly(url: str) -> Dict[str, Any]:
    """Checks mobile friendliness using Google's Mobile-Friendly Test API."""
    try:
        api_key = os.getenv('PAGESPEED_API_KEY')  # Same key works for mobile-friendly test
        api_url = "https://searchconsole.googleapis.com/v1/urlTestingTools/mobileFriendlyTest:run"
        
        headers = {'Content-Type': 'application/json'}
        payload = {
            'url': url,
            'requestScreenshot': True
        }
        
        response = requests.post(f"{api_url}?key={api_key}", 
                               headers=headers, 
                               json=payload)
        
        if response.status_code == 200:
            data = response.json()
            
            mobile_friendly = data.get('mobileFriendliness', 'UNKNOWN')
            issues = data.get('mobileFriendlyIssues', [])
            
            return {
                "status": "success",
                "mobile_friendly": mobile_friendly == 'MOBILE_FRIENDLY',
                "issues_count": len(issues),
                "issues": [issue.get('rule', 'Unknown issue') for issue in issues[:5]],
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"status": "error", "message": f"Mobile-Friendly API error: {response.status_code}"}
            
    except Exception as e:
        return {"status": "error", "message": f"Mobile-friendly check error: {str(e)}"}

def generate_analysis_report(url: str, screenshot_data: Dict, speed_data: Dict, mobile_data: Dict) -> str:
    """Generates a comprehensive analysis report."""
    
    report = f"""
# Website Analysis Report for {url}

## Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Screenshot Analysis
- Screenshot captured: {screenshot_data.get('screenshot_captured', False)}
- Text detected: {screenshot_data.get('text_detected', False)}
- Content preview: {screenshot_data.get('text_preview', 'N/A')}

## Performance Analysis
- Overall Performance Score: {speed_data.get('scores', {}).get('performance', 'N/A')}/100
- Accessibility Score: {speed_data.get('scores', {}).get('accessibility', 'N/A')}/100
- Best Practices Score: {speed_data.get('scores', {}).get('best_practices', 'N/A')}/100
- SEO Score: {speed_data.get('scores', {}).get('seo', 'N/A')}/100

## Core Web Vitals
- Largest Contentful Paint: {speed_data.get('core_web_vitals', {}).get('largest_contentful_paint', 'N/A')}
- First Input Delay: {speed_data.get('core_web_vitals', {}).get('first_input_delay', 'N/A')}
- Cumulative Layout Shift: {speed_data.get('core_web_vitals', {}).get('cumulative_layout_shift', 'N/A')}

## Mobile Friendliness
- Mobile Friendly: {mobile_data.get('mobile_friendly', False)}
- Issues Found: {mobile_data.get('issues_count', 0)}
- Issues: {', '.join(mobile_data.get('issues', []))}

## Basic Recommendations
1. {"✅ Great performance!" if speed_data.get('scores', {}).get('performance', 0) >= 90 else "⚠️ Consider optimizing page load speed"}
2. {"✅ Mobile-friendly!" if mobile_data.get('mobile_friendly', False) else "⚠️ Fix mobile usability issues"}
3. {"✅ Good accessibility!" if speed_data.get('scores', {}).get('accessibility', 0) >= 90 else "⚠️ Improve accessibility features"}
    """
    
    return report

# Create the root agent
root_agent = Agent(
    name="website_analyzer_v1",
    model="gemini-2.0-flash",
    description="A website analyzer that captures screenshots and performs basic technical analysis",
    instruction="""
    You are a website analyzer agent. When given a URL, you will:
    1. Capture a screenshot of the page using Google Cloud Vision API
    2. Analyze page speed using PageSpeed Insights API
    3. Check mobile-friendliness using Google's Mobile-Friendly Test API
    4. Generate a comprehensive analysis report with basic recommendations
    
    Always provide actionable insights and clear, non-technical explanations.
    """,
    tools=[capture_screenshot, analyze_page_speed, check_mobile_friendly, generate_analysis_report]
)