import json
import csv
import random
import uuid
import datetime
import os

os.makedirs('backend/uploads/simulations/new_test_data', exist_ok=True)

genders = ['male', 'female', 'other']
mbtis = ['ISTJ', 'ISFJ', 'INFJ', 'INTJ', 'ISTP', 'ISFP', 'INFP', 'INTP', 'ESTP', 'ESFP', 'ENFP', 'ENTP', 'ESTJ', 'ESFJ', 'ENFJ', 'ENTJ']
countries = ['United States', 'Canada', 'United Kingdom', 'Australia', 'Germany', 'France', 'Japan', 'Brazil', 'China', 'India']
professions = ['Teacher', 'Software Engineer', 'Nurse', 'Retired', 'Student', 'Retail Worker', 'Accountant', 'Construction Worker', 'Artist', 'Manager', 'Unemployed', 'Freelancer']
interests_pool = ['Healthcare', 'Technology', 'Sports', 'Reading', 'Travel', 'Cooking', 'Gaming', 'Music', 'Fitness', 'Art', 'Politics', 'Finance']
income_tiers = ['Low', 'Lower-Middle', 'Middle', 'Upper-Middle', 'High']

# Generate Reddit Profiles (JSON)
reddit_profiles = []
twitter_profiles = []

for i in range(1, 51):
    age = random.randint(18, 85)
    gender = random.choice(genders)
    mbti = random.choice(mbtis)
    country = random.choice(countries)
    profession = random.choice(professions)
    interests = random.sample(interests_pool, random.randint(2, 5))
    
    transit_accessibility = round(random.uniform(0.1, 1.0), 2)
    digital_literacy = round(random.uniform(0.1, 1.0), 2)
    mobility_score = round(random.uniform(0.1, 1.0), 2)
    caregiver_support = random.choice([True, False])
    income_tier = random.choice(income_tiers)
    
    name = f"Test_User_{i}"
    username = f"patient_{i}_mock"
    
    bio = f"I am a {age} year old {profession} from {country}. Participating in clinical simulation."
    persona = f"Mock patient with following traits: {gender}, {mbti}, {income_tier} income. Transit: {transit_accessibility}, Digital Literacy: {digital_literacy}, Mobility: {mobility_score}, Caregiver: {caregiver_support}."
    
    reddit_profiles.append({
        "user_id": i + 1000,
        "username": username + "_reddit",
        "name": name,
        "bio": bio,
        "persona": persona,
        "karma": random.randint(10, 5000),
        "created_at": (datetime.datetime.now() - datetime.timedelta(days=random.randint(10, 1000))).strftime("%Y-%m-%d"),
        "age": age,
        "gender": gender,
        "mbti": mbti,
        "country": country,
        "profession": profession,
        "interested_topics": interests,
        # Extended custom fields for clinical trials:
        "transit_accessibility": transit_accessibility,
        "digital_literacy": digital_literacy,
        "mobility_score": mobility_score,
        "caregiver_support": caregiver_support,
        "income_tier": income_tier
    })
    
    twitter_profiles.append({
        "user_id": i + 1000,
        "name": name,
        "username": username + "_twitter",
        "user_char": persona,
        "description": bio
    })

# Write Reddit JSON
with open('backend/uploads/simulations/new_test_data/reddit_profiles_mock.json', 'w', encoding='utf-8') as f:
    json.dump(reddit_profiles, f, ensure_ascii=False, indent=2)

# Write Twitter CSV
with open('backend/uploads/simulations/new_test_data/twitter_profiles_mock.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=["user_id", "name", "username", "user_char", "description"])
    writer.writeheader()
    for row in twitter_profiles:
        writer.writerow(row)

print("Generated new test data at backend/uploads/simulations/new_test_data/")
