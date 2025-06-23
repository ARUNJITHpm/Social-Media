import requests
import time

print("🔄 Waiting for Ngrok to be ready...")
time.sleep(2)

# Replace with your current Ngrok URL
ngrok_url = "https://8617-2405-201-f009-31b5-b55c-ded9-16-8a44.ngrok-free.app"

print(f"✅ Ngrok URL Found: {ngrok_url}")

# Step 1: Create a post
print("\n📝 Creating a post...")
response = requests.post(f"{ngrok_url}/create_post", json={"message": "Hello !"})
post_result = response.json()
print("✅ Post Response:", post_result)

post_id = post_result.get('id')
if not post_id:
    print("❌ Failed to get post ID.")
    exit()

# Step 2: View post details
print("\n🔎 Viewing post details...")
details_response = requests.get(f"{ngrok_url}/post_details/{post_id}")
print("✅ Post Details:", details_response.json())

# Step 3: Comment on the post
print("\n💬 Commenting on the post...")
comment_response = requests.post(f"{ngrok_url}/comments/{post_id}", json={"message": "Hi!"})
comment_result = comment_response.json()
print("✅ Comment Response:", comment_result)

comment_id = comment_result.get('id')
if not comment_id:
    print("❌ Failed to get comment ID.")
    exit()

# Step 4: View comments
print("\n👀 Viewing comments on the post...")
comments_response = requests.get(f"{ngrok_url}/view_comments/{post_id}")
print("✅ Comments:", comments_response.json())

# Step 5: Reply to the comment
print("\n💬 Replying to the comment...")
reply_response = requests.post(f"{ngrok_url}/reply_comment/{comment_id}", json={"message": "Thank you for your comment!"})
print("✅ Reply Response:", reply_response.json())
