# dashboard
## functions
```
msg_classify(msg)
```
- Doing word segmentation according to msg, and classify the category, store it in database
```
location_classify()
```
- if the user state is 2, then using this function to check the user location
## states
- 0: first user
- 1: user have seen
- 2: waiting to this user's location
