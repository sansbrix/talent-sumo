import instaloader, profile

# Get instance
L = instaloader.Instaloader()

# Optionally, login or load session
L.login("iamkarantalwar", "kataria@123")  

profile = instaloader.Profile.from_username(L.context,'diveej_s')

followers = profile.get_followers()

data = []

print("How many followers I have {}".format(followers.count))
for follower in followers: 
    data.append({
        "name": follower.full_name,
        "total_follower": follower.username
    })
    print(follower.full_name)