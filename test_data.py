import pybaseball as pb

# Search for a player (Let's use Aaron Judge)
data = pb.playerid_lookup('judge', 'aaron')
print("Connection Successful!")
print(data)