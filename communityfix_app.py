import streamlit as st
import pandas as pd
import datetime
import json
from pathlib import Path
import base64
import io
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="CommUnityFix - Barangay Union",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79, #2e7d32);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .emergency-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .success-card {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .report-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
    .status-received { border-left-color: #ffc107; }
    .status-progress { border-left-color: #17a2b8; }
    .status-resolved { border-left-color: #28a745; }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1f4e79, #2e7d32);
    }
    .stButton > button {
        background: linear-gradient(90deg, #007bff, #0056b3);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #0056b3, #004085);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for data storage
if 'reports' not in st.session_state:
    st.session_state.reports = []
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
if 'admin_password' not in st.session_state:
    st.session_state.admin_password = "admin123"  # Default password

# Data persistence functions
def save_data_to_file():
    """Save reports data to JSON file"""
    try:
        data = {
            'reports': st.session_state.reports,
            'last_updated': datetime.datetime.now().isoformat()
        }
        with open('reports_data.json', 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.error(f"Error saving data: {e}")

def load_data_from_file():
    """Load reports data from JSON file"""
    try:
        if Path('reports_data.json').exists():
            with open('reports_data.json', 'r') as f:
                data = json.load(f)
                st.session_state.reports = data.get('reports', [])
    except Exception as e:
        st.error(f"Error loading data: {e}")

# Load data on startup
load_data_from_file()

# Sample emergency contacts
EMERGENCY_CONTACTS = {
    "Barangay Hall": "123-4567",
    "Police Station": "911",
    "Fire Department": "911",
    "Hospital Emergency": "911",
    "Rescue Services": "123-4567"
}

# Sample tips for minor problems
TIPS = [
    "For minor garbage issues: Separate biodegradable from non-biodegradable waste",
    "Small potholes: Mark the area with visible objects to alert others while waiting for repair",
    "Streetlight issues: Note the exact location and pole number if available",
    "Drainage problems: Clear visible debris if safe to do so",
    "Graffiti: Document with photos for proper reporting"
]

def save_report(name, contact, issue_type, location, description, photo=None):
    """Save a new report to session state"""
    report_id = len(st.session_state.reports) + 1
    
    # Handle photo upload
    photo_data = None
    if photo is not None:
        try:
            # Convert uploaded file to base64 for storage
            photo_data = base64.b64encode(photo.read()).decode()
        except Exception as e:
            st.warning(f"Could not process photo: {e}")
    
    new_report = {
        'id': report_id,
        'name': name,
        'contact': contact,
        'issue_type': issue_type,
        'location': location,
        'description': description,
        'status': 'Received',
        'assigned_to': 'Not assigned',
        'date_reported': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        'comments': [],
        'photo': photo_data,
        'priority': 'Medium'  # Default priority
    }
    st.session_state.reports.append(new_report)
    
    # Save to file
    save_data_to_file()
    
    return report_id

def add_comment(report_id, comment_text, author="Admin"):
    """Add a comment to a report"""
    for report in st.session_state.reports:
        if report['id'] == report_id:
            comment = {
                'author': author,
                'text': comment_text,
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            report['comments'].append(comment)
            break

def main():
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🏘️ CommUnityFix</h1>
        <h3>Barangay Union - Community Issue Reporting System</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🏘️ CommUnityFix")
    st.sidebar.markdown("**Barangay Union**")
    st.sidebar.markdown("---")
    
    if not st.session_state.admin_logged_in:
        page = st.sidebar.radio("Navigation", ["Report Issue", "Emergency Contacts", "Admin Login"])
    else:
        page = st.sidebar.radio("Navigation", ["Report Issue", "Emergency Contacts", "Admin Dashboard", "Logout"])
    
    # Report Issue Page
    if page == "Report Issue":
        show_report_page()
    
    # Emergency Contacts Page
    elif page == "Emergency Contacts":
        show_contacts_page()
    
    # Admin Login Page
    elif page == "Admin Login":
        show_admin_login()
    
    # Admin Dashboard
    elif page == "Admin Dashboard":
        if st.session_state.admin_logged_in:
            show_admin_dashboard()
        else:
            st.warning("Please log in first")
            show_admin_login()
    
    # Logout
    elif page == "Logout":
        st.session_state.admin_logged_in = False
        st.success("Logged out successfully!")
        st.rerun()

def show_report_page():
    st.title("📝 Report a Community Issue")
    st.markdown("Use this form to report problems in our community. Your reports help make Barangay Union better!")
    
    # Add some helpful information
    with st.expander("ℹ️ Before Reporting"):
        st.write("""
        - **Take a photo** if possible to help us understand the issue better
        - **Be specific** about the location (street names, landmarks, house numbers)
        - **Describe the severity** and any safety concerns
        - **Include your contact** so we can follow up if needed
        """)
    
    with st.form("report_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Your Name *", placeholder="Enter your full name")
            contact = st.text_input("Contact Number *", placeholder="09XXXXXXXXX", help="Include area code if applicable")
            issue_type = st.selectbox(
                "Issue Type *",
                ["Pothole", "Garbage Accumulation", "Broken Streetlight", 
                 "Clogged Drainage", "Graffiti", "Damaged Road", "Water Leak", 
                 "Noise Complaint", "Safety Hazard", "Other"]
            )
            priority = st.selectbox(
                "Priority Level",
                ["Low", "Medium", "High", "Emergency"],
                help="Emergency: Immediate danger to life/property"
            )
        
        with col2:
            location = st.text_input("Location *", placeholder="Ex: Near Barangay Hall, Main Street")
            description = st.text_area("Description *", placeholder="Please describe the issue in detail...", height=100)
            photo = st.file_uploader("Upload Photo (Optional)", type=['png', 'jpg', 'jpeg'], help="Maximum file size: 5MB")
            
            # Show photo preview if uploaded
            if photo is not None:
                try:
                    image = Image.open(photo)
                    st.image(image, caption="Photo Preview", use_column_width=True)
                except Exception as e:
                    st.warning(f"Could not preview image: {e}")
        
        st.markdown("**Required fields*")
        submitted = st.form_submit_button("🚀 Submit Report", use_container_width=True)
        
        if submitted:
            # Enhanced validation
            errors = []
            if not name or len(name.strip()) < 2:
                errors.append("Please enter a valid name (at least 2 characters)")
            if not contact or len(contact.strip()) < 10:
                errors.append("Please enter a valid contact number (at least 10 digits)")
            if not location or len(location.strip()) < 5:
                errors.append("Please provide a more specific location")
            if not description or len(description.strip()) < 10:
                errors.append("Please provide a more detailed description (at least 10 characters)")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                report_id = save_report(name, contact, issue_type, location, description, photo)
                st.markdown(f"""
                <div class="success-card">
                    <h3>✅ Report Submitted Successfully!</h3>
                    <p><strong>Report ID:</strong> #{report_id}</p>
                    <p>Thank you for helping improve our community!</p>
                </div>
                """, unsafe_allow_html=True)
                st.info("📞 You can check the status of your report by contacting Barangay Hall or logging in as admin.")

def show_contacts_page():
    st.title("📞 Emergency Contacts & Tips")
    
    st.header("🚨 Emergency Contacts")
    col1, col2 = st.columns(2)
    
    with col1:
        for service, number in list(EMERGENCY_CONTACTS.items())[:3]:
            st.markdown(f"""
            <div class="emergency-card">
                <h4>{service}</h4>
                <h2>{number}</h2>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        for service, number in list(EMERGENCY_CONTACTS.items())[3:]:
            st.markdown(f"""
            <div class="emergency-card">
                <h4>{service}</h4>
                <h2>{number}</h2>
            </div>
            """, unsafe_allow_html=True)
    
    st.header("🛠️ Tips for Minor Problems")
    
    for i, tip in enumerate(TIPS, 1):
        st.markdown(f"""
        <div class="report-card">
            <strong>{i}.</strong> {tip}
        </div>
        """, unsafe_allow_html=True)
    
    st.header("🚨 Emergency Procedures")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("🏥 Medical Emergency", expanded=False):
            st.write("""
            **Immediate Actions:**
            1. Call emergency services immediately (911)
            2. Provide clear location details
            3. Do not move injured person unless necessary
            4. Have someone wait to guide emergency responders
            5. Apply first aid if trained
            """)
        
        with st.expander("🔥 Fire Emergency", expanded=False):
            st.write("""
            **Immediate Actions:**
            1. Alert everyone in the area
            2. Call fire department (911)
            3. Use fire extinguisher if safe
            4. Evacuate immediately if fire spreads
            5. Meet at designated assembly point
            """)
    
    with col2:
        with st.expander("🌪️ Natural Disasters", expanded=False):
            st.write("""
            **General Guidelines:**
            1. Stay informed through official channels
            2. Follow evacuation orders immediately
            3. Have emergency kit ready
            4. Stay away from windows and doors
            5. Check on neighbors if safe
            """)
        
        with st.expander("🚨 Security Issues", expanded=False):
            st.write("""
            **Safety Measures:**
            1. Call police immediately (911)
            2. Do not confront suspicious persons
            3. Lock doors and windows
            4. Stay in safe location
            5. Report to barangay officials
            """)
    
    # Quick action buttons
    st.header("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📞 Call Emergency (911)", use_container_width=True):
            st.info("Dial 911 for immediate emergency assistance")
    
    with col2:
        if st.button("🏛️ Contact Barangay Hall", use_container_width=True):
            st.info("Barangay Hall: 123-4567")
    
    with col3:
        if st.button("📝 Report Issue", use_container_width=True):
            st.info("Use the 'Report Issue' page to submit non-emergency problems")

def show_admin_login():
    st.title("🔐 Admin Login")
    
    with st.form("login_form"):
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")
        
        if login_btn:
            if password == st.session_state.admin_password:
                st.session_state.admin_logged_in = True
                st.success("Login successful! Redirecting to dashboard...")
                st.rerun()
            else:
                st.error("Incorrect password!")

def show_admin_dashboard():
    st.title("📊 Admin Dashboard")
    
    # Statistics
    total_reports = len(st.session_state.reports)
    received = len([r for r in st.session_state.reports if r['status'] == 'Received'])
    in_progress = len([r for r in st.session_state.reports if r['status'] == 'In Progress'])
    resolved = len([r for r in st.session_state.reports if r['status'] == 'Resolved'])
    
    # Calculate resolution rate
    resolution_rate = (resolved / total_reports * 100) if total_reports > 0 else 0
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Reports</h3>
            <h1>{total_reports}</h1>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Received</h3>
            <h1>{received}</h1>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>In Progress</h3>
            <h1>{in_progress}</h1>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Resolved</h3>
            <h1>{resolved}</h1>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Resolution Rate</h3>
            <h1>{resolution_rate:.1f}%</h1>
        </div>
        """, unsafe_allow_html=True)
    
    # Reports table with status management
    st.header("📋 All Reports")
    
    if st.session_state.reports:
        # Search and filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input("🔍 Search reports", placeholder="Search by location, issue type, or name")
        
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All", "Received", "In Progress", "Resolved"])
        
        with col3:
            issue_filter = st.selectbox("Filter by Issue Type", ["All"] + list(set([r['issue_type'] for r in st.session_state.reports])))
        
        # Filter reports based on search and filters
        filtered_reports = st.session_state.reports.copy()
        
        if search_term:
            filtered_reports = [r for r in filtered_reports if 
                              search_term.lower() in r['location'].lower() or 
                              search_term.lower() in r['issue_type'].lower() or 
                              search_term.lower() in r['name'].lower()]
        
        if status_filter != "All":
            filtered_reports = [r for r in filtered_reports if r['status'] == status_filter]
        
        if issue_filter != "All":
            filtered_reports = [r for r in filtered_reports if r['issue_type'] == issue_filter]
        
        # Create DataFrame for display
        df_data = []
        for report in filtered_reports:
            df_data.append({
                'ID': report['id'],
                'Name': report['name'],
                'Issue Type': report['issue_type'],
                'Location': report['location'],
                'Status': report['status'],
                'Date Reported': report['date_reported'],
                'Assigned To': report['assigned_to'],
                'Priority': report.get('priority', 'Medium')
            })
        
        if df_data:
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            # Show filtered count
            st.info(f"Showing {len(filtered_reports)} of {len(st.session_state.reports)} reports")
        else:
            st.warning("No reports match your search criteria.")
        
        # Report management
        st.header("🛠️ Manage Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Update Report Status")
            report_id = st.selectbox("Select Report", 
                                   [f"#{r['id']} - {r['issue_type']} - {r['location']}" 
                                    for r in st.session_state.reports])
            
            selected_report = None
            selected_id = None
            
            if report_id:
                selected_id = int(report_id.split('#')[1].split(' - ')[0])
                selected_report = next((r for r in st.session_state.reports if r['id'] == selected_id), None)
                
                if selected_report:
                    # Display report details
                    st.markdown(f"""
                    <div class="report-card">
                        <h4>Report #{selected_report['id']}</h4>
                        <p><strong>Reporter:</strong> {selected_report['name']}</p>
                        <p><strong>Contact:</strong> {selected_report['contact']}</p>
                        <p><strong>Issue:</strong> {selected_report['issue_type']}</p>
                        <p><strong>Location:</strong> {selected_report['location']}</p>
                        <p><strong>Description:</strong> {selected_report['description']}</p>
                        <p><strong>Date:</strong> {selected_report['date_reported']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show photo if available
                    if selected_report.get('photo'):
                        try:
                            photo_data = base64.b64decode(selected_report['photo'])
                            st.image(photo_data, caption="Report Photo", use_column_width=True)
                        except:
                            st.warning("Could not display photo")
                    
                    new_status = st.selectbox("Update Status", 
                                            ["Received", "In Progress", "Resolved"],
                                            index=["Received", "In Progress", "Resolved"].index(selected_report['status']))
                    assigned_to = st.text_input("Assign To", value=selected_report['assigned_to'])
                    priority = st.selectbox("Priority", 
                                          ["Low", "Medium", "High", "Emergency"],
                                          index=["Low", "Medium", "High", "Emergency"].index(selected_report.get('priority', 'Medium')))
                    
                    if st.button("Update Report", use_container_width=True):
                        selected_report['status'] = new_status
                        selected_report['assigned_to'] = assigned_to
                        selected_report['priority'] = priority
                        save_data_to_file()  # Save changes
                        st.success("Report updated successfully!")
                        st.rerun()
        
        with col2:
            st.subheader("Add Comment")
            if selected_report:
                comment = st.text_area("Add comment/update", placeholder="Enter your comment or status update...")
                if st.button("Add Comment", use_container_width=True):
                    if comment:
                        add_comment(selected_id, comment)
                        save_data_to_file()  # Save changes
                        st.success("Comment added!")
                        st.rerun()
                    else:
                        st.warning("Please enter a comment")
        
        # Display comments for selected report
        if selected_report and selected_report['comments']:
            st.subheader("💬 Comments & Updates")
            for comment in reversed(selected_report['comments']):
                with st.container():
                    st.markdown(f"""
                    <div class="report-card">
                        <strong>{comment['author']}</strong> - <em>{comment['timestamp']}</em><br>
                        {comment['text']}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Export functionality
        st.header("📊 Export & Backup")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export Reports to CSV", use_container_width=True):
                if st.session_state.reports:
                    df_export = pd.DataFrame(st.session_state.reports)
                    csv = df_export.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"reports_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No reports to export")
        
        with col2:
            if st.button("💾 Backup Data", use_container_width=True):
                save_data_to_file()
                st.success("Data backed up successfully!")
    
    else:
        st.info("No reports submitted yet.")

if __name__ == "__main__":
    main()