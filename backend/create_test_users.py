"""
Script to create 50 test users across different subscription tiers
Generates users with realistic data for testing the multi-agent system
"""

import requests
import json
from datetime import datetime

# Backend URL
BACKEND_URL = "https://next-backend-jxs4smo7nq-uc.a.run.app"

# Subscription tier distribution (50 users total)
TIER_DISTRIBUTION = {
    "free": 25,  # 50% - Free tier
    "basic": 10,  # 20% - Basic tier
    "pro": 10,  # 20% - Pro tier
    "elite": 5,  # 10% - Elite tier
}

# Sample data for realistic test users
FIRST_NAMES = [
    "Emma",
    "Liam",
    "Olivia",
    "Noah",
    "Ava",
    "Ethan",
    "Sophia",
    "Mason",
    "Isabella",
    "William",
    "Mia",
    "James",
    "Charlotte",
    "Benjamin",
    "Amelia",
    "Lucas",
    "Harper",
    "Henry",
    "Evelyn",
    "Alexander",
    "Abigail",
    "Sebastian",
    "Emily",
    "Jack",
    "Elizabeth",
    "Michael",
    "Sofia",
    "Daniel",
    "Avery",
    "Matthew",
    "Ella",
    "Joseph",
    "Scarlett",
    "David",
    "Grace",
    "Logan",
    "Chloe",
    "Jackson",
    "Victoria",
    "Samuel",
    "Riley",
    "Owen",
    "Aria",
    "Wyatt",
    "Lily",
    "John",
    "Aubrey",
    "Carter",
    "Zoey",
    "Dylan",
]

LAST_NAMES = [
    "Smith",
    "Johnson",
    "Williams",
    "Brown",
    "Jones",
    "Garcia",
    "Miller",
    "Davis",
    "Rodriguez",
    "Martinez",
    "Hernandez",
    "Lopez",
    "Gonzalez",
    "Wilson",
    "Anderson",
    "Thomas",
    "Taylor",
    "Moore",
    "Jackson",
    "Martin",
    "Lee",
    "Perez",
    "Thompson",
    "White",
    "Harris",
    "Sanchez",
    "Clark",
    "Ramirez",
    "Lewis",
    "Robinson",
    "Walker",
    "Young",
    "Allen",
    "King",
    "Wright",
    "Scott",
    "Torres",
    "Nguyen",
    "Hill",
    "Flores",
    "Green",
    "Adams",
    "Nelson",
    "Baker",
    "Hall",
    "Rivera",
    "Campbell",
    "Mitchell",
    "Carter",
    "Roberts",
]

JOB_TITLES = [
    "Software Engineer",
    "Data Scientist",
    "Product Manager",
    "UX Designer",
    "DevOps Engineer",
    "Full Stack Developer",
    "Frontend Developer",
    "Backend Developer",
    "ML Engineer",
    "Cloud Architect",
    "Business Analyst",
    "Project Manager",
    "Marketing Manager",
    "Sales Executive",
    "HR Manager",
    "Financial Analyst",
    "Accountant",
    "Operations Manager",
    "Customer Success Manager",
    "Content Writer",
    "Graphic Designer",
    "Mobile Developer",
    "QA Engineer",
    "Security Engineer",
    "Database Administrator",
]

SKILLS_BY_ROLE = {
    "Software Engineer": ["Python", "Java", "React", "AWS", "Docker"],
    "Data Scientist": ["Python", "Machine Learning", "SQL", "Statistics", "TensorFlow"],
    "Product Manager": ["Agile", "Product Strategy", "Data Analysis", "Stakeholder Management", "Roadmapping"],
    "UX Designer": ["Figma", "User Research", "Prototyping", "Design Systems", "Usability Testing"],
    "DevOps Engineer": ["Kubernetes", "CI/CD", "AWS", "Terraform", "Monitoring"],
    "Full Stack Developer": ["React", "Node.js", "MongoDB", "REST APIs", "JavaScript"],
    "Frontend Developer": ["React", "TypeScript", "CSS", "HTML", "Webpack"],
    "Backend Developer": ["Python", "Django", "PostgreSQL", "REST APIs", "Microservices"],
    "ML Engineer": ["PyTorch", "TensorFlow", "Python", "Deep Learning", "MLOps"],
    "Cloud Architect": ["AWS", "Azure", "Cloud Security", "Infrastructure as Code", "Networking"],
}

LOCATIONS = [
    "New York, NY",
    "San Francisco, CA",
    "Seattle, WA",
    "Austin, TX",
    "Boston, MA",
    "Chicago, IL",
    "Los Angeles, CA",
    "Denver, CO",
    "Atlanta, GA",
    "Portland, OR",
    "Remote",
    "Miami, FL",
    "Dallas, TX",
    "Phoenix, AZ",
    "San Diego, CA",
]


def create_test_users():
    """Create 50 test users across different tiers"""

    users_created = {"free": [], "basic": [], "pro": [], "elite": []}

    user_index = 0

    print("🚀 Starting test user creation...\n")
    print(f"Target: {sum(TIER_DISTRIBUTION.values())} users")
    print(f"Distribution: {TIER_DISTRIBUTION}\n")

    # Create users for each tier
    for tier, count in TIER_DISTRIBUTION.items():
        print(f"\n{'='*60}")
        print(f"Creating {count} {tier.upper()} tier users...")
        print(f"{'='*60}\n")

        for i in range(count):
            # Generate user data
            first_name = FIRST_NAMES[user_index % len(FIRST_NAMES)]
            last_name = LAST_NAMES[user_index % len(LAST_NAMES)]
            full_name = f"{first_name} {last_name}"
            email = f"test.{tier}.{i+1}@careeriq.com"
            firebase_uid = f"test_{tier}_{i+1}_{datetime.now().timestamp()}"

            # Job-related data
            job_title = JOB_TITLES[user_index % len(JOB_TITLES)]
            skills = SKILLS_BY_ROLE.get(job_title, ["Python", "JavaScript", "SQL"])[:5]
            location = LOCATIONS[user_index % len(LOCATIONS)]
            years_experience = (user_index % 15) + 1  # 1-15 years

            user_data = {"email": email, "firebase_uid": firebase_uid, "name": full_name, "subscription_tier": tier}

            # Create user in backend
            try:
                response = requests.post(f"{BACKEND_URL}/api/users", json=user_data, timeout=10)

                if response.status_code in [200, 201]:
                    user_info = {
                        "email": email,
                        "password": f"{tier}Test123!",  # Standard test password
                        "name": full_name,
                        "tier": tier,
                        "job_title": job_title,
                        "skills": skills,
                        "location": location,
                        "experience": years_experience,
                    }
                    users_created[tier].append(user_info)
                    print(f"✅ Created: {email} | {full_name} | {tier.upper()}")
                else:
                    print(f"❌ Failed to create {email}: {response.status_code}")
                    print(f"   Response: {response.text}")

            except Exception as e:
                print(f"❌ Error creating {email}: {str(e)}")

            user_index += 1

    # Generate summary report
    print("\n" + "=" * 60)
    print("✅ USER CREATION COMPLETE")
    print("=" * 60 + "\n")

    total_created = sum(len(users) for users in users_created.values())
    print(f"Total users created: {total_created}/{sum(TIER_DISTRIBUTION.values())}\n")

    # Print tier breakdown
    for tier, users in users_created.items():
        print(f"{tier.upper()}: {len(users)} users")

    # Save credentials to file
    save_credentials(users_created)

    # Print test credentials
    print_test_credentials(users_created)

    return users_created


def save_credentials(users_created):
    """Save all user credentials to JSON file"""

    output_file = "test_users_credentials.json"

    credentials = {
        "created_at": datetime.now().isoformat(),
        "backend_url": BACKEND_URL,
        "total_users": sum(len(users) for users in users_created.values()),
        "users_by_tier": users_created,
        "test_instructions": {
            "elite": "Use these credentials to test all premium features",
            "pro": "Use these credentials to test pro-level features",
            "basic": "Use these credentials to test basic tier features",
            "free": "Use these credentials to test free tier limitations",
        },
    }

    with open(output_file, "w") as f:
        json.dump(credentials, f, indent=2)

    print(f"\n💾 All credentials saved to: {output_file}")


def print_test_credentials(users_created):
    """Print test credentials for Elite and Pro tiers"""

    print("\n" + "=" * 60)
    print("🔑 TEST CREDENTIALS FOR MANUAL TESTING")
    print("=" * 60 + "\n")

    # Elite tier credentials
    if users_created["elite"]:
        print("🏆 ELITE TIER TEST ACCOUNTS:")
        print("-" * 60)
        for i, user in enumerate(users_created["elite"][:3], 1):  # Show first 3
            print(f"\nElite Account #{i}:")
            print(f"  Email:    {user['email']}")
            print(f"  Password: {user['password']}")
            print(f"  Name:     {user['name']}")
            print(f"  Role:     {user['job_title']}")

    # Pro tier credentials
    if users_created["pro"]:
        print("\n\n💎 PRO TIER TEST ACCOUNTS:")
        print("-" * 60)
        for i, user in enumerate(users_created["pro"][:3], 1):  # Show first 3
            print(f"\nPro Account #{i}:")
            print(f"  Email:    {user['email']}")
            print(f"  Password: {user['password']}")
            print(f"  Name:     {user['name']}")
            print(f"  Role:     {user['job_title']}")

    # Basic tier credentials
    if users_created["basic"]:
        print("\n\n⭐ BASIC TIER TEST ACCOUNTS:")
        print("-" * 60)
        for i, user in enumerate(users_created["basic"][:2], 1):  # Show first 2
            print(f"\nBasic Account #{i}:")
            print(f"  Email:    {user['email']}")
            print(f"  Password: {user['password']}")
            print(f"  Name:     {user['name']}")
            print(f"  Role:     {user['job_title']}")

    # Free tier credentials
    if users_created["free"]:
        print("\n\n🆓 FREE TIER TEST ACCOUNTS:")
        print("-" * 60)
        for i, user in enumerate(users_created["free"][:2], 1):  # Show first 2
            print(f"\nFree Account #{i}:")
            print(f"  Email:    {user['email']}")
            print(f"  Password: {user['password']}")
            print(f"  Name:     {user['name']}")
            print(f"  Role:     {user['job_title']}")

    print("\n" + "=" * 60)
    print("📋 TESTING INSTRUCTIONS")
    print("=" * 60)
    print(
        """
1. Use ELITE credentials to test:
   - Full 9-agent orchestrator access
   - Unlimited analysis runs
   - Career Radar Dashboard
   - All predictive features
   - Peer benchmarking
   - Market intelligence

2. Use PRO credentials to test:
   - 7-agent system access
   - Advanced analytics
   - Career trajectory predictions
   - Limited benchmarking

3. Use BASIC credentials to test:
   - 5-agent system access
   - Standard analysis
   - Basic features

4. Use FREE credentials to test:
   - 3-agent basic analysis
   - Feature limitations
   - Upgrade prompts
    """
    )


if __name__ == "__main__":
    create_test_users()
